import unittest, os
from unittest.mock import patch, mock_open, MagicMock
from core.subtitle_downloader import MediaOperations

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
#from core.utils import MediaDownloader, WhisperRecognizer  # Adjust the import as necessary


#class TestMediaOperations(unittest.TestCase):
class TestMediaOperations(unittest.TestCase):

    def setUp(self):
        self.media_ops = MediaOperations(channel_url='', output_dir='test_output/', download_mode='mp3')

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    @patch('core.subtitle_downloader.MediaDownloader')
    @patch('core.subtitle_downloader.WhisperRecognizer')
    def test_download_audio_and_transcribe(self, mock_whisper, mock_downloader):
        # 設置 mock
        mock_downloader_instance = mock_downloader.return_value
        mock_whisper_instance = mock_whisper.return_value
        mock_whisper_instance.transcribe_audio.return_value = "Mocked transcription"

        # 調用方法
        result = self.media_ops.download_audio_and_transcribe("OZmoqGIjWus")

        # 斷言
        mock_downloader_instance.download_audio.assert_called_once_with(video_id="OZmoqGIjWus", download_type='mp3')
        mock_whisper_instance.transcribe_audio.assert_called_once_with("OZmoqGIjWus")
        self.assertEqual(result, "Mocked transcription")

    @patch('core.subtitle_downloader.MediaDownloader')
    def test_download_single_subtitles(self):
        download_single_subtitles
        
'''
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    @patch('core.utils.MediaDownloader')
    @patch('core.utils.WhisperRecognizer')


    def test_download_audio_and_transcribe(self, mock_WhisperRecognizer, mock_MediaDownloader):
        # Setup
        mock_downloader_instance = mock_MediaDownloader.return_value
        mock_downloader_instance.download_audio.return_value = None  # Mock the return value of download_audio

        mock_recognizer_instance = mock_WhisperRecognizer.return_value
        mock_recognizer_instance.transcribe_audio.return_value = "This is a test transcription."

        media_ops = MediaOperations()

        # Action
        result = media_ops.download_audio_and_transcribe("OZmoqGIjWus")

        # Assert
        mock_downloader_instance.download_audio.assert_called_once_with(video_id="OZmoqGIjWus", download_type='mp3')
        mock_recognizer_instance.transcribe_audio.assert_called_once_with("test_video_id")
        self.assertEqual(result, "This is a test transcription.")


class TestMediaOperations(unittest.TestCase):

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    #@patch('os.path.exists', return_value=True)
    #@patch('builtins.open', new_callable=mock_open, read_data="Mock audio data")
    #@patch('core.utils.WhisperRecognizer')
    @patch('core.utils.MediaDownloader')
    def test_download_audio_and_transcribe(self, MockMediaDownloader):
    #def test_download_audio_and_transcribe(self, MockMediaDownloader, MockWhisperRecognizer, mock_open, mock_exists):
        # Arrange
        video_id = 'OZmoqGIjWus'
        transcription_result = 'This is a test transcription.'

        # Mock MediaDownloader instance
        mock_downloader_instance = MockMediaDownloader.return_value
        mock_downloader_instance.download_audio.return_value = None  # download_audio doesn't return anything
        mock_downloader_instance.download_audio.side_effect = lambda *args, **kwargs: print("模拟的下载音频方法被调用")

        #breakpoint()
        # 打印以验证模拟对象
        print(f"MockMediaDownloader: {MockMediaDownloader}")
        print(f"mock_downloader_instance: {mock_downloader_instance}")
        # Mock WhisperRecognizer instance
        #mock_recognizer_instance = MockWhisperRecognizer.return_value
        #mock_recognizer_instance.transcribe_audio.return_value = transcription_result

        # Act
        

        media_operations = MediaOperations()
        result = media_operations.download_audio_and_transcribe(video_id)
        print(result)

        # Assert
        #mock_downloader_instance.download_audio.assert_called_once_with(video_id=video_id, download_type='mp3')
        #mock_recognizer_instance.transcribe_audio.assert_called_once_with(video_id)
        #self.assertEqual(result, transcription_result)


class TestMediaOperations(unittest.TestCase):
    def setUp(self):
        self.client = MediaOperations(channel_url="", output_dir="test/output/", download_mode='mp3')

 
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    @patch('core.utils.WhisperRecognizer')
    def test_download_audio_and_transcribe(self, MockWhisperRecognizer, MockMediaDownloader):
        # Arrange
        video_id = 'OZmoqGIjWus'
        transcription_result = 'This is a test transcription.'
        #MockWhisperRecognizer.return_value = transcription_result

        # Mock the WhisperRecognizer instance
        #mock_recognizer_instance = MockWhisperRecognizer.return_value
        #mock_recognizer_instance.transcribe_audio.return_value = transcription_result
         # Mock the WhisperRecognizer instance
        mock_recognizer_instance = MockWhisperRecognizer.return_value
        mock_recognizer_instance.transcribe_audio.return_value = transcription_result

   # Mock the MediaDownloader instance
        mock_downloader_instance = MockMediaDownloader.return_value
        mock_downloader_instance.download_audio.return_value = None  # download_audio doesn't return anything

        # Mock the WhisperRecognizer instance
        mock_recognizer_instance = MockWhisperRecognizer.return_value
        mock_recognizer_instance.transcribe_audio.return_value = transcription_result

        # Act
        media_operations = MediaOperations()
        result = media_operations.download_audio_and_transcribe(video_id)
        print(result)

        # Assert
        #mock_downloader.download_audio.assert_called_once_with(video_id=video_id, download_type='mp3')
        #mock_recognizer.transcribe_audio.assert_called_once()
        #self.assertEqual(result, transcription_result)


    """
    @patch('core.utils.MediaDownloader.check_and_download_subtitles')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_api_key"})
    def test_download_single_subtitles(self, mock_check_and_download_subtitles):
        mock_check_and_download_subtitles.return_value = {'state': 'NotFound'}

        result = self.client.download_single_subtitles('test_video_id')

        #self.assertEqual(, expected_files)
        

    @patch('core.subtitle_downloader.WhisperRecognizer.transcribe_audio')
    @patch('core.subtitle_downloader.MediaDownloader.downlaod_audio')
    def test_download_audio_and_transcribe(self):
        expected = 1
        client = MediaOperations(channel_url = "", output_dir = "test/output/", download_mode = 'mp3')
        result = client.download_audio_and_transcribe('GBg-DZwgGkA')
        print()

        self.assertEqual(result, expected)
    """
    # expected = self.config['test_get_system']
    # https://youtube.com/shorts/GBg-DZwgGkA
    '''