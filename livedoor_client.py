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
        import os
        from datetime import timezone
        
        # Createdの生成 (UTC)
        created = datetime.datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Nonceの生成 (16バイトのバイナリ)
        nonce_raw = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce_raw).decode('utf-8')
        
        # PasswordDigest = Base64 ( SHA1 ( Nonce + Created + API_KEY ) )
        sha1_digest = hashlib.sha1(nonce_raw + created.encode('utf-8') + self.api_key.encode('utf-8')).digest()
        password_digest = base64.b64encode(sha1_digest).decode('utf-8')
        
        return (
            f'UsernameToken Username="{self.livedoor_id}", '
            f'PasswordDigest="{password_digest}", '
            f'Nonce="{nonce_b64}", '
            f'Created="{created}"'
        )

    def post_article(self, title, content, category=None, draft=False):
        """記事を投稿する"""
        headers = {
            'Authorization': 'WSSE profile="UsernameToken"',
            'X-WSSE': self._get_wsse_header(),
            'Content-Type': 'application/atom+xml'
        }
        
        category_tag = f'<category scheme="http://livedoor.blogcms.jp/blog/{self.blog_id}/category" term="{category}" />' if category else ""
        draft_str = "yes" if draft else "no"

        entry_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title><![CDATA[{title}]]></title>
  <content type="text/html"><![CDATA[
    {content}
  ]]></content>
  {category_tag}
  <app:control>
    <app:draft>{draft_str}</app:draft>
  </app:control>
</entry>
"""
        res = requests.post(self.endpoint, data=entry_xml.encode('utf-8'), headers=headers)
        if res.status_code >= 400:
            print(f"Livedoor API Error: {res.status_code} - {res.text}")
        res.raise_for_status()
        return res.text
