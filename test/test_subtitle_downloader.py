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

    @patch.object(MediaOperations, 'download_audio_and_transcribe')
    @patch('core.subtitle_downloader.MediaDownloader')
    def test_download_single_subtitles_both(self, mock_downloader, mock_download_audio_and_transcribe):
        mock_downloader_instance = mock_downloader.return_value
        mock_downloader_instance.check_and_download_subtitles.return_value = {'state': 'NotFound'}
        mock_download_audio_and_transcribe.return_value = "Mocked transcription"
        result = self.media_ops.download_single_subtitles('test_video_id', download_mode = 'both')
        self.assertEqual(result, "Mocked transcription")

    @patch.object(MediaOperations, 'download_audio_and_transcribe')
    def test_download_single_subtitles_mp3(self, mock_download_audio_and_transcribe):
        mock_download_audio_and_transcribe.return_value = "Mocked transcription"
        result = self.media_ops.download_single_subtitles('test_video_id', download_mode = 'mp3')
        self.assertEqual(result, "Mocked transcription")

    @patch.object(MediaOperations, 'download_single_subtitles')
    def test_download_subtitles_single_video_id(self, mock_download_single_subtitles):
        video_id = 'test_video_id'
        self.media_ops.download_subtitles(video_id)
        
        mock_download_single_subtitles.assert_called_once_with(video_id, self.media_ops.download_mode)
