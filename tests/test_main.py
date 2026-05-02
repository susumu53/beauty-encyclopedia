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

    @patch('main.LivedoorClient')
    @patch('main.scrape_bi_girl_page')
    @patch('main.DMMClient')
    def test_process_posts_with_dmm(self, mock_dmm_class, mock_scraper, mock_livedoor_class):
        """DMMの作品がある場合に画像が挿入されるかテスト"""
        # 環境変数の設定
        with patch.dict('os.environ', {
            'LIVEDOOR_ID': 'test_user',
            'LIVEDOOR_API_KEY': 'test_key',
            'LIVEDOOR_BLOG_ID': 'test_blog',
            'DMM_API_ID': 'dmm_api_id',
            'DMM_AFFILIATE_ID': 'dmm_aff_id'
        }):
            # モックの設定
            mock_scraper.return_value = [
                {'name': '日暮りん', 'id': 'id1', 'url': 'url1', 'image_url': 'img1'}
            ]
            
            mock_dmm = mock_dmm_class.return_value
            mock_dmm.search_all.return_value = [
                {'title': '作品1', 'url': 'dmm_url1', 'image': 'dmm_img1'}
            ]

            mock_livedoor = mock_livedoor_class.return_value
            
            # 状態と履歴の読み込み用モック
            m = mock_open(read_data='{"current_page": 2000}')
            m.side_effect = [
                mock_open(read_data='{"current_page": 2000}').return_value, # state read
                mock_open(read_data='').return_value,                       # history read
                mock_open().return_value,                                   # history write
                mock_open().return_value                                    # state write
            ]

            with patch('builtins.open', m):
                from main import process_posts
                process_posts(dry_run=False)

            # post_article が呼ばれた際の引数を確認
            self.assertTrue(mock_livedoor.post_article.called)
            args, kwargs = mock_livedoor.post_article.call_args
            content = args[1]
            
            # DMMの画像が含まれているか
            self.assertIn('dmm_img1', content)
            self.assertIn('dmm_url1', content)
            self.assertIn('DMM作品', content)

if __name__ == '__main__':
    unittest.main()
