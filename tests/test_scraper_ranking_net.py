import unittest
from unittest.mock import patch, MagicMock
import json
from scraper_ranking_net import scrape_ranking_net

class TestScraperRankingNet(unittest.TestCase):
    @patch('scraper_ranking_net.requests.get')
    @patch('scraper_ranking_net.search_bing_images')
    def test_scrape_ranking_net(self, mock_bing, mock_get):
        """Ranking.netスクレイパーの基本機能とBing補強を確認"""
        sample_json = {
            "props": {
                "pageProps": {
                    "ranking": {
                        "items": [
                            {
                                "name": "テストアイドル",
                                "twitter_id": "test_idol"
                            }
                        ]
                    }
                }
            }
        }
        sample_html = f'<html><body><script id="__NEXT_DATA__" type="application/json">{json.dumps(sample_json)}</script></body></html>'
        
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.status_code = 200
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        mock_bing.return_value = ["https://bing.com/img1.jpg"]
        
        results = scrape_ranking_net(max_pages=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'テストアイドル')
        self.assertEqual(results[0]['id'], 'test_idol')
        self.assertIn('https://bing.com/img1.jpg', results[0]['images'])

if __name__ == '__main__':
    unittest.main()
