import unittest
from unittest.mock import patch, MagicMock
from dmm_client import DMMClient

class TestDMMClient(unittest.TestCase):
    def setUp(self):
        self.client = DMMClient(api_id="test_api_id", affiliate_id="test_affiliate_id")

    @patch('requests.get')
    def test_search_dmm_com(self, mock_get):
        """DMM.com（一般）からアイテムを取得できるかテスト"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "status": 200,
                "items": [
                    {
                        "title": "テスト作品",
                        "affiliateURL": "https://al.dmm.com/test",
                        "imageURL": {"large": "https://pics.dmm.com/test_l.jpg"}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        items = self.client.search_items("テスト美女", site="DMM.com")
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], "テスト作品")
        self.assertEqual(items[0]['url'], "https://al.dmm.com/test")
        self.assertEqual(items[0]['image'], "https://pics.dmm.com/test_l.jpg")
        
    @patch('requests.get')
    def test_search_all(self, mock_get):
        """DMM.com と FANZA の両方から取得してマージできるかテスト"""
        # 1回目は DMM.com、2回目は FANZA のレスポンスを返すように設定
        mock_get.side_effect = [
            MagicMock(json=lambda: {"result": {"status": 200, "items": [{"title": "一般作品", "affiliateURL": "url1", "imageURL": {"large": "img1"}}]}}),
            MagicMock(json=lambda: {"result": {"status": 200, "items": [{"title": "成人向け作品", "affiliateURL": "url2", "imageURL": {"large": "img2"}}]}})
        ]

        items = self.client.search_all("テスト美女")
        
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['title'], "一般作品")
        self.assertEqual(items[1]['title'], "成人向け作品")
        self.assertEqual(mock_get.call_count, 2)

if __name__ == '__main__':
    unittest.main()
