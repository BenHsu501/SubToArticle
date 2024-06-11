import sqlite3
import json
import subprocess
from typing import List, Dict, Any, Set, Tuple

def fetch_youtube_playlist(playlist_url: str) -> List[Dict[str, Any]]:
    """
    Fetches a list of videos from a YouTube playlist using the `yt-dlp` tool.

    This function calls the `yt-dlp` command-line program to retrieve information
    about each video in a YouTube playlist specified by the URL. The function
    parses the JSON output from `yt-dlp` and returns a list of video details.

    Args:
        playlist_url (str): The full URL to the YouTube user's playlist or channel,
                            e.g., "https://www.youtube.com/@benhsu501".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains
                              details of a video. Possible keys include 'title', 'url',
                              'duration', etc.

    Raises:
        subprocess.CalledProcessError: If `yt-dlp` fails to run.
        json.JSONDecodeError: If parsing JSON fails.

    Example:
        >>> fetch_youtube_playlist("https://www.youtube.com/@benhsu501")
        [{'title': 'Example Video', 'url': 'https://youtube.com/example', ...}, ...]

    """
    command = [
        'yt-dlp',
        '-o', '%(title)s.%(ext)s',
        '--flat-playlist',
        '--dump-json',
        playlist_url
    ]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    videos_info = []
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            try:
                video_data = json.loads(line)
                videos_info.append(video_data)
            except json.JSONDecodeError:
                print("Error decoding JSON from line:", line)
    return videos_info

def fetch_existing_ids(db_path: str = 'sql/yt_info.db') -> Set[str]:
    """
    Retrieves a set of existing video IDs from the database.

    This function queries the SQLite database at the specified path for all video
    IDs stored in the 'videos' table. It returns these IDs in a set, which can be
    used to check for existing videos and prevent duplicate entries.

    Args:
        db_path (str): The file path to the SQLite database. Default is 'yt_info.db'.

    Returns:
        Set[str]: A set containing the video IDs already stored in the database.

    Example:
        >>> existing_ids = fetch_existing_ids('yt_info.db')
        >>> print(existing_ids)
        {'video1', 'video2', 'video3'}
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM videos")
    existing_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return existing_ids

def classify_videos(new_videos: List[Dict[str, Any]], existing_ids: Set[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Classifies videos into new or existing based on their IDs.

    This function takes a list of video dictionaries and a set of existing video IDs,
    and separates the videos into two lists: one for videos whose IDs are already in
    the database, and another for those that are new and not present in the database.

    Args:
        new_videos (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                           contains details of a video.
        existing_ids (Set[str]): A set of video IDs that have been previously stored in the database.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: A tuple containing two lists:
            - The first list contains dictionaries of videos that are already in the database.
            - The second list contains dictionaries of new videos that are not in the database.

    Example:
        >>> new_videos = [{'id': 'video4', 'title': 'New Video 4'}, {'id': 'video1', 'title': 'Existing Video 1'}]
        >>> existing_ids = {'video1', 'video2', 'video3'}
        >>> new_data, existing_data = classify_videos(new_videos, existing_ids)
        >>> print(new_data)
        [{'id': 'video4', 'title': 'New Video 4'}]
        >>> print(existing_data)
        [{'id': 'video1', 'title': 'Existing Video 1'}]
    """
    
    new_data = []
    existing_data = []
    for video in new_videos:
        if video['id'] in existing_ids:
            existing_data.append(video)
        else:
            new_data.append(video)
    return new_data, existing_data



def save_videos_to_db(videos_info, db_path='sql/yt_info.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT,
        description TEXT,
        duration INTEGER,
        view_count INTEGER,
        webpage_url TEXT,
        webpage_url_domain TEXT,
        extractor TEXT,
        playlist_title TEXT,
        playlist_id TEXT,
        playlist_uploader TEXT,
        playlist_uploader_id TEXT,
        n_entries INTEGER,
        duration_string TEXT,
        upload_date TEXT,
        has_subtitles TEXT DEFAULT 'No',
        has_generated_article TEXT DEFAULT 'No',
        has_uploaded_article TEXT DEFAULT 'No'
    );
    ''')

    for video in videos_info:
        c.execute('''
        INSERT OR REPLACE INTO videos (id, title, url, description, duration, view_count, webpage_url, webpage_url_domain, extractor,
                            playlist_title, playlist_id, playlist_uploader, playlist_uploader_id, n_entries, duration_string, upload_date,
                            has_subtitles, has_generated_article, has_uploaded_article)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video['id'],
            video.get('title', ''),
            video.get('url', ''),
            video.get('description', ''),
            video.get('duration', None),
            video.get('view_count', None),
            video.get('webpage_url', ''),
            video.get('webpage_url_domain', ''),
            video.get('extractor', ''),
            video.get('playlist_title', ''),
            video.get('playlist_id', ''),
            video.get('playlist_uploader', ''),
            video.get('playlist_uploader_id', ''),
            video.get('n_entries', None),
            video.get('duration_string', ''),
            video.get('upload_date', ''),  # 確保有上传日期
            'No',  # has_subtitles
            'No',  # has_generated_article
            'No'   # has_uploaded_article
        ))

    conn.commit()
    conn.close()


