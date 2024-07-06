import argparse
from core.utils import fetch_youtube_playlist, classify_videos, clean_subtitles, find_files
from core.utils import  MediaDownloader, OperateDB, WhisperRecognizer
from core.subtitle_downloader import MediaOperations
from openai import OpenAI
import CopyCraftAPI.utils as CopyCraftAPI

def main():

    from core.subtitle_downloader import MediaOperations

    parser = argparse.ArgumentParser(description="Data Fetching Operations")
    
    parser.add_argument("--mode", default='full_process',  
                    choices=["full_process", "fetch_video_id", 'download_subtitle', 'generate_article', 'test'], 
                    help="Select the mode of operation. The mode 'full_process' runs through all three stages: fetch_video_id, download_subtitle, and generate_article. The other three modes execute each stage individually.")
    parser.add_argument("--download_mode", choices=['video_id', 'playlist'], type=str, default='video_id', help = '')
    parser.add_argument("--subtitle_source", choices=['mp3', 'subtitle', 'both'], type=str, default='mp3',
        help="Specify the source of subtitles. 'mp3': Subtitles are generated from the Whisper-extracted MP3 file. 'subtitle': Subtitles are fetched from YouTube. 'both': If YouTube does not provide subtitles, generate them from the MP3 file.")

    parser.add_argument("--channel_url", type=str, default='https://www.youtube.com/@benhsu501')
    parser.add_argument("--output_path", type=str, default='output/')
    parser.add_argument("--video_id", type=str, nargs='+', help="One or more video IDs")

    args = parser.parse_args()

    if args.mode == "fetch_video_id":
        videos_info = fetch_youtube_playlist(args.channel_url)
        db = OperateDB()
        existing_ids = db.fetch_existing_ids()
        new_videos, existing_videos = classify_videos(videos_info, existing_ids)

        print("新的影片資料：")
        for video in new_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")
        print("已存在的影片資料：")
        for video in existing_videos:
            print(f"ID: {video['id']}, 作者: {video['playlist_uploader_id']}, 標題: {video.get('title', '無標題')}")

        db.save_new_yt_info(new_videos)
        db.close()
        

    if args.mode == "download_subtitle" and args.download_mode == 'video_id':
        from core.subtitle_downloader import MediaOperations
        client = MediaOperations(channel_url=args.channel_url, 
                                 output_dir=args.output_path, 
                                 download_mode=args.subtitle_source)
        client.download_subtitles(args.video_id)
    
    if args.mode == "download_subtitle" and args.download_mode == 'playlist':
        db = OperateDB()
        #breakpoint()
        # video_ids = db.get_video_ids(conditions = {'has_subtitles': 'Done', 'has_address_subtitles': 'No'})
        video_ids = db.get_video_ids(conditions = {'has_subtitles': 'Done', 'has_address_subtitles': 'No'})
        from core.subtitle_downloader import MediaOperations
        client = MediaOperations(channel_url=args.channel_url, 
                                 output_dir=args.output_path, 
                                 download_mode=args.subtitle_source)
        #breakpoint()
        client.download_subtitles(list(video_ids))
        
        
    
    if args.mode == "test":
        client = MediaOperations(download_mode='subtitle')
        # breakpoint()
        client.download_subtitles('cPdVWtRFDqw')
        db = OperateDB()


    if args.mode == "download_playlist_subtitle":
        
        db = OperateDB()
        video_ids = db.get_video_ids()
        downloader = MediaDownloader()
        #downloader.check_and_download_subtitles(['HjgerWSDoXE'], 0)       
        downloader.check_and_download_subtitles(video_ids, 0)

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
            state_result = downloader.check_and_download_subtitles(video_id, 0)
                
            if args.download_mode == 'both' and state_result['state'] == 'NotFound':
                downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')
                client = WhisperRecognizer()
                result = client.transcribe_audio(video_id)
                print(result)   
        if args.download_mode == 'mp3':
            downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')
            client = WhisperRecognizer()
            result = client.transcribe_audio(video_id)
            print(result)   


        input_path = 'output/subtitles' 
        output_path = 'output/adress_subtitles'
        matched_files = find_files(input_path, [video_id, 'vtt'])
        # 下面寫 db 的寫入

    if args.mode == 'create_article':
        1
    if args.mode == 'test2':
        print(args.video_id)
        test = MediaOperations("")
        #test.download_single_subtitles("test_id", download_mode = 'subtitle')
        test.download_audio_and_transcribe('OZmoqGIjWus')
        
        # ownloader = MediaDownloader()
        # downloader.check_and_download_subtitles(['OZmoqGIjWus'], 0)
        # id = 'GBg-DZwgGkA'
        # id = 'JXUnrgp_8WI'
        # downloader.check_and_download_subtitles([id], 0)

        #client = OpenAI()

        #audio_file= open("output/mp3/ScVRy6PxT_A.mp3", "rb")
        #transcription = client.audio.transcriptions.create(
        #    model="whisper-1", 
        #    file=audio_file
        #)
     #print(transcription.text)   

if __name__ == "__main__":
    main()

## example check 
## yt-dlp --list-subs https://www.youtube.com/watch?v=HjgerWSDoXE

## example download 
## yt-dlp --write-sub  --sub-langs en --skip-download -o subtitles/%(id)s.%(ext)s https://www.youtube.com/watch?v=HjgerWSDoXE
