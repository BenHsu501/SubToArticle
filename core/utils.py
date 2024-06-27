import sqlite3
import json
import subprocess
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
import re
import os


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
            has_address_subtitles TEXT DEFAULT 'No',
            has_generated_article TEXT DEFAULT 'No',
            has_uploaded_article TEXT DEFAULT 'No'
        );
        ''')

        for video in videos_info:
            c.execute('''
            INSERT OR REPLACE INTO videos (id, title, url, description, duration, view_count, webpage_url, webpage_url_domain, extractor,
                                playlist_title, playlist_id, playlist_uploader, playlist_uploader_id, n_entries, duration_string, upload_date,
                                has_subtitles, has_address_subtitles, has_generated_article, has_uploaded_article)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                'No',
                'No',  # has_generated_article
                'No'   # has_uploaded_article
            ))
        self.conn.commit()

    def get_video_ids(self, conditions: dict = {'has_subtitles': 'No'}) -> Set[str]:
        '''
        Example:
            conditions = {'has_subtitles': 'No', 'has_uploaded_article': 'No'}
            video_ids = db.get_video_ids(conditions)
        '''
        if not conditions:
            raise ValueError("No conditions provided for the query.")
        
        # 准备查询条件和参数
        query_conditions = " AND ".join([f"{col} = ?" for col in conditions])
        parameters = tuple(conditions.values())

        # 构建并执行 SQL 查询
        sql_query = f"SELECT id FROM videos WHERE {query_conditions}"
        self.cursor.execute(sql_query, parameters)
        waiting_download_ids = {row[0] for row in self.cursor.fetchall()}
        return waiting_download_ids
    
    def update_value(self, id: str, col_name: str, value: str) -> None:
        try:
            # Prepare the SQL statement
            sql = f"UPDATE videos SET {col_name} = ? WHERE id = ?"
            # Execute the SQL statement
            self.cursor.execute(sql, (value, id))
            # Commit the changes
            self.conn.commit()
            print(f'Column "{col_name}" updated to "{value}" successfully.')
            "The \"has_subtitles\" col in the DB was updated successfully to \"Done\"."
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
        for video_id in video_ids:
            # check subtilte
            manual_subs, subtitle_type = self.check_subtitle_available(video_id, mode)
            print(video_id, manual_subs, subtitle_type)
            # select_subtitle_lang
            download_lang = None
            if not manual_subs is None:
                download_lang = self.select_subtitle_lang(manual_subs)
            
            # 字幕下載
            if download_lang:
                download_result = self.downlaod_audio(download_lang = download_lang, video_id = video_id, subtitle_type = subtitle_type)
                if download_result.returncode == 0:
                    self.write_log(video_id, f"{download_lang} subtitles downloaded successfully.\n")
                    db.update_value(video_id, 'has_subtitles', 'Done')
                    # print('has_subtitles', 'Done')
                    return {'state': 'Done'}
                else:
                    self.write_log(video_id, "An error occurred while downloading subtitles.\n")
                    db.update_value(video_id, 'has_subtitles', 'Error')
                    # print('has_subtitles', 'Error')
                    return {'state': 'Error'}

                db.update_value(video_id, 'type_subtitle', subtitle_type)
            else:
                self.write_log(video_id, "No suitable subtitles were found.\n")
                db.update_value(video_id, 'has_subtitles', 'NotFound')
                # print('has_subtitles', 'NotFound')
                return {'state': 'NotFound'}

        db.close()


    def select_subtitle_lang(self, subtitles:List[str]):
        download_lang = None
        # 依據優先序選擇下載語言
        for lang in self.priority_langs:

            if any(lang == sub for sub in subtitles):
                download_lang = lang
                break
        # 如果有除了 priority 的語言，就使用第一個
        if download_lang is None and len(subtitles) > 0: 
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
        
        # check subtitle exits.
        if 'vtt' in list_result.stdout:
            list_result_split_by_subtitletype = list_result.stdout.split("[info] Available subtitles for")
            if '[info] Available subtitles for' in list_result.stdout:
                _split = list_result_split_by_subtitletype[1].split('\n')
                manual_subs = [index.split(' ')[0] for index in _split if 'vtt' in index]

                if len(manual_subs) > 0:
                    # 有可能仍沒有字幕
                    return manual_subs, 'manual'
            if '[info] Available automatic captions' in list_result.stdout:
                _split = list_result_split_by_subtitletype[0].split('\n')
                automatic_subs = [index.split(' ')[0] for index in _split if 'vtt' in index]
                # automatic_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', 
                #                             list_result_split_by_subtitletype[0], re.MULTILINE)
                if len(automatic_subs) > 1:
                    # 有可能仍沒有字幕
                    return automatic_subs, 'auto'
            ValueError("Check another situation.")    
        else:
            return None, None
        #print('aaa', list_result.stdout.split('\n'))
        
        '''
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
            # manual_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[0], re.MULTILINE)

            print('aaa', manual_subs)
            return manual_subs, 'manual'
        '''


    def downlaod_audio(self, download_lang:str, video_id:str, subtitle_type:int = 'manual', type:str = 'subtitle'):

        if type == 'subtitle':
            sub_command = '--write-sub' if subtitle_type == 'manual' else '--write-auto-sub'
            download_command = [
                'yt-dlp',
                sub_command,  # 使用手动或自动字幕下载指令
                '--sub-langs', download_lang,  # 指定下载语言
                '--skip-download',  # 只下载字幕，不下载视频
                '-o', f'{self.output_dir}/%(id)s.%(ext)s',
                f'https://www.youtube.com/watch?v={video_id}'
            ]
        if type == 'mp3':
            download_command = [
                'yt-dlp',
                '-x',  # Extract audio only
                '--audio-format', 'mp3',  # Specify audio format as mp3
                '-o', f'{self.output_dir}/%(id)s.%(ext)s',
                f'https://www.youtube.com/watch?v={video_id}'
            ]

        download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Write download results to log file
        self.write_log(video_id, f"Download {type} Output:\n{download_result.stdout}\nDownload {type} Errors:\n{download_result.stderr}")
        return download_result

    def write_log(self, video_id:str, message:str) -> None:
        with open(f'output/subtitles/{video_id}_logs.txt', 'a') as log_file:
            log_file.write(message)


