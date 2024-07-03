import core
import unittest
from core.utils import fetch_youtube_playlist, OperateDB
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
        self.db = OperateDB(':memory')
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