import hashlib
import base64
import datetime
import random
import requests

class LivedoorClient:
    def __init__(self, livedoor_id, api_key, blog_id):
        self.livedoor_id = livedoor_id
        self.api_key = api_key
        self.blog_id = blog_id
        self.endpoint = f"https://livedoor.blogcms.jp/atompub/{blog_id}/article"

    def _get_wsse_header(self):
        """Livedoor AtomPub用のWSSEヘッダーを生成する"""
        created = datetime.datetime.now().isoformat() + "Z"
        # Nonceはランダムなバイト列をBase64エンコードしたもの
        nonce_raw = str(random.random()).encode()
        nonce = base64.b64encode(nonce_raw).decode()
        
        # PasswordDigest = Base64 ( SHA1 ( Nonce + Created + API_KEY ) )
        # 注意: SHA1に渡すNonceはデコードされた生のバイト列である必要がある
        sha1_digest = hashlib.sha1(nonce_raw + created.encode() + self.api_key.encode()).digest()
        password_digest = base64.b64encode(sha1_digest).decode()
        
        return (
            f'UsernameToken Username="{self.livedoor_id}", '
            f'PasswordDigest="{password_digest}", '
            f'Nonce="{nonce}", '
            f'Created="{created}"'
        )

    def post_article(self, title, content):
        """記事を投稿する (後ほど実装)"""
        pass
