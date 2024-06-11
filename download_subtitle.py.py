import subprocess
import re
from typing import List
from datetime import datetime

class SubtitleDownloader:
    def __inti__(self, output_dir:str = 'subtitles', priority_langs:List[str] = ['en', 'zh-TW', 'zh', 'es']) -> None:
        self.output_dir = output_dir
        self.priority_langs = priority_langs
        now_tinme = '{:%y%m%d_%H%M%S%}'.format(datetime.now())
        self.log_path = f'{self.output_dir}/{now_tinme}_yt_dlp_logs.txt'

    def check_and_download_subtitles(self, video_ids):
        for video_id in video_ids:
            manual_subs = self.check_subtitle_available(video_id)

            download_lang = None
            if len(manual_subs) > 0:
                for lang in self.priority_langs:
                    if any(lang == sub[0] for sub in manual_subs):
                        download_lang = lang
                        break
                # 如果有除了 priority 的語言
                if download_lang is None: 
                    download_lang = manual_subs[0]

            if download_lang:


            for lag in self.priority_langs:
                if 
            subtitle_lag_list
            use_lag = 

    def select_subtitle_lag():
        1
    
    def check_subtitle_available(self, video_id:str):
        list_command = [
            'yt-dlp',
            '--list-subs',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        list_result = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # writing log
        log_message = f"Checking subtitles for video ID {video_id}\nList Subtitles Output:\n{list_result.stdout}\nList Subtitles Errors:\n{list_result.stderr}\n"
        self.write_log(log_message)
        if list_result.returncode != 0:
            self.write_log(f"Error listing subtitles for video ID {video_id}\n")
            return
        
         # Regex to find available subtitles
        list_result_split_by_subtitletype = list_result.stdout.split("[info] Available subtitles for")
        manual_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[1], re.MULTILINE)
        return manual_subs

    def downlaod_subtitle(self, download_lang:str, video_id:str):
        download_command = [
            'yt-dlp',
            '--write-sub',
            '--sub-langs', download_lang,  # Specify the chosen language for download
            '--skip-download',   # Only download subtitles, not the video
            '-o', f'{self.output_dir}/%(id)s.%(ext)s',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Write download results to log file
        log_file.write("Download Subtitles Output:\n")
        log_file.write(download_result.stdout)
        log_file.write("\nDownload Subtitles Errors:\n")
        log_file.write(download_result.stderr)

        if download_result.returncode == 0:
            log_file.write(f"{download_lang} subtitles downloaded successfully.\n")
        else:
            log_file.write("An error occurred while downloading subtitles.\n")
    else:
        log_file.write("No suitable subtitles were found.\n")
    
    def write_log(video_id:str, message:str) -> None:
        with open(f'subtitles/{video_id}_logs.txt', 'a') as log_file:
            log_file.write(message)

def check_and_download_subtitles(video_ids:List[str], output_dir:str ='subtitles', priority_langs:List = ['en', 'zh-TW', 'zh', 'es']) -> None:
    '''
    確認指定 youtube 影片是否有字幕，並依據優先序下載
    並將執行結果存入 db 進行紀錄
    '''
    if not isinstance(video_ids, list):
        return "The input video_list must be List."
    for video_id in video_ids:
        list_command = [
            'yt-dlp',
            '--list-subs',
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        list_result = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        with open(f'subtitles/yt_dlp_logs_{video_id}.txt', 'a') as log_file:
            log_file.write(f"Checking subtitles for video ID {video_id}\n")
            log_file.write("List Subtitles Output:\n")
            log_file.write(list_result.stdout)
            log_file.write("\nList Subtitles Errors:\n")
            log_file.write(list_result.stderr)
        
            if list_result.returncode != 0:
                log_file.write(f"Error listing subtitles for video ID {video_id}\n")
                return
            list_result_split_by_subtitletype = list_result.stdout.split("[info] Available subtitles for")
            
        
            # Regex to find available subtitles
            # auto_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[0], re.MULTILINE)
            manual_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result_split_by_subtitletype[1], re.MULTILINE)

            print('˙777', list_result_split_by_subtitletype[1])
            print('Manual subtitles:', manual_subs)
            
            # Priority order for subtitles
            priority_langs = ['en', 'zh-TW', 'zh', 'es']  # Example priority: English, Chinese, Spanish
            download_lang = None
            if len(manual_subs) > 0:
                for lang in priority_langs:
                    if any(lang == sub[0] for sub in manual_subs):
                        download_lang = lang
                        break
                if download_lang is None:
                    download_lang = manual_subs[0]
                        
            if download_lang:
                # Download the chosen subtitle language
                download_command = [
                    'yt-dlp',
                    '--write-sub',
                    '--sub-langs', download_lang,  # Specify the chosen language for download
                    '--skip-download',   # Only download subtitles, not the video
                    '-o', f'{output_dir}/%(id)s.%(ext)s',
                    f'https://www.youtube.com/watch?v={video_id}'
                ]

                download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Write download results to log file
                log_file.write("Download Subtitles Output:\n")
                log_file.write(download_result.stdout)
                log_file.write("\nDownload Subtitles Errors:\n")
                log_file.write(download_result.stderr)

                if download_result.returncode == 0:
                    log_file.write(f"{download_lang} subtitles downloaded successfully.\n")
                else:
                    log_file.write("An error occurred while downloading subtitles.\n")
            else:
                log_file.write("No suitable subtitles were found.\n")
        
# Example usage
#check_and_download_subtitles("dQw4w9WgXcQ")  # Replace with a valid YouTube video ID

# 使用函數
# check_and_download_subtitles('VIDEO_ID_HERE')
# 使用函數
check_and_download_subtitles('g0RWoZnOANM')

import subprocess
import re

class SubtitleDownloader:
    def __init__(self, output_dir='subtitles', priority_langs=None):
        self.output_dir = output_dir
        self.priority_langs = priority_langs if priority_langs else ['en', 'zh-TW', 'zh', 'es']
        self.log_path = f'{self.output_dir}/yt_dlp_logs.txt'

    def check_and_download_subtitles(self, video_ids):
        for video_id in video_ids:
            self.check_subtitles(video_id)

    def check_subtitles(self, video_id):
        list_command = ['yt-dlp', '--list-subs', f'https://www.youtube.com/watch?v={video_id}']
        list_result = subprocess.run(list_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        with open(self.log_path, 'a') as log_file:
            log_file.write(f"Checking subtitles for video ID {video_id}\n")
            self.process_list_result(video_id, list_result, log_file)

    def process_list_result(self, video_id, list_result, log_file):
        if list_result.returncode != 0:
            log_file.write(f"Error listing subtitles for video ID {video_id}\n")
            return
        manual_subs = re.findall(r'^([a-zA-Z-]{2,10})\s+.*?\s+vtt', list_result.stdout, re.MULTILINE)
        self.download_subtitle(video_id, manual_subs, log_file)

    def download_subtitle(self, video_id, subtitles, log_file):
        download_lang = next((lang for lang in self.priority_langs if lang in subtitles), None)
        if download_lang:
            download_command = ['yt-dlp', '--write-sub', '--sub-langs', download_lang, '--skip-download', '-o', f'{self.output_dir}/%(id)s.%(ext)s', f'https://www.youtube.com/watch?v={video_id}']
            download_result = subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.log_download_result(download_result, download_lang, log_file)
        else:
            log_file.write("No suitable subtitles were found.\n")

    def log_download_result(self, download_result, download_lang, log_file):
        if download_result.returncode == 0:
            log_file.write(f"{download_lang} subtitles downloaded successfully.\n")
        else:
            log_file.write("An error occurred while downloading subtitles.\n")

# 使用
downloader = SubtitleDownloader()
downloader.check_and_download_subtitles(['g0RWoZnOANM'])
