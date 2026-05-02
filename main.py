import json
import os
from livedoor_client import LivedoorClient
from scraper import scrape_bi_girl_page

def process_posts():
    # 設定の読み込み
    LD_ID = os.getenv("LIVEDOOR_ID")
    API_KEY = os.getenv("LIVEDOOR_API_KEY")
    BLOG_ID = os.getenv("LIVEDOOR_BLOG_ID", "ranking000-w6crxelo")
    
    if not LD_ID or not API_KEY:
        print("LIVEDOOR_ID or LIVEDOOR_API_KEY not set.")
        return

    client = LivedoorClient(LD_ID, API_KEY, BLOG_ID)
    
    # 状態（ページ番号）の読み込み
    state_path = 'state.json'
    if os.path.exists(state_path):
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {"current_page": 2000}

    # 履歴（投稿済みID）の読み込み
    history_path = 'history.txt'
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            history = set(line.strip() for line in f if line.strip())
    else:
        history = set()

    current_page = state.get("current_page", 2000)
    print(f"Scraping page {current_page}...")
    
    try:
        items = scrape_bi_girl_page(current_page)
    except Exception as e:
        print(f"Failed to scrape page {current_page}: {e}")
        return

    count = 0
    posted_this_run = 0
    for item in items:
        if posted_this_run >= 5:
            print("Batch limit reached (5 posts).")
            break
            
        if item['id'] in history:
            continue
        
        print(f"Posting: {item['name']} (@{item['id']})")
        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        # Xポストの埋め込みHTML (簡易版)
        content = f"""
        <p>アカウント名：{item['name']}</p>
        <p>X ID：@{item['id']}</p>
        <p><a href="{item['url']}">{item['url']}</a></p>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
        
        try:
            client.post_article(title, content)
            history.add(item['id'])
            posted_this_run += 1
        except Exception as e:
            print(f"Failed to post {item['id']}: {e}")
            continue
    
    # 状態の更新
    # ページ内のアイテムがすべて処理されたか、1件も新しいのがなかった場合はページを戻す
    if posted_this_run == 0 and current_page > 2:
        state['current_page'] = current_page - 1
        print(f"Moving to next page: {state['current_page']}")
    
    # ファイルに保存
    with open(history_path, 'w', encoding='utf-8') as f:
        for hid in sorted(history):
            f.write(f"{hid}\n")
            
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    process_posts()
