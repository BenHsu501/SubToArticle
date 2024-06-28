import argparse
from core.utils import fetch_youtube_playlist, classify_videos, clean_subtitles, find_files
from core.utils import  MediaDownloader, OperateDB
import os 

def main():
    parser = argparse.ArgumentParser(description="Data Fetching Operations")
    parser.add_argument("--mode", choices=["fetch_youtube_playlist", "download_subtitle", 'download_single_subtitle', 'test'], help="Select the mode of operation.")
    parser.add_argument("--channel_url", type=str, default='https://www.youtube.com/@benhsu501')
    parser.add_argument("--output_path", type=str, default='output/')
    parser.add_argument("--video_id", type=str, default='output/')
    parser.add_argument("--download_mode", choices=['mp3', 'subtitle', 'both'], type=str, default='both', help = 'mp3: Subtitle comes from the Whisper-extracted MP3 file. subtitle: Subtitle comes from YouTube. both: When YouTube does not provide a subtitle, use the MP3 mode.')

    # parser.add_argument("--max_download_num", type=int, default=100)

    args = parser.parse_args()

    if args.mode == 'fetch_youtube_playlist':
        channel_url = args.channel_url

        # 抓取 yt playlist
        videos_info = fetch_youtube_playlist(channel_url)
        
        # 查看抓下來的數據是否已經存在 db
        db = OperateDB()
        existing_ids = db.fetch_existing_ids()
        # 判斷哪些數據需要加入資料庫
        new_videos, existing_videos = classify_videos(videos_info, existing_ids)

        # 列印已存在的影片資料
        print("新的影片資料：")
        for video in new_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

        print("已存在的影片資料：")
        for video in existing_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

        db.save_new_yt_info(new_videos)
        db.close()

    if args.mode == "download_playlist_subtitle":
        
        db = OperateDB()
        video_ids = db.get_video_ids()
        downloader = MediaDownloader()
        #downloader.check_and_download_subtitles(['HjgerWSDoXE'], 0)       
        downloader.check_and_download_subtitles(video_ids, 0)

        # video_ids = db.get_video_id(has_address_subtitles, )
        video_ids = db.get_video_ids({'has_subtitles': 'Done', 'has_address_subtitles': 'No'})
        for video_id in list(video_ids):
            print('1', video_id)
            input_path = 'output/subtitles' 
            output_path = 'output/adress_subtitles'
            downloader = MediaDownloader()
            matched_files = find_files(input_path, [video_id, 'vtt'])
            print('2', matched_files)
            clean_subtitles(file_path = matched_files[0],
                            output_dir = output_path)

        db.close()
    
    if args.mode == "download_single_subtitle":
        video_id = args.video_id

        downloader = MediaDownloader()
        state_result = None

        if args.download_mode in ['subtitle', 'both']:
            state_result = downloader.check_and_download_subtitles([video_id], 0)
            if args.download_mode == 'both':
                if state_result['state'] == 'NotFound':
                    downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')

        if args.download_mode == 'mp3':
            downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')



        input_path = 'output/subtitles' 
        output_path = 'output/adress_subtitles'
        matched_files = find_files(input_path, [video_id, 'vtt'])
        # 下面寫 db 的寫入

    if args.mode == 'create_article':
        import CopyCraftAPI.utils as CopyCraftAPI

    if args.mode == 'test':
        # ownloader = MediaDownloader()
        # downloader.check_and_download_subtitles(['OZmoqGIjWus'], 0)
        # id = 'GBg-DZwgGkA'
        # id = 'JXUnrgp_8WI'
        # downloader.check_and_download_subtitles([id], 0)

        from openai import OpenAI
        client = OpenAI()

        audio_file= open("output/mp3/ScVRy6PxT_A.mp3", "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        print(transcription.text)   

if __name__ == "__main__":
    main()

## example check 
## yt-dlp --list-subs https://www.youtube.com/watch?v=HjgerWSDoXE

## example download 
## yt-dlp --write-sub  --sub-langs en --skip-download -o subtitles/%(id)s.%(ext)s https://www.youtube.com/watch?v=HjgerWSDoXE