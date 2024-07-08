import argparse
from core.utils import fetch_youtube_playlist, classify_videos, clean_subtitles, find_files
from core.utils import  OperateDB
from openai import OpenAI
from CopyCraftAPI.utils import GetAPIMessage
from core.subtitle_downloader import MediaOperations
import os

def step_generate_article(args):
    input_path_sub = args.output_path + '/adress_subtitles'
    input_path_tra = args.output_path + '/transcriptions'
    response_content_list = {}
    for id in args.video_id:
        #breakpoint()
        use_file = find_files(input_path_tra, id)
        use_file = use_file if len(use_file) == 1 else  find_files(input_path_sub, id)
        message = GetAPIMessage(path=use_file[0], article_type='blog', role='Angel investor')
        message = message.combine_messages()
        
        client = OpenAI()
        response = client.chat.completions.create(model=args.model, messages=message, max_tokens=args.max_tokens)
        response_content_list[id] = response.choices[0].message.content
        
    return response_content_list

def save_articles(result, output_path, video_ids):
    directory = os.path.join(output_path, 'article')
    if not os.path.exists(directory):
        os.makedirs(directory)

    for _id in video_ids:
        output_path = directory + _id + '.txt'
        with open(output_path, 'w') as file:
            file.write(f"{_id}: {result[_id]}\n")
            print(f'Save the article to {output_path}')

def handle_fetch_video_id(args):
    videos_info = fetch_youtube_playlist(args.channel_url)
    db = OperateDB()
    existing_ids = db.fetch_existing_ids()
    new_videos, existing_videos = classify_videos(videos_info, existing_ids)

    print("New video data:")
    for video in new_videos:
        print(f"ID: {video['id']}, Author: {video['playlist_uploader_id']}, Title: {video.get('title', 'No Title')}")
    print("Existing video data:")
    for video in existing_videos:
        print(f"ID: {video['id']}, Author: {video['playlist_uploader_id']}, Title: {video.get('title', 'No Title')}")

    db.save_new_yt_info(new_videos)
    db.close()


def handle_download_subtitle(args, video_ids):
    client = MediaOperations(channel_url=args.channel_url, 
                             output_dir=args.output_path, 
                             download_mode=args.subtitle_source)
    client.download_subtitles(video_ids)


def main():
    parser = argparse.ArgumentParser(description="Data Fetching Operations")
    parser.add_argument("--mode", default='full_process',  
                    choices=["full_process", "fetch_video_id", 'download_subtitle', 'generate_article', 'test'], 
                    help="Select the mode of operation. The mode 'full_process' runs through all three stages: fetch_video_id, download_subtitle, and generate_article. The other three modes execute each stage individually.")
    parser.add_argument("--download_mode", choices=['video_id', 'playlist'], type=str, default='video_id', help = '')
    parser.add_argument("--subtitle_source", choices=['mp3', 'subtitle', 'both'], type=str, default='mp3',
        help="Specify the source of subtitles. 'mp3': Subtitles are generated from the Whisper-extracted MP3 file. 'subtitle': Subtitles are fetched from YouTube. 'both': If YouTube does not provide subtitles, generate them from the MP3 file.")
    parser.add_argument("--channel_url", type=str, default='https://www.youtube.com/@benhsu501')
    parser.add_argument("--output_path", type=str, default='output/')
    parser.add_argument("--video_id", type=str, nargs='+', help="One or more video IDs", default=None)
    # chatGPT API para
    parser.add_argument("--model", type=str, default = 'gpt-3.5-turbo', choices=['gpt-3.5-turbo', 'gpt-4o'], help='Set the model for the chatGPT API. Default is gpt-3.5-turbo.')
    parser.add_argument("--max_tokens", type=int, default=2000, help="set the max tokens for the chatGPT API.")
    args = parser.parse_args()

    if args.mode == "fetch_video_id":
        handle_fetch_video_id(args)
        
    if args.mode == "download_subtitle":
        db = OperateDB()
        if args.download_mode == 'video_id':
            handle_download_subtitle(args, args.video_id)
        if args.download_mode == 'playlist':
            video_ids = db.get_video_ids(conditions={'has_subtitles': 'Done', 'has_address_subtitles': 'No'})
            handle_download_subtitle(args, list(video_ids))
        db.close()

    if args.mode == 'generate_article':
        if not args.video_id:
            raise  ValueError('Please input video_id by --video_id.')
        result = step_generate_article(args)
        save_articles(result, args.output_path, args.video_id)

    if args.mode == "full_process":
        if args.download_mode == "playlist":
            print('The full_process mode with --download_mode video_id playlist isn\'t working yet. Please use --download_mode mp3 instead.')

        if args.download_mode == 'video_id':
            if not args.video_id:
                raise  ValueError('Please input video_id by --video_id.')
            handle_download_subtitle(args, args.video_id)
            result = step_generate_article(args)
            save_articles(result, args.output_path, args.video_id)

if __name__ == "__main__":
    main()

## example check 
## yt-dlp --list-subs https://www.youtube.com/watch?v=HjgerWSDoXE

## example download 
## yt-dlp --write-sub  --sub-langs en --skip-download -o subtitles/%(id)s.%(ext)s https://www.youtube.com/watch?v=HjgerWSDoXE
