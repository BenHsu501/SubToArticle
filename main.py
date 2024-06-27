import argparse
from core.utils import fetch_youtube_playlist, classify_videos, clean_subtitles, find_files
from core.utils import  SubtitleDownloader, OperateDB
import os 

def main():
    parser = argparse.ArgumentParser(description="Data Fetching Operations")
    parser.add_argument("--mode", choices=["fetch_youtube_playlist", "download_subtitle", 'download_video_subtitle', 'test'], help="Select the mode of operation.")
    parser.add_argument("--channel_url", type=str, default='https://www.youtube.com/@benhsu501')
    parser.add_argument("--output_path", type=str, default='output/')
    parser.add_argument("--video_id", type=str, default='output/')

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
        downloader = SubtitleDownloader()
        #downloader.check_and_download_subtitles(['HjgerWSDoXE'], 0)       
        downloader.check_and_download_subtitles(video_ids, 0)

        # video_ids = db.get_video_id(has_address_subtitles, )
        video_ids = db.get_video_ids({'has_subtitles': 'Done', 'has_address_subtitles': 'No'})
        for video_id in list(video_ids):
            print('1', video_id)
            input_path = 'output/subtitles' 
            output_path = 'output/adress_subtitles'
            downloader = SubtitleDownloader()
            matched_files = find_files(input_path, [video_id, 'vtt'])
            print('2', matched_files)
            clean_subtitles(file_path = matched_files[0],
                            output_dir = output_path)

        db.close()
    
    if args.mode == "download_video_subtitle":
        video_id = args.video_id

        downloader = SubtitleDownloader()
        state_result = downloader.check_and_download_subtitles([video_id], 0)
        if state_result == 'Error' and 1: # here need to add a logic which judge download mp3 file
            downloader.check_and_download_subtitles([video_id], 0)
        print(1, state_result)
        input_path = 'output/subtitles' 
        output_path = 'output/adress_subtitles'
        matched_files = find_files(input_path, [video_id, 'vtt'])
        print('2', matched_files)
        # 下面寫 db 的寫入

    if args.mode == 'create_article':
        import CopyCraftAPI.utils as CopyCraftAPI

    if args.mode == 'test':
        downloader = SubtitleDownloader()
        # downloader.check_and_download_subtitles(['OZmoqGIjWus'], 0)
        id = 'GBg-DZwgGkA'
        id = 'JXUnrgp_8WI'
        downloader.check_and_download_subtitles([id], 0)



if __name__ == "__main__":
    main()

## example check 
## yt-dlp --list-subs https://www.youtube.com/watch?v=HjgerWSDoXE

## example download 
## yt-dlp --write-sub  --sub-langs en --skip-download -o subtitles/%(id)s.%(ext)s https://www.youtube.com/watch?v=HjgerWSDoXE