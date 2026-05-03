import sys
import os
import json
import datetime
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
            history = set(line.strip().lower() for line in f if line.strip())
    else:
        history = set()

    # キューの定義（優先順位順）
    queues = [
        {'path': 'queue_reinasex.json', 'name': 'ReinaSex Blog Collection'},
        {'path': 'queue_aru18.json', 'name': 'a-ru18.com Top 100'},
        {'path': 'queue_ranking_net.json', 'name': 'ranking.net Gravure 50'}
    ]

    items = []
    source_queue_path = None
    
    # 優先順位に従ってキューをチェック
    priority_items = []
    source_queue_path = None
    for q in queues:
        if os.path.exists(q['path']):
            with open(q['path'], 'r', encoding='utf-8') as f:
                q_data = json.load(f)
                q_items = q_data.get("items", [])
                
                # このキューに未投稿のアイテムがあるか確認
                has_new_items = False
                for item in q_items:
                    if item['id'].lower() not in history:
                        has_new_items = True
                        break
                
                if has_new_items:
                    print(f"Found new items in {q['name']}. Prioritizing...")
                    priority_items = q_items
                    source_queue_path = q['path']
                    break
                else:
                    print(f"All items in {q['name']} are already in history. Checking next queue...")

    # 元の巡回（bi-girl.net）もチェック
    current_page = state.get("current_page", 2000)
    print(f"Scraping page {current_page} from bi-girl.net...")
    regular_items = []
    try:
        regular_items = scrape_bi_girl_page(current_page)
    except Exception as e:
        print(f"Failed to scrape page {current_page}: {e}")

    # 合計5件になるように配分 (例: 優先 3, 通常 2)
    items_to_post = []
    
    # 優先キューから取得
    for p_item in priority_items:
        if len(items_to_post) >= 3:
            break
        if p_item['id'].lower() not in [h.lower() for h in history]:
            p_item['source_type'] = 'priority'
            items_to_post.append(p_item)
    
    # 通常巡回から取得
    for r_item in regular_items:
        if len(items_to_post) >= 5:
            break
        if r_item['id'].lower() not in [h.lower() for h in history]:
            r_item['source_type'] = 'regular'
            items_to_post.append(r_item)
    
    # まだ足りない場合は優先キューから補充
    if len(items_to_post) < 5:
        for p_item in priority_items:
            if len(items_to_post) >= 5:
                break
            if p_item['id'].lower() not in [h.lower() for h in history] and p_item not in items_to_post:
                p_item['source_type'] = 'priority'
                items_to_post.append(p_item)

    posted_this_run = 0
    posted_priority_ids = []
    posted_regular_count = 0
    
    for item in items_to_post:
        print(f"Processing ({item.get('source_type')}): {item['name']} (@{item['id']})")
        
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
        sns_links_html = f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🐦 X (Twitter)：<a href="https://x.com/{item["id"]}" target="_blank" style="font-size: 24px;">@{item["id"]}</a></p>'
        
        if item.get('insta'):
            insta_id = item['insta'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">📸 Instagram：<a href="{item["insta"]}" target="_blank" style="font-size: 24px;">@{insta_id}</a></p>'
        
        if item.get('tiktok'):
            tiktok_id = item['tiktok'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🎵 TikTok：<a href="{item["tiktok"]}" target="_blank" style="font-size: 24px;">{tiktok_id}</a></p>'
        
        # 画像セクションの構築 (bi-girl.netなどの直リンク可能な場合のみ)
        image_html = ""
        # regular (bi-girl.net) か、priorityかつreinasex以外の場合に画像を表示
        if item.get('source_type') == 'regular' or (item.get('source_type') == 'priority' and item.get('source') != 'reinasex'):
            images = item.get('images', [])
            if not images and item.get('image_url'):
                images = [item['image_url']]
            
            if images:
                image_html = "<div style='margin: 15px 0;'>"
                for img_url in images[:3]: # 最大3枚
                    image_html += f'<p><img src="{img_url}" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;"></p>'
                image_html += "</div>"

        # X (Twitter) 誘導ボタン (埋め込みの代わり)
        x_button_html = f"""
        <div style="margin: 30px 0; text-align: center;">
            <a href="https://x.com/{item['id']}" target="_blank" 
               style="display: inline-block; padding: 16px 32px; background-color: #000; color: #fff; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
               🐦 X (Twitter) で最新の投稿を見る
            </a>
        </div>
        """

        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        
        # 引用元URL
        item_url = item.get('url', f"https://x.com/{item['id']}")
        
        content = f"""
        <p>アカウント名：{item['name']}</p>
        {sns_links_html}
        {image_html}
        {x_button_html}
        {dmm_section}
        <p style="margin-top: 20px;"><a href="{item_url}" target="_blank" style="color: #666; font-size: 12px;">引用元表示</a></p>
        """
        
        if dry_run:
            print(f"--- [DRY RUN] ---")
            print(f"Title: {title}")
            print(f"Content snippet: {content[:200]}...")
            print(f"-----------------")
            posted_this_run += 1
            if item.get('source_type') == 'priority':
                posted_priority_ids.append(item['id'])
            else:
                posted_regular_count += 1
        else:
            try:
                client.post_article(title, content, category=CATEGORY)
                history.add(item['id'])
                posted_this_run += 1
                if item.get('source_type') == 'priority':
                    posted_priority_ids.append(item['id'])
                else:
                    posted_regular_count += 1
            except Exception as e:
                error_msg = f"Failed to post {item['id']}: {e}"
                print(error_msg)
                # エラーをファイルに記録（GitHub Actionsでの確認用）
                with open('error_log.txt', 'a', encoding='utf-8') as ef:
                    ef.write(f"{datetime.datetime.now()}: {error_msg}\n")
                continue
    
    if not dry_run:
        # 状態の更新
        # 全てのアイテムが既知だった場合、かつ通常投稿が1件もなかった場合
        if posted_regular_count == 0 and len(regular_items) > 0 and current_page > 2:
            # ページ内の未投稿がなくなったと判断
            all_known = True
            for r_item in regular_items:
                if r_item['id'].lower() not in [h.lower() for h in history]:
                    all_known = False
                    break
            
            if all_known:
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
        if source_queue_path and posted_priority_ids:
            with open(source_queue_path, 'r', encoding='utf-8') as f:
                q_data = json.load(f)
                items = q_data.get("items", [])
                remaining_items = [i for i in items if i['id'] not in posted_priority_ids]
                
            with open(source_queue_path, 'w', encoding='utf-8') as f:
                json.dump({"items": remaining_items}, f, indent=2, ensure_ascii=False)
            print(f"Queue {source_queue_path} updated. {len(remaining_items)} items remaining.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="実際に投稿せずに内容を表示する")
    args = parser.parse_args()
    process_posts(dry_run=args.dry_run)
