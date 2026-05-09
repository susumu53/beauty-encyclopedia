import unittest
from unittest.mock import patch, MagicMock
from scraper import scrape_bi_girl_page

class TestScraper(unittest.TestCase):
    @patch('requests.get')
    def test_scrape_bi_girl_page(self, mock_get):
        """一覧ページから情報を正しく抽出できるかテスト（複数画像対応）"""
        sample_html = """
        <div class="img_wrapper_inner">
            <div class="img_frame">
                <a class="img_a img_all">
                    <img data-src="https://bi-girl.net/main1.jpg" />
                    <img src="https://bi-girl.net/main2.jpg" />
                </a>
            </div>
            <div class="all_tweet_profile_name">日暮りん</div>
            <div class="all_tweet_profile_screenName">@higurashirin</div>
            <a href="https://x.com/higurashirin/status/123456789">ポスト</a>
        </div>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = scrape_bi_girl_page(2)

        self.assertEqual(len(results), 1)
        # image_url ではなく images リストを期待
        self.assertIn('https://bi-girl.net/main1.jpg', results[0]['images'])
        self.assertIn('https://bi-girl.net/main2.jpg', results[0]['images'])
        self.assertEqual(len(results[0]['images']), 2)

if __name__ == '__main__':
    unittest.main()
