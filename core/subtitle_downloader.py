from core.utils import  OperateDB, MediaDownloader, WhisperRecognizer

class MediaOperations:
    def __init__(self, channel_url: str, output_dir: str = 'output/', mode: str = ''):
        self.channel_url = channel_url
        self.output_dir = output_dir

    def download_single_subtitles(self, video_id:str, download_mode:str = 'mp3'):
        downloader = MediaDownloader()
        state_result = None

        if download_mode in ['subtitle', 'both']:
            state_result = downloader.check_and_download_subtitles(video_id, 0)
            
            if download_mode == 'both' and state_result['state'] in ['NotFound' in 'Error']:
                downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')
                client = WhisperRecognizer()
                result = client.transcribe_audio(video_id)
        if download_mode == 'mp3':
            downloader.downlaod_audio(video_id = video_id, download_type = 'mp3')
            client = WhisperRecognizer()
            # recognizer and save result
            result = client.transcribe_audio(video_id)

    def download_subtitles(self, ):
        1
