import argparse
from core.utils import fetch_youtube_playlist, fetch_existing_ids, classify_videos, save_videos_to_db, check_db_subtitles_info, db_change_value, SubtitleDownloader

def main():
    parser = argparse.ArgumentParser(description="Data Fetching Operations")
    parser.add_argument("--mode", choices=["fetch_youtube_playlist", "download_subtitle"], help="Select the mode of operation.")
    parser.add_argument("--channel_url", type=str, default='https://www.youtube.com/@benhsu501')

    args = parser.parse_args()

    if args.mode == 'fetch_youtube_playlist':
        channel_url = args.channel_url

        # 抓取 yt playlist
        videos_info = fetch_youtube_playlist(channel_url)
        
        # 查看抓下來的數據是否已經存在 db
        existing_ids = fetch_existing_ids('sql/yt_info.db')

        # 判斷哪些數據需要加入資料庫
        new_videos, existing_videos = classify_videos(videos_info, existing_ids)

        # 列印已存在的影片資料
        print("新的影片資料：")
        for video in new_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

        print("已存在的影片資料：")
        for video in existing_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

        save_videos_to_db(videos_info)

    if args.mode == "download_subtitle":
        
        video_ids = check_db_subtitles_info()
        downloader = SubtitleDownloader()
        #downloader.check_and_download_subtitles(['HjgerWSDoXE'], 0)       
        downloader.check_and_download_subtitles(video_ids, 0) 

if __name__ == "__main__":
    main()

## example check 
## yt-dlp --list-subs https://www.youtube.com/watch?v=HjgerWSDoXE

## example download 
## yt-dlp --write-sub  --sub-langs en --skip-download -o subtitles/%(id)s.%(ext)s https://www.youtube.com/watch?v=HjgerWSDoXE