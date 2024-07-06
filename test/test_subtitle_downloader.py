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
    if None:
        @patch.object(MediaOperations, 'download_audio_and_transcribe')
        @patch('core.subtitle_downloader.MediaDownloader')
        @patch('core.subtitle_downloader.OperateDB')
        @patch('core.subtitle_downloader.find_files')
        @patch('core.subtitle_downloader.clean_subtitles')
        def test_download_single_subtitles_both(self, mock_clean_subtitles, mock_find_files, mock_operate_db, mock_downloader, mock_download_audio_and_transcribe):
            mock_downloader_instance = mock_downloader.return_value
            mock_downloader_instance.check_and_download_subtitles.return_value = {'state': 'Done'}
            mock_find_files.return_value = ['test_output/subtitles/test_video_id.vtt']
            mock_db_instance = mock_operate_db.return_value

            result = self.media_ops.download_single_subtitles('test_video_id', download_mode='both')

            mock_find_files.assert_called_once_with('test_output//subtitle', ['test_video_id', 'vtt'])
            mock_clean_subtitles.assert_called_once_with(file_path='test_output/subtitles/test_video_id.vtt', output_dir='test_output/adress_subtitles')
            mock_db_instance.update_value.assert_called_once_with('test_video_id', 'has_address_subtitles', 'Done')
            mock_db_instance.close.assert_called_once()

    
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
    

  