def clean_subtitles(file_path:str, output_dir:str = 'output/adress_subtitles') -> None:
    # 用于匹配时间线和WEBVTT的标头
    time_stamp_regex = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*")
    tag_regex = re.compile(r"<\d{2}:\d{2}:\d{2}\.\d{3}><c>.*?</c>")

    # 读取字幕文件
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 清洗数据
    cleaned_lines = []
    for line in lines:
        if not time_stamp_regex.match(line) and not line.startswith('WEBVTT') and line.strip():
            # 移除字幕中的标签
            line = re.sub(tag_regex, '', line)
            cleaned_lines.append(line.strip())

    # 将处理后的文本合并为一个字符串
    cleaned_text = ' '.join(cleaned_lines)


    filename = os.path.basename(file_path)
    new_filename = filename.rsplit('.', 1)[0] + '.txt'

    # 写入到新的文件中
    filename = os.path.join(output_dir, new_filename)

    ensure_directory_exists(filename)
    with open(filename, 'w', encoding='utf-8') as output_file:
        output_file.write(cleaned_text)

    print("字幕已清洗完毕并保存到, ", filename)


def find_files(directory: str, search_texts: List[str]) -> List[str]:
    # Check if the directory exists
    if not os.path.exists(directory):
        print("The directory does not exist.")
        return []

    # Search for files that contain all specified search_texts
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if all(search_text in filename for search_text in search_texts):
                matching_files.append(os.path.join(root, filename))
    
    return matching_files

def ensure_directory_exists(filename):
    # 获取文件的目录路径
    directory = os.path.dirname(filename)
    
    # 如果目录不存在，创建它
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)  # exist_ok=True 防止在目录已存在时抛出异常

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
