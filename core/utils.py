import sqlite3
import json
import subprocess
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
import re

def fetch_youtube_playlist(playlist_url: str) -> List[Dict[str, Any]]:
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

class OperateDB:
    def __init__(self, db_path:str = 'output/yt_info.db'): 
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def fetch_existing_ids(self)  -> Set[str]:
        self.cursor.execute("SELECT id FROM videos")
        existing_ids = {row[0] for row in self.cursor.fetchall()}
        return existing_ids
    
    def save_new_yt_info(self, videos_info):
        c = self.cursor

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
        self.conn.commit()

    def check_no_subtitle_videos(self) -> Set[str]:
        self.cursor.execute("SELECT id FROM videos WHERE has_subtitles='No'")
        waitting_downlaod_ids = {row[0] for row in self.cursor.fetchall()}
        return waitting_downlaod_ids 
    
    def update_value(self, id: str, col_name: str, value: str) -> None:
        try:
            # Prepare the SQL statement
            sql = f"UPDATE videos SET {col_name} = ? WHERE id = ?"
            # Execute the SQL statement
            self.cursor.execute(sql, (value, id))
            # Commit the changes
            self.conn.commit()
            print("Database updated successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def close(self):
        self.cursor.close()
        self.conn.close()                     

def classify_videos(new_videos: List[Dict[str, Any]], existing_ids: Set[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    new_data = []
    existing_data = []
    for video in new_videos:
        if video['id'] in existing_ids:
            existing_data.append(video)
        else:
            new_data.append(video)
    return new_data, existing_data

class SubtitleDownloader:
    def __init__(self, output_dir:str = 'output/subtitles', priority_langs:List[str] = ['en', 'zh-TW', 'zh', 'es']) -> None:
        self.output_dir = output_dir
        self.priority_langs = priority_langs

        now_tinme = '{:%y%m%d_%H%M%S%}'.format(datetime.now())
        self.log_path = f'{self.output_dir}/{now_tinme}_yt_dlp_logs.txt'

    def check_and_download_subtitles(self, video_ids:List[str], mode:int) -> None:
        db = OperateDB()
        # 依據每一個函數使用
        for video_id in video_ids:
            # check subtilte
            print(video_id, self.check_subtitle_available(video_id, mode))
            manual_subs, subtitle_type = self.check_subtitle_available(video_id, mode)
            # select_subtitle_lag
            download_lang = None
            if not manual_subs is None:
                download_lang = self.select_subtitle_lag(manual_subs)
            
            # 字幕下載
            if download_lang:
                download_result = self.downlaod_subtitle(download_lang = download_lang, video_id = video_id, subtitle_type = subtitle_type)
                if download_result.returncode == 0:
                    self.write_log(video_id, f"{download_lang} subtitles downloaded successfully.\n")
                    db.update_value(video_id, 'has_subtitles', 'Done')
                else:
                    self.write_log(video_id, "An error occurred while downloading subtitles.\n")
                    db.update_value(video_id, 'has_subtitles', 'Error')

            else:
                self.write_log(video_id, "No suitable subtitles were found.\n")
                db.update_value(video_id, 'has_subtitles', 'NotFound')



    def select_subtitle_lag(self, subtitles:List[str]):
        download_lang = None
        # 依據優先序選擇下載語言
        for lang in self.priority_langs:

            if any(lang == sub for sub in subtitles):
                download_lang = lang
                break
        # 如果有除了 priority 的語言，就使用第一個
        if download_lang is None: 
            print(subtitles[0])
            download_lang = subtitles[0]    
        return download_lang

    def check_subtitle_available(self, video_id:str, mode:int) -> None | str:
        list_command = [
            'yt-dlp',
            '--list-subs',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        list_result = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # writing log
        log_message = f"Checking subtitles for video ID {video_id}\nList Subtitles Output:\n{list_result.stdout}\nList Subtitles Errors:\n{list_result.stderr}\n"
        self.write_log(video_id, log_message)
        if list_result.returncode != 0:
            self.write_log(video_id, f"Error listing subtitles for video ID {video_id}\n")
            return None, None
        
         # Regex to find available subtitles
        list_result_split_by_subtitletype = list_result.stdout.split("[info] Available subtitles for")
        if 'has no subtitles' in list_result_split_by_subtitletype[0]:
            self.write_log(video_id, f" has no subtitles\n")
            if mode == 0:
                auto_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[0], re.MULTILINE)
                if len(auto_subs) != 0:              
                    return auto_subs, 'auto'
                else:
                    return None, 'auto'
        else:
            manual_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[1], re.MULTILINE)
            return manual_subs, 'manual'

    def downlaod_subtitle(self, download_lang:str, video_id:str, subtitle_type:int = 'manual'):
        sub_command = '--write-sub' if subtitle_type == 'manual' else '--write-auto-sub'
        download_command = [
            'yt-dlp',
            sub_command,  # 使用手动或自动字幕下载指令
            '--sub-langs', download_lang,  # 指定下载语言
            '--skip-download',  # 只下载字幕，不下载视频
            '-o', f'{self.output_dir}/%(id)s.%(ext)s',
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Write download results to log file
        self.write_log(video_id, "Download Subtitles Output:\n{download_result.stdout}\nDownload Subtitles Errors:\n{download_result.stderr}")
        return download_result
        
    def write_log(self, video_id:str, message:str) -> None:
        with open(f'subtitles/{video_id}_logs.txt', 'a') as log_file:
            log_file.write(message)

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
