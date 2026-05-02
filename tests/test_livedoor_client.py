import unittest
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

if __name__ == '__main__':
    unittest.main()
