import core
import unittest
from core.utils import fetch_youtube_playlist, OperateDB
from unittest.mock import patch

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