def save_videos_to_csv(videos_info, csv_path='yt_videos.csv'):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = ['id', 'title', 'url', 'description', 'duration', 'view_count', 'webpage_url', 'webpage_url_domain',
                   'extractor', 'playlist_title', 'playlist_id', 'playlist_uploader', 'playlist_uploader_id', 'n_entries', 'duration_string', 'upload_date']
        writer.writerow(headers)
        for video in videos_info:
            row = [
                video['id'],
                video.get('title', ''),
                video.get('url', ''),
                video.get('description', ''),
                video.get('duration', None),
                video.get('view_count', None),
                video.get('webpage_url', ''),
                video.get('webpage_url_domain', ''),
                video.get('extractor', ''),
                video.get('playlist_title', ''),
                video.get('playlist_id', ''),
                video.get('playlist_uploader', ''),
                video.get('playlist_uploader_id', ''),
                video.get('n_entries', None),
                video.get('duration_string', ''),
                video.get('upload_date', ''),
                'No',  # has_subtitles
                'No',  # has_generated_article
                'No'   # has_uploaded_article
            ]
            writer.writerow(row)


    

def check_db_subtitles_info(db_path: str = 'sql/yt_info.db') -> Set[str]:
    """
    
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM videos WHERE has_subtitles='No'")
    waitting_downlaod_ids = {row[0] for row in cursor.fetchall()}

    conn.close()
                   
    return waitting_downlaod_ids


def check_and_download_subtitles(video_ids: Set[str], output_dir:str ='subtitles', log_path='yt_dlp_logs.txt'):
    # 檢查可用的字幕
    if len(video_ids) == 0:
        return "All subtitles of videos have been downloaded."

    for video_id in video_ids:
        list_command = [
            'yt-dlp',
            '--list-subs',
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        # 執行命令並獲取輸出
        list_result = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 檢查輸出中是否包含 'en'（代表英語字幕）
        if 'en (auto-generated)' in list_result.stdout or 'en' in list_result.stdout:
            # 下載英語字幕
            download_command = [
                'yt-dlp',
                '--write-sub',
                '--sub-langs', 'en',  # 指定下載英語字幕
                '--skip-download',   # 只下載字幕，不下載影片
                '-o', f'{output_dir}/%(ㄎㄛ).%(ext)s',
                f'https://www.youtube.com/watch?v={video_id}'
            ]

            # 執行下載命令
            download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(video_id, "")
                # 寫入下載結果到日誌文件

            if download_result.returncode == 0:
                #log_file.write("英語字幕下載成功\n")
                # db_change_value(id = video_id, col_name = 'has_subtitles', value = 'Yes')
                print(video_id, "英語字幕下載成功\n")
            else:
                # db_change_value(id = video_id, col_name = 'has_subtitles', value = 'Error')
                print(video_id, "英語字幕下載失敗\n")
        else:
            # db_change_value(id = video_id, col_name = 'has_subtitles', value = 'No_en')
            print(video_id, "該影片沒有可用的英語字幕")



import sqlite3

def db_change_value(id: str, col_name: str, value: str, db_path: str = 'sql/yt_info.db'):
    """
    Changes a specific value in the database for a given video ID.

    This function updates a specific column for a single row in the SQLite database,
    identified by the video ID. It allows for dynamically setting the column and value.

    Args:
        id (str): The ID of the video whose data needs to be updated.
        col_name (str): The name of the column in the database to update.
        value (str): The new value to set in the specified column.
        db_path (str): The path to the SQLite database file. Defaults to 'sql/yt_info.db'.

    Raises:
        ValueError: If the column name provided does not exist in the database.
        sqlite3.Error: If an error occurs during the database operation.

    Example:
        >>> db_change_value('video123', 'title', 'New Video Title')
        # This will update the 'title' column for the video with ID 'video123' to 'New Video Title'.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Prepare the SQL statement
        sql = f"UPDATE videos SET {col_name} = ? WHERE id = ?"
        # Execute the SQL statement
        cursor.execute(sql, (value, id))
        # Commit the changes
        conn.commit()
        print("Database updated successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        # Ensure that the connection is closed
        conn.close()


# 示例用法
#import csv
#channel_url = 'https://www.youtube.com/@benhsu501'
#channel_url = 'https://www.youtube.com/@bumpbro'
#channel_url = 'https://www.youtube.com/@DanLok'
#videos_info = fetch_youtube_playlist(channel_url)
#existing_ids = fetch_existing_ids('yt_info.db')
#new_videos, existing_videos = classify_videos(videos_info, existing_ids)

# print("新的影片資料：")
# for video in new_videos:
#     print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

## 列印已存在的影片資料：只列印 ID 和標題
# print("已存在的影片資料：")
# for video in existing_videos:
#     print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")


# print(videos_info)
# save_videos_to_csv(videos_info, csv_path = "/dir/test/yt_videos.csv")
# 使用新函式保存到 CSV
# save_videos_to_db(videos_info)
