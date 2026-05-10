import unittest
from unittest.mock import patch, MagicMock
from scraper_aru18 import scrape_aru18_top100

class TestScraperAru18(unittest.TestCase):
    @patch('scraper_aru18.requests.get')
    @patch('scraper_aru18.search_bing_images')
    def test_scrape_aru18_top100(self, mock_bing, mock_get):
        """Aru18スクレイパーの基本機能とBing補強を確認"""
        sample_html = """
        <html><body>
        <div class="actress-item">
            <div class="name">テスト女優</div>
            <a href="https://twitter.com/intent/follow?screen_name=test_actress">フォロー</a>
        </div>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.status_code = 200
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        mock_bing.return_value = ["https://bing.com/img1.jpg"]
        
        items = scrape_aru18_top100()
        
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0]['name'], 'テスト女優')
        self.assertEqual(items[0]['id'], 'test_actress')
        self.assertIn('https://bing.com/img1.jpg', items[0]['images'])

if __name__ == '__main__':
    unittest.main()
