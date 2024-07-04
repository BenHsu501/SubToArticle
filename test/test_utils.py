import unittest
from core.utils import fetch_youtube_playlist, OperateDB, classify_videos, MediaDownloader, WhisperRecognizer
from unittest.mock import patch
import sqlite3
from unittest.mock import MagicMock

# coverage run --source=core.utils -m unittest discover -s test
# coverage report
# coverage html
# python3 -m http.server --directory ./htmlcov        

class TestFetchYoutubePlaylist(unittest.TestCase):

    # @patch('subprocess.run')
    def test_fetch_youtube_playlist_positive(self):
        # mock_subprocess_run.return_value.stdout = '["{"title": "Resume Writing Tips for Students and Career Changers: Building a Structure to Guide Interviewers", "url": "https://www.youtube.com/watch?v=g0RWoZnOANM"}", "{"title": "數據分析轉職 | 是否要唸碩士? | 規劃年薪百萬的方法 ", "url": "https://www.youtube.com/watch?v=cPdVWtRFDqw"}"]'
        
        playlist_url = 'https://www.youtube.com/@BenHsu501'
        result = fetch_youtube_playlist(playlist_url)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['title'], 'Resume Writing Tips for Students and Career Changers: Building a Structure to Guide Interviewers')
        self.assertEqual(result[0]['url'], 'https://www.youtube.com/watch?v=g0RWoZnOANM')
        self.assertEqual(result[1]['title'], '數據分析轉職 | 是否要唸碩士? | 規劃年薪百萬的方法')
        self.assertEqual(result[1]['url'], 'https://www.youtube.com/watch?v=cPdVWtRFDqw')

    @patch('subprocess.run')
    def test_fetch_youtube_playlist_negative(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = '{'  # Simulate empty output
        
        playlist_url = 'https://www.youtube.com/playlist'
        result = fetch_youtube_playlist(playlist_url)
        self.assertEqual(result, [])  # Ensure empty list is returned for negative case


class TestOperateDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = OperateDB(':memory:')
        self.create_and_populate_table()
    
    def create_and_populate_table(self):
        c = self.db.conn.cursor()
        c.execute('DROP TABLE IF EXISTS videos')  # Drop the table if it exists
        c.execute('''
            CREATE TABLE videos (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                description TEXT,
                duration INTEGER,
                view_count INTEGER,
                webpage_url TEXT,
                webpage_url_domain TEXT,
                extractor TEXT,
                playlist_title TEXT,
                playlist_id TEXT,
                playlist_uploader TEXT,
                playlist_uploader_id TEXT,
                n_entries INTEGER,
                duration_string TEXT,
                upload_date TEXT,
                has_subtitles TEXT DEFAULT 'No',
                type_subtitle TEXT DEFAULT 'No',
                has_address_subtitles TEXT DEFAULT 'No',
                has_generated_article TEXT DEFAULT 'No',
                has_uploaded_article TEXT DEFAULT 'No'
            );
        ''')
        video = ("test_video_id", "Test Video", "http://youtube.com/test", "Test description", 100, 150, "http://youtube.com/test", "youtube.com", "youtube", "Test Playlist", "TPL", "Test Uploader", "TU1", 1, "10:00", "20220101", "No", "No", "No", "No", "No")
        c.execute('''
        INSERT OR REPLACE INTO videos (id, title, url, description, duration, view_count, webpage_url, webpage_url_domain, extractor, playlist_title, playlist_id, playlist_uploader, playlist_uploader_id, n_entries, duration_string, upload_date, has_subtitles, type_subtitle, has_address_subtitles, has_generated_article, has_uploaded_article)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', video)
        self.db.conn.commit()

    def tearDown(self):
        self.db.conn.close()
    
    def test_fetch_existing_ids(self):
        # Positive test case
        existing_ids = self.db.fetch_existing_ids()
        print(existing_ids)
        self.assertIsInstance(existing_ids, set)

        # Negative test case - Simulate empty database
        self.db.cursor.execute("DROP TABLE IF EXISTS videos")
        existing_ids = self.db.fetch_existing_ids()
        self.assertEqual(len(existing_ids), 0)

    def test_fetch_existing_ids_other_operational_error(self):
        # 创建一个 MagicMock 对象来模拟 cursor
        mock_cursor = MagicMock()
        # 配置 mock_cursor 在 execute 调用时抛出 sqlite3.OperationalError 异常
        mock_cursor.execute.side_effect = sqlite3.OperationalError('some other error')

        # 使用 mock_cursor 替换 self.db.cursor
        self.db.cursor = mock_cursor

        with self.assertRaises(sqlite3.OperationalError):
            self.db.fetch_existing_ids()


    def test_save_new_yt_info(self):
        # Positive test case
        videos_info = [{'id': 'Test Video2',
            'title': 1,
            'url': 'http://test.com' ,
            'description': 'test',
            'duration': 1,
            'view_count': 1,
            'webpage_url': 'test',
            'webpage_url_domain': 'test',
            'extractor': 'test',
            'playlist_title': 'test',
            'playlist_id': 'test',
            'playlist_uploader': 'test',
            'playlist_uploader_id': 'test',
            'n_entries': 1,
            'duration_string': 'test',
            'upload_date': 'test',
            'has_subtitles': 'No',
            'type_subtitle': 'No',
            'has_address_subtitles': 'No',
            'has_generated_article': 'No',
            'has_uploaded_article': 'No'}]
        expected = {'test_video_id', 'Test Video2'}
        self.db.save_new_yt_info(videos_info)
        existing_ids = self.db.fetch_existing_ids()
        self.assertEqual(set(existing_ids), expected)

        # Negative test case - Duplicate video ID
        videos_info[0]['title'] = '2'
        self.db.save_new_yt_info(videos_info)
        c = self.db.conn.cursor()
        result = c.execute("SELECT title FROM videos WHERE id='Test Video2'")
        self.assertEqual('2', result.fetchone()[0])
    
    def test_get_video_ids(self):
        # Positive test case
        conditions = {'has_subtitles': 'No'}
        video_ids = self.db.get_video_ids(conditions)
        self.assertIsInstance(video_ids, set)

        # Negative test case - Invalid conditions
        with self.assertRaises(ValueError):
            self.db.get_video_ids({})
    
    def test_update_value(self):
        # Positive test case
        self.db.cursor.execute("INSERT INTO videos (id, has_subtitles) VALUES ('1', 'No')")
        self.db.update_value('1', 'has_subtitles', 'Yes')
        self.db.cursor.execute("SELECT has_subtitles FROM videos WHERE id = '1'")
        updated_value = self.db.cursor.fetchone()[0]
        self.assertEqual(updated_value, 'Yes')

        # Negative test case - Non-existent ID
        with self.assertRaises(sqlite3.Error):
            self.db.update_value('100', 'has_sutitles', 'Yes')
    def test_close(self):
        # Test the close method
        self.db.close()
        
        # Verify that the cursor and connection are closed
        with self.assertRaises(sqlite3.ProgrammingError):
            self.db.cursor.execute("SELECT 1")
        
        with self.assertRaises(sqlite3.ProgrammingError):
            self.db.conn.execute("SELECT 1")

class TestClassifyVideos(unittest.TestCase):

    def test_positive_case(self):
        new_videos = [{'id': '1', 'title': 'Video 1'}, {'id': '2', 'title': 'Video 2'}]
        existing_ids = {'2', '3'}
        new_data, existing_data = classify_videos(new_videos, existing_ids)
        self.assertEqual(new_data, [{'id': '1', 'title': 'Video 1'}])
        self.assertEqual(existing_data, [{'id': '2', 'title': 'Video 2'}])

    def test_negative_case(self):
        new_videos = [{'id': '3', 'title': 'Video 3'}, {'id': '4', 'title': 'Video 4'}]
        existing_ids = {'1', '2'}
        new_data, existing_data = classify_videos(new_videos, existing_ids)
        self.assertEqual(new_data, [{'id': '3', 'title': 'Video 3'}, {'id': '4', 'title': 'Video 4'}])
        self.assertEqual(existing_data, [])

    def test_empty_input(self):
        new_videos = []
        existing_ids = {'1', '2'}
        new_data, existing_data = classify_videos(new_videos, existing_ids)
        self.assertEqual(new_data, [])
        self.assertEqual(existing_data, [])

class TestMediaDownloader(unittest.TestCase):

    def test_select_subtitle_lang_positive(self):
        downloader = MediaDownloader()
        subtitles = ['en', 'zh-TW', 'es']
        result = downloader.select_subtitle_lang(subtitles)
        self.assertEqual(result, 'en')

    def test_select_subtitle_lang_negative(self):
        downloader = MediaDownloader()
        subtitles = ['fr', 'de', 'it']
        result = downloader.select_subtitle_lang(subtitles)
        self.assertEqual('fr', result)

    @patch('subprocess.run')
    def test_check_subtitle_available_case1(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result
        
        downloader = MediaDownloader()
        manual_subs, subtitle_type = downloader.check_subtitle_available('video_id', 1)
        
        self.assertEqual(manual_subs, None)
        self.assertEqual(subtitle_type, None)
    
    @patch('subprocess.run')
    def test_check_subtitle_available_case2(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.stdout = "[info] Available subtitles for cPdVWtRFDqw:\nLanguage      Name                                        Formats\nzh-TW                                                     vtt\nen                                                       vtt"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        downloader = MediaDownloader()
        manual_subs, subtitle_type = downloader.check_subtitle_available('video_id', 1)
        
        self.assertEqual(manual_subs, ['zh-TW', 'en'])
        self.assertEqual(subtitle_type, 'manual')

    @patch('subprocess.run')
    def test_check_subtitle_available_case3(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.stdout = "[info] Available automatic captions for oyvLXWEzcdM:\nLanguage               Name                                                          Formats\nen                     English, English, English, English, English, English, unknown vtt, ttml, srv3, srv2, srv1, json3, vtt"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        downloader = MediaDownloader()
        manual_subs, subtitle_type = downloader.check_subtitle_available('video_id', 1)
        self.assertEqual(manual_subs, ['en'])
        self.assertEqual(subtitle_type, 'auto')
    
    @patch('subprocess.run')
    def test_check_subtitle_available_case4(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.stdout = "vtt"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        downloader = MediaDownloader()
        with self.assertRaises(ValueError):
            downloader.check_subtitle_available('video_id', 1)

    @patch('subprocess.run')
    def test_check_subtitle_available_case5(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.stdout = "Checking subtitles for video ID GBg-DZwgGkA\nList Subtitles Output:[youtube] Extracting URL: https://www.youtube.com/watch?v=GBg-DZwgGkA\n[youtube] GBg-DZwgGkA: Downloading webpage\n[youtube] GBg-DZwgGkA: Downloading ios player API JSON\n[youtube] GBg-DZwgGkA: Downloading android player API JSON\n[youtube] GBg-DZwgGkA: Downloading m3u8 information\nGBg-DZwgGkA has no automatic captions\nGBg-DZwgGkA has no subtitles\n"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        downloader = MediaDownloader()
        manual_subs, subtitle_type = downloader.check_subtitle_available('video_id', 1)
        self.assertEqual(manual_subs, None)
        self.assertEqual(subtitle_type, None)

    @patch('subprocess.run')
    def test_download_audio_subtitle_positive(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 0
        downloader = MediaDownloader()
        result = downloader.download_audio('video_id', download_type='subtitle', download_lang='en', subtitle_type='manual')
        self.assertEqual(result.returncode, 0)

    @patch('subprocess.run')
    def test_download_audio_subtitle_negative(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 1
        downloader = MediaDownloader()
        result = downloader.download_audio('video_id', download_type='subtitle', download_lang='en', subtitle_type='manual')
        self.assertNotEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_download_audio_mp3_positive(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 0
        downloader = MediaDownloader()
        result = downloader.download_audio('video_id', download_type='mp3', download_lang='en', subtitle_type='manual')
        self.assertEqual(result.returncode, 0)

    @patch('subprocess.run')
    def test_download_audio_mp3_negative(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 1
        downloader = MediaDownloader()
        result = downloader.download_audio('video_id', download_type='mp3', download_lang='en', subtitle_type='manual')
        self.assertNotEqual(result.returncode, 0)

    @patch('core.utils.OperateDB')
    @patch('core.utils.MediaDownloader.download_audio')
    @patch('core.utils.MediaDownloader.select_subtitle_lang')
    @patch('core.utils.MediaDownloader.check_subtitle_available')
    def test_check_and_download_subtitles(self, mock_check_subtitle_available, mock_select_subtitle_lang, mock_download_audio, mock_operate_db):
        self.downloader = MediaDownloader()
        # Mock OperateDB instance
        mock_db_instance = MagicMock()
        mock_operate_db.return_value = mock_db_instance

        # Mock methods in MediaDownloader
        mock_check_subtitle_available.side_effect = [
            (['en'], 'manual'),
            (['en'], 'manual')
        ]
        mock_select_subtitle_lang.return_value = 'en'
        mock_download_audio.return_value = MagicMock(returncode=0)

        # Define the video IDs for the test
        video_ids = ['video1', 'video2']

        # Execute the method under test
        result = self.downloader.check_and_download_subtitles(video_ids, 1)
        # Assertions
        self.assertEqual(result, {'state': 'Done'})
        #mock_db_instance.close.assert_called_once()
        #mock_db_instance.close.reset_mock()  # Reset mock for the next test

        mock_download_audio.return_value = MagicMock(returncode=1)
        result = self.downloader.check_and_download_subtitles(video_ids, 1)
        self.assertEqual(result, {'state': 'Error'})
        #mock_db_instance.close.assert_called_once()
        #mock_db_instance.close.reset_mock()  # Reset mock for the next test

        mock_check_subtitle_available.side_effect = [
            (['en'], 'manual'),
            (['en'], 'manual')
        ]
        mock_select_subtitle_lang.return_value = None
        result = self.downloader.check_and_download_subtitles(video_ids, 1)
        self.assertEqual(result, {'state': 'NotFound'})
        #mock_db_instance.close.assert_called_once()
        #mock_db_instance.close.reset_mock()  # Reset mock for the next test

class TestWhisperRecognizer(unittest.TestCase):
    
    def test_transcribe_audio_positive(self):
        recognizer = WhisperRecognizer()
        recognizer.client.audio.transcriptions.create = MagicMock(return_value=MagicMock(text="This is a test transcription"))
        result = recognizer.transcribe_audio("test_video")
        self.assertEqual(result, "This is a test transcription")
        
    def test_transcribe_audio_file_not_found(self):
        recognizer = WhisperRecognizer()
        with self.assertRaises(FileNotFoundError):
            recognizer.transcribe_audio("non_existent_video")
    
    @patch("builtins.open")
    def test_save_transcription_positive(self, mock_open):
        recognizer = WhisperRecognizer()
        video_id = "test_video"
        text = "Test transcription text"
        recognizer.save_transcription(video_id, text)
        
        mock_open.assert_called_once_with(f"output/transcriptions/{video_id}.txt", "w", encoding="utf-8")
        
    @patch("builtins.open")
    def test_save_transcription_content(self, mock_open):
        recognizer = WhisperRecognizer()
        video_id = "test_video"
        text = "Test transcription text"
        recognizer.save_transcription(video_id, text)
        
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(text)

class TestCleanSubtitles(unittest.TestCase):

    def test_clean_subtitles(self):
        file_path = "test_subtitles.vtt"
        output_dir = "output/test"
        with patch('builtins.open', mock_open(read_data="00:00:01.000 --> 00:00:05.000\nHello <c>world</c>\n")) as mock_file:
            clean_subtitles(file_path, output_dir)
            mock_file.assert_called_with(file_path, 'r', encoding='utf-8')
            # Add assertions to check the cleaned subtitles file content and its correctness

    # Add more positive and negative test cases for clean_subtitles function

