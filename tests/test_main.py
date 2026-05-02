import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os

class TestMainLogic(unittest.TestCase):
    def setUp(self):
        self.mock_items = [
            {
                "name": f"Girl {i}", 
                "id": f"id_{i}", 
                "url": f"https://x.com/id_{i}/status/1",
                "image_url": f"https://bi-girl.net/img/{i}.jpg"
            }
            for i in range(1, 10)
        ]

    def test_process_posts_batch_limit(self):
        """1回の実行で5件までに制限されているかテスト"""
        # モックの設定
        with patch('os.getenv') as mock_getenv, \
             patch('os.path.exists') as mock_exists, \
             patch('livedoor_client.LivedoorClient') as mock_client_class, \
             patch('main.scrape_bi_girl_page') as mock_scrape:
            
            mock_getenv.side_effect = lambda k, default=None: {
                "LIVEDOOR_ID": "test_user",
                "LIVEDOOR_API_KEY": "test_key",
                "LIVEDOOR_BLOG_ID": "test_blog",
                "LIVEDOOR_CATEGORY": "美女図鑑"
            }.get(k, default)
            
            mock_exists.return_value = True
            mock_scrape.return_value = self.mock_items
            
            # mock_open の設定
            m = mock_open(read_data='{"current_page": 2000}')
            m.side_effect = [
                mock_open(read_data='{"current_page": 2000}').return_value, # state read
                mock_open(read_data='').return_value,                       # history read
                mock_open().return_value,                                   # history write
                mock_open().return_value,                                   # state write
                mock_open().return_value,                                   # fallback
                mock_open().return_value                                    # fallback
            ]

            with patch('builtins.open', m):
                mock_client = mock_client_class.return_value
                from main import process_posts
                process_posts(dry_run=False)

            # 5件投稿されたか
            self.assertEqual(mock_client.post_article.call_count, 5)
            # 最後の投稿内容をチェック
            args, kwargs = mock_client.post_article.call_args
            content = args[1]
            self.assertIn('<img src="https://bi-girl.net/img/5.jpg"', content)
            self.assertEqual(kwargs['category'], "美女図鑑")

if __name__ == '__main__':
    unittest.main()
