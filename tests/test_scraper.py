import unittest
from unittest.mock import patch, MagicMock
from scraper import scrape_bi_girl_page

class TestScraper(unittest.TestCase):
    @patch('requests.get')
    def test_scrape_bi_girl_page(self, mock_get):
        """一覧ページから情報を正しく抽出できるかテスト（実際のHTML構造に合わせたセレクタ）"""
        sample_html = """
        <div class="img_wrapper_inner">
            <div class="all_tweet_profile_wrap">
                <div class="all_tweet_profile_right">
                    <div class="all_tweet_profile_name">日暮りん</div>
                    <div class="all_tweet_profile_screenName">@higurashirin</div>
                </div>
            </div>
            <a href="https://x.com/higurashirin/status/123456789">ポスト</a>
        </div>
        <div class="img_wrapper_inner">
            <div class="all_tweet_profile_wrap">
                <div class="all_tweet_profile_right">
                    <div class="all_tweet_profile_name">テスト美女</div>
                    <div class="all_tweet_profile_screenName">@test_girl</div>
                </div>
            </div>
            <a href="https://x.com/test_girl/status/987654321">ポスト</a>
        </div>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = scrape_bi_girl_page(2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], '日暮りん')
        self.assertEqual(results[0]['id'], 'higurashirin')
        self.assertEqual(results[0]['url'], 'https://x.com/higurashirin/status/123456789')

        self.assertEqual(results[1]['name'], 'テスト美女')
        self.assertEqual(results[1]['id'], 'test_girl')
        self.assertEqual(results[1]['url'], 'https://x.com/test_girl/status/987654321')

if __name__ == '__main__':
    unittest.main()
