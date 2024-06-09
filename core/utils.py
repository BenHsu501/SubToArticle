import sqlite3
import json
import subprocess
from typing import List, Dict, Any, Set, Tuple

def fetch_youtube_videos(playlist_url: str) -> List[Dict[str, Any]]:
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
        >>> fetch_youtube_videos("https://www.youtube.com/@benhsu501")
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

def fetch_existing_ids(db_path='sql/yt_info.db') -> Set[str]:
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



def save_videos_to_db(videos_info, db_path='yt_info.db'):
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
                            playlist_title, playlist_id, playlist_uploader, playlist_uploader_id, n_entries, duration_string, upload_date
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
            video.get('upload_date', '')  # 確保有上传日期
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



# 示例用法
import csv
channel_url = 'https://www.youtube.com/@benhsu501'
channel_url = 'https://www.youtube.com/@bumpbro'
channel_url = 'https://www.youtube.com/@DanLok'
videos_info = fetch_youtube_videos(channel_url)
existing_ids = fetch_existing_ids('yt_info.db')
new_videos, existing_videos = classify_videos(videos_info, existing_ids)

print("新的影片資料：")
for video in new_videos:
    print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

# 列印已存在的影片資料：只列印 ID 和標題
print("已存在的影片資料：")
for video in existing_videos:
    print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")


#print(videos_info)
# save_videos_to_csv(videos_info, csv_path = "/dir/test/yt_videos.csv")
# 使用新函式保存到 CSV
save_videos_to_db(videos_info)
