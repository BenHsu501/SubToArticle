from core.utils import  OperateDB, MediaDownloader, WhisperRecognizer
from typing import List
from core.utils import find_files, clean_subtitles

class MediaOperations:
    def __init__(self, channel_url: str = '', output_dir: str = 'output/', download_mode: str = 'mp3'):
        self.channel_url = channel_url
        self.output_dir = output_dir
        self.download_mode = download_mode

    def download_audio_and_transcribe(self, video_id: str):
        
        downloader = MediaDownloader()
        downloader.download_audio(video_id=video_id, download_type='mp3')
        #breakpoint()
        client = WhisperRecognizer()
        result = client.transcribe_audio(video_id)
        return result

    def download_single_subtitles(self, video_id:str, download_mode:str = None):
        downloader = MediaDownloader()
        state_result = None
        result = None
        if download_mode in ['subtitle', 'both']:
            state_result = downloader.check_and_download_subtitles(video_id, 0)
            print('Subtitle mode:', video_id, state_result['state'])
            if state_result['state'] == 'Done':
                input_path = self.output_dir + '/subtitles' 
                output_path = self.output_dir + '/adress_subtitles'
                matched_files = find_files(input_path, [video_id, 'vtt'])
                clean_subtitles(file_path = matched_files[0],
                                 output_dir = output_path)
                db = OperateDB()
                db.update_value(video_id, 'has_address_subtitles', 'Done')
                db.close()
            
            if download_mode == 'both' and state_result['state'] in ['NotFound', 'Error']:
                result = self.download_audio_and_transcribe(video_id)

        if download_mode == 'mp3':
            result = self.download_audio_and_transcribe(video_id)
        
        return result if result else None
    
    def download_subtitles(self, video_ids:List):
        if not isinstance(video_ids, list):
            video_ids = [video_ids]
        for video_id in video_ids:
            self.download_single_subtitles(video_id, self.download_mode)


