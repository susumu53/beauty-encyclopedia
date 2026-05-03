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

    # キューの定義（優先順位順）
    queues = [
        {'path': 'queue_aru18.json', 'name': 'a-ru18.com Top 100'},
        {'path': 'queue_ranking_net.json', 'name': 'ranking.net Gravure 50'},
        {'path': 'queue_reinasex.json', 'name': 'ReinaSex Blog Collection'}
    ]

    items = []
    source_queue_path = None
    
    # 優先順位に従ってキューをチェック
    for q in queues:
        if os.path.exists(q['path']):
            with open(q['path'], 'r', encoding='utf-8') as f:
                q_data = json.load(f)
                q_items = q_data.get("items", [])
                if q_items:
                    print(f"Found {len(q_items)} items in {q['name']}. Prioritizing...")
                    items = q_items
                    source_queue_path = q['path']
                    break

    # キューが空（または存在しない）場合は元の巡回へ
    if not items:
        current_page = state.get("current_page", 2000)
        print(f"No priority queues found. Scraping page {current_page} from bi-girl.net...")
        try:
            items = scrape_bi_girl_page(current_page)
        except Exception as e:
            print(f"Failed to scrape page {current_page}: {e}")
            return

    posted_this_run = 0
    remaining_items = list(items)
    
    for item in items:
        if posted_this_run >= 5:
            print("Batch limit reached (5 posts).")
            break
            
        if item['id'] in history:
            if source_queue_path:
                remaining_items = [i for i in remaining_items if i['id'] != item['id']]
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

        # SNSリンクの構築
        sns_section = ""
        if item.get('insta'):
            sns_section += f"<p>📸 Instagram: <a href='{item['insta']}' target='_blank'>{item['insta']}</a></p>"
        if item.get('tiktok'):
            sns_section += f"<p>🎵 TikTok: <a href='{item['tiktok']}' target='_blank'>{item['tiktok']}</a></p>"

        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        
        # 画像セクションの構築 (複数枚対応)
        image_html = ""
        images = item.get('images', [])
        if not images and item.get('image_url'):
            images = [item['image_url']]
            
        if images:
            image_html = "<div style='margin: 15px 0;'>"
            for img_url in images[:3]: # 最大3枚
                image_html += f'<p><img src="{img_url}" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;"></p>'
            image_html += "</div>"

        item_url = item.get('url', f"https://x.com/{item['id']}")
        
        x_profile_url = f"https://x.com/{item['id']}"
        content = f"""
        <p>アカウント名：{item['name']}</p>
        <p style="font-size: 15px; font-weight: bold;">🐦 X (Twitter)：<a href="{x_profile_url}" target="_blank" style="font-size: 15px;">@{item['id']}</a></p>
        {sns_section}
        {image_html}
        {dmm_section}
        <p><a href="{item_url}">{item_url}</a></p>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
        
        if dry_run:
            print(f"--- [DRY RUN] ---")
            print(f"Title: {title}")
            print(f"Content snippet: {content[:200]}...")
            print(f"-----------------")
            posted_this_run += 1
            if source_queue_path:
                remaining_items = [i for i in remaining_items if i['id'] != item['id']]
        else:
            try:
                client.post_article(title, content, category=CATEGORY)
                history.add(item['id'])
                posted_this_run += 1
                if source_queue_path:
                    remaining_items = [i for i in remaining_items if i['id'] != item['id']]
            except Exception as e:
                print(f"Failed to post {item['id']}: {e}")
                continue
    
    if not dry_run:
        # 状態の更新
        if not source_queue_path and posted_this_run == 0 and current_page > 2:
            state['current_page'] = current_page - 1
            print(f"Moving to next page: {state['current_page']}")
        
        # 履歴の保存
        with open(history_path, 'w', encoding='utf-8') as f:
            for hid in sorted(history):
                f.write(f"{hid}\n")
                
        # 状態の保存
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

        # キューの更新
        if source_queue_path:
            with open(source_queue_path, 'w', encoding='utf-8') as f:
                json.dump({"items": remaining_items}, f, indent=2, ensure_ascii=False)
            print(f"Queue {source_queue_path} updated. {len(remaining_items)} items remaining.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="実際に投稿せずに内容を表示する")
    args = parser.parse_args()
    process_posts(dry_run=args.dry_run)
