# 美女図鑑 自動投稿システム 実装プラン

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** `bi-girl.net` から美女情報を取得し、Livedoorブログへ1人1記事形式で自動投稿する。

**Architecture:** スクレイパー、Livedoor投稿クライアント、履歴管理ロジックを統合し、GitHub Actionsで定期実行する。

**Tech Stack:** Python 3.10, requests, beautifulsoup4, AtomPub API (WSSE)

---

### Task 1: Livedoor AtomPub クライアントの作成

**Files:**
- Create: `livedoor_client.py`

**Step 1: WSSE認証ヘッダーの生成と投稿機能の実装**
Livedoor IDとAPIキーを使用してWSSE認証を行い、新規記事をPOSTするクラスを作成します。

```python
import requests
import hashlib
import base64
import datetime
import random

class LivedoorClient:
    def __init__(self, livedoor_id, api_key, blog_id):
        self.livedoor_id = livedoor_id
        self.api_key = api_key
        self.blog_id = blog_id
        self.endpoint = f"https://livedoor.blogcms.jp/atompub/{blog_id}/article"

    def _get_wsse_header(self):
        created = datetime.datetime.now().isoformat() + "Z"
        nonce = hashlib.sha1(str(random.random()).encode()).hexdigest()
        digest = base64.b64encode(hashlib.sha1((nonce + created + self.api_key).encode()).digest()).decode()
        return f'UsernameToken Username="{self.livedoor_id}", PasswordDigest="{digest}", Nonce="{base64.b64encode(nonce.encode()).decode()}", Created="{created}"'

    def post_article(self, title, content):
        headers = {'X-WSSE': self._get_wsse_header(), 'Content-Type': 'application/atom+xml'}
        entry = f"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>{title}</title>
  <content type="text/html">
    <![CDATA[{content}]]>
  </content>
</entry>"""
        res = requests.post(self.endpoint, data=entry.encode('utf-8'), headers=headers)
        res.raise_for_status()
        return res.text
```

**Step 2: Commit**
```bash
git add livedoor_client.py
git commit -m "feat: add Livedoor AtomPub client"
```

---

### Task 2: スクレイパーの実装

**Files:**
- Create: `scraper.py`

**Step 1: bi-girl.net の一覧ページから情報を抽出する関数の実装**
`search-images` ページを解析し、モデル名、ID、ツイートURLのリストを返します。

```python
import requests
from bs4 import BeautifulSoup

def scrape_bi_girl_page(page_num):
    url = f"https://bi-girl.net/search-images/page/{page_num}"
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    
    results = []
    # 各投稿カードをループ（セレクタは実際のHTML構造に合わせる）
    for card in soup.select('.post-card'):
        name = card.select_one('.name').text.strip()
        x_id = card.select_one('.x-id').text.strip().replace('@', '')
        tweet_url = card.select_one('.tweet-link')['href']
        results.append({"name": name, "id": x_id, "url": tweet_url})
    return results
```

**Step 2: Commit**
```bash
git add scraper.py
git commit -m "feat: add scraper for bi-girl.net"
```

---

### Task 3: メインロジックと状態管理の実装

**Files:**
- Create: `main.py`
- Create: `history.txt`
- Create: `state.json`

**Step 1: 重複排除とバッチ処理の実装**
履歴を参照し、未投稿のアカウントのみを一定数投稿します。

```python
import json
import os
from livedoor_client import LivedoorClient
from scraper import scrape_bi_girl_page

def main():
    # 環境変数から設定取得
    LD_ID = os.getenv("LIVEDOOR_ID")
    API_KEY = os.getenv("LIVEDOOR_API_KEY")
    BLOG_ID = "ranking000-w6crxelo"
    
    client = LivedoorClient(LD_ID, API_KEY, BLOG_ID)
    
    # 状態読み込み
    with open('state.json', 'r') as f:
        state = json.load(f)
    with open('history.txt', 'r') as f:
        history = set(f.read().splitlines())

    current_page = state.get("current_page", 2000)
    items = scrape_bi_girl_page(current_page)
    
    count = 0
    for item in items:
        if count >= 5: break # 1回5件
        if item['id'] in history: continue
        
        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        content = f"<p>アカウント名：{item['name']}</p><p>X ID：@{item['id']}</p>{item['url']}"
        
        client.post_article(title, content)
        history.add(item['id'])
        count += 1
    
    # 状態保存
    with open('history.txt', 'w') as f:
        f.write('\n'.join(history))
    if count == 0 and current_page > 2: # ページ内がすべて投稿済みなら次のページへ
        state['current_page'] = current_page - 1
    with open('state.json', 'w') as f:
        json.dump(state, f)

if __name__ == "__main__":
    main()
```

---

### Task 4: GitHub Actions 設定

**Files:**
- Create: `.github/workflows/autopost.yml`

**Step 1: 定期実行とコミットバックの設定**
1時間おきに実行し、`history.txt` などを自動でリポジトリに保存します。

**Step 2: Commit**
```bash
git add .github/workflows/autopost.yml
git commit -m "feat: add github actions workflow"
```
