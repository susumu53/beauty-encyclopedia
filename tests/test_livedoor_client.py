import unittest
from unittest.mock import patch, MagicMock
from livedoor_client import LivedoorClient
import re

class TestLivedoorClient(unittest.TestCase):
    def setUp(self):
        self.client = LivedoorClient(
            livedoor_id="test_user",
            api_key="test_key",
            blog_id="test_blog"
        )

    def test_wsse_header_format(self):
        """WSSEヘッダーが正しい形式で生成されるかテスト"""
        header = self.client._get_wsse_header()
        
        # 必要なフィールドが含まれているかチェック
        self.assertIn('UsernameToken', header)
        self.assertIn('Username="test_user"', header)
        self.assertIn('PasswordDigest=', header)
        self.assertIn('Nonce=', header)
        self.assertIn('Created=', header)
        
        # CreatedがISO 8601形式（Z付き）かチェック
        self.assertTrue(re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', header))

    @patch('requests.post')
    def test_post_article_payload(self, mock_post):
        """post_articleが正しいXMLペイロードを送信するかテスト"""
        mock_response = MagicMock()
        mock_response.text = "success"
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.client.post_article("Sample Title", "Sample Content")

        # postが呼ばれたか確認
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        # エンドポイントの確認
        self.assertEqual(args[0], "https://livedoor.blogcms.jp/atompub/test_blog/article")
        
        # ペイロード（XML）の確認
        payload = kwargs['data'].decode('utf-8')
        self.assertIn('<title>Sample Title</title>', payload)
        self.assertIn('Sample Content', payload)
        self.assertIn('<![CDATA[', payload)

    @patch('requests.post')
    def test_post_article_with_category_and_draft(self, mock_post):
        """categoryとdraftオプションが正しくXMLに反映されるかテスト"""
        mock_response = MagicMock()
        mock_response.text = "success"
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        self.client.post_article(
            "Title", 
            "Content", 
            category="SNS美女", 
            draft=True
        )

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs['data'].decode('utf-8')
        
        # カテゴリの確認
        self.assertIn('term="SNS美女"', payload)
        self.assertIn(f'scheme="http://livedoor.blogcms.jp/blog/test_blog/category"', payload)
        
        # 下書き設定の確認
        self.assertIn('<app:draft>yes</app:draft>', payload)
        self.assertIn('xmlns:app="http://www.w3.org/2007/app"', payload)

if __name__ == '__main__':
    unittest.main()
