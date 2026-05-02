import sys
import os
import json
from livedoor_client import LivedoorClient
from scraper import scrape_bi_girl_page
from dmm_client import DMMClient
from scraper_aru18 import scrape_aru18_top100
import argparse

# Windows環境でのエンコーディングエラー対策
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def process_posts(dry_run=False):
    # 設定の読み込み
    LD_ID = os.getenv("LIVEDOOR_ID", "ranking000")
    API_KEY = os.getenv("LIVEDOOR_API_KEY")
    BLOG_ID = os.getenv("LIVEDOOR_BLOG_ID", "ranking000-w6crxelo")
    CATEGORY = os.getenv("LIVEDOOR_CATEGORY")
    
    DMM_API_ID = os.getenv("DMM_API_ID")
    DMM_AFFILIATE_ID = os.getenv("DMM_AFFILIATE_ID")
    
    if not dry_run and (not LD_ID or not API_KEY):
        print("LIVEDOOR_ID or LIVEDOOR_API_KEY not set. Skipping real post.")
        if not API_KEY:
            print("Hint: API_KEY (AtomPub API Key) is required for real posting.")
        dry_run = True

    client = LivedoorClient(LD_ID, API_KEY, BLOG_ID) if LD_ID and API_KEY else None
    dmm_client = DMMClient(DMM_API_ID, DMM_AFFILIATE_ID) if DMM_API_ID and DMM_AFFILIATE_ID else None
    
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

    # a-ru18.com キューの読み込み
    queue_path = 'queue_aru18.json'
    queue_items = []
    if os.path.exists(queue_path):
        with open(queue_path, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
            queue_items = queue_data.get("items", [])
    elif True: # ファイルがない場合は常に作成を試みる
        # キューファイルがない場合は新規作成（一度だけ実行）
        print("Initializing a-ru18.com queue...")
        queue_items = scrape_aru18_top100()
        with open(queue_path, 'w', encoding='utf-8') as f:
            json.dump({"items": queue_items}, f, indent=2, ensure_ascii=False)
        print(f"Queue initialized with {len(queue_items)} items.")

    items = []
    source_is_queue = False
    
    if queue_items:
        print(f"Found {len(queue_items)} items in a-ru18.com queue. Prioritizing...")
        items = queue_items
        source_is_queue = True
    else:
        current_page = state.get("current_page", 2000)
        print(f"Scraping page {current_page}...")
        try:
            items = scrape_bi_girl_page(current_page)
        except Exception as e:
            print(f"Failed to scrape page {current_page}: {e}")
            return

    posted_this_run = 0
    remaining_queue = list(queue_items) if source_is_queue else []
    
    for item in items:
        if posted_this_run >= 5:
            print("Batch limit reached (5 posts).")
            break
            
        if item['id'] in history:
            if source_is_queue:
                # すでに投稿済みの場合はキューから外して次へ
                remaining_queue = [i for i in remaining_queue if i['id'] != item['id']]
            continue
        
        print(f"Processing: {item['name']} (@{item['id']})")
        
        # DMM検索
        dmm_section = ""
        if dmm_client:
            dmm_items = dmm_client.search_all(item['name'])
            if dmm_items:
                dmm_section = "<h3>DMM作品</h3><div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
                for d_item in dmm_items:
                    dmm_section += f"""
                    <div style='width: 45%;'>
                        <a href='{d_item['url']}' target='_blank'>
                            <img src='{d_item['image']}' style='width: 100%; border-radius: 5px;'>
                        </a>
                    </div>
                    """
                dmm_section += "</div>"

        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        # Xポストの埋め込みHTML (簡易版) と 画像
        image_html = f'<p><img src="{item["image_url"]}" style="max-width: 100%;"></p>' if item.get('image_url') else ""
        # 投稿URLがなければXのプロフィールURLを推測
        item_url = item.get('url', f"https://x.com/{item['id']}")
        content = f"""
        <p>アカウント名：{item['name']}</p>
        <p>X ID：@{item['id']}</p>
        {image_html}
        {dmm_section}
        <p><a href="{item_url}">{item_url}</a></p>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
        
        if dry_run:
            print(f"--- [DRY RUN] ---")
            print(f"Title: {title}")
            print(f"Category: {CATEGORY}")
            print(f"Content: {content[:200]}...")
            print(f"-----------------")
            posted_this_run += 1
            if source_is_queue:
                remaining_queue = [i for i in remaining_queue if i['id'] != item['id']]
        else:
            try:
                client.post_article(title, content, category=CATEGORY)
                history.add(item['id'])
                posted_this_run += 1
                if source_is_queue:
                    remaining_queue = [i for i in remaining_queue if i['id'] != item['id']]
            except Exception as e:
                print(f"Failed to post {item['id']}: {e}")
                continue
    
    if not dry_run:
        # 状態の更新
        if not source_is_queue and posted_this_run == 0 and current_page > 2:
            state['current_page'] = current_page - 1
            print(f"Moving to next page: {state['current_page']}")
        
        # ファイルに保存
        with open(history_path, 'w', encoding='utf-8') as f:
            for hid in sorted(history):
                f.write(f"{hid}\n")
                
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

        # キューの保存
        if source_is_queue:
            with open(queue_path, 'w', encoding='utf-8') as f:
                json.dump({"items": remaining_queue}, f, indent=2, ensure_ascii=False)
            print(f"Queue updated. {len(remaining_queue)} items remaining.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="実際に投稿せずに内容を表示する")
    args = parser.parse_args()
    process_posts(dry_run=args.dry_run)
