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
        {'path': 'queue_lifecolle.json', 'name': 'Lifecolle Instagram Collection'},
        {'path': 'queue_yuuzuki.json', 'name': 'Dougo-Yuuzuki Column Collection'},
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

    # 合計5件になるように配分
    items_to_post = []
    seen_ids = set()
    
    # 優先キューから取得 (最大3件)
    for p_item in priority_items:
        if len(items_to_post) >= 3:
            break
        p_id = p_item.get('id')
        if not p_id:
            continue
        p_id_low = p_id.lower()
        if p_id_low not in history and p_id_low not in seen_ids:
            p_item['source_type'] = 'priority'
            items_to_post.append(p_item)
            seen_ids.add(p_id_low)
    
    # 通常巡回から取得 (合計5件まで)
    for r_item in regular_items:
        if len(items_to_post) >= 5:
            break
        r_id = r_item.get('id')
        if not r_id:
            continue
        r_id_low = r_id.lower()
        if r_id_low not in history and r_id_low not in seen_ids:
            r_item['source_type'] = 'regular'
            items_to_post.append(r_item)
            seen_ids.add(r_id_low)
    
    # まだ足りない場合は優先キューからさらに補充
    if len(items_to_post) < 5:
        for p_item in priority_items:
            if len(items_to_post) >= 5:
                break
            p_id = p_item.get('id')
            if not p_id:
                continue
            p_id_low = p_id.lower()
            if p_id_low not in history and p_id_low not in seen_ids:
                p_item['source_type'] = 'priority'
                items_to_post.append(p_item)
                seen_ids.add(p_id_low)

    posted_this_run = 0
    posted_priority_ids = []
    posted_regular_count = 0
    
    if not items_to_post:
        print("No new items to post.")
        return

    print(f"Selected {len(items_to_post)} items to post.")
    
    for item in items_to_post:
        item_id = item.get('id', 'unknown')
        print(f"Processing ({item.get('source_type')}): {item['name']} (@{item_id})")
        
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

        # SNSリンクの存在確認
        # lifecolle, yuuzuki は Instagram がメインなので X は無しとする
        is_placeholder_x = item.get('is_placeholder_id', False) or \
                          (item.get('source') == 'reinasex' and item['id'].startswith('reina_')) or \
                          (item.get('source') in ['lifecolle', 'yuuzuki'])
        
        has_x = not is_placeholder_x
        has_insta = bool(item.get('insta'))
        has_tiktok = bool(item.get('tiktok'))
        
        if not (has_x or has_insta or has_tiktok):
            print(f"Skipping {item['name']} - No valid SNS links found.")
            # 履歴に追加して次回以降スキップ＆キューから削除されるようにする
            history.add(item['id'].lower())
            continue

        # SNSリンクの構築
        sns_links_html = ""
        if has_x:
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🐦 X (Twitter)：<a href="https://x.com/{item["id"]}" target="_blank" style="font-size: 24px;">@{item["id"]}</a></p>'
        
        if has_insta:
            insta_id = item['insta'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">📸 Instagram：<a href="{item["insta"]}" target="_blank" style="font-size: 24px;">@{insta_id}</a></p>'
        
        if has_tiktok:
            tiktok_id = item['tiktok'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🎵 TikTok：<a href="{item["tiktok"]}" target="_blank" style="font-size: 24px;">{tiktok_id}</a></p>'
        
        # 画像セクションの構築 (直リンク可能な場合)
        image_html = ""
        images = item.get('images', [])
        if not images and item.get('image_url'):
            images = [item['image_url']]
        
        # 2ntなどの特定の画像を除外していた制限を解除
        if images:
            image_html = "<div style='margin: 15px 0;'>"
            for img_url in images[:3]: # 最大3枚を表示
                image_html += f'<p><img src="{img_url}" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;"></p>'
            image_html += "</div>"

        # サムネイル（一番最初の画像）
        thumbnail_url = images[0] if images else None

        # X (Twitter) タイムライン埋め込み
        x_embed_html = ""
        if has_x:
            x_embed_html = f"""
            <div style="margin: 30px 0;">
                <p style="font-weight: bold; margin-bottom: 10px;">最新のツイート</p>
                <a class="twitter-timeline" 
                   data-height="600" 
                   data-chrome="noheader nofooter noborders" 
                   href="https://twitter.com/{item['id']}?ref_src=twsrc%5Etfw">
                   Tweets by {item['id']}
                </a>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            </div>
            """

        # タイトルの生成 (ReinaSex特有の文言を削除)
        clean_name = item['name'].replace(' - きれいなお姉さん無修正', '').replace('きれいなお姉さん無修正', '').strip().rstrip('-').strip()
        if has_x:
            title = f"ネットで見つけた美女 {clean_name} (@{item['id']})"
        elif has_insta:
            insta_id = item['insta'].rstrip('/').split('/')[-1]
            title = f"ネットで見つけた美女 {clean_name} (@{insta_id})"
        else:
            title = f"ネットで見つけた美女 {clean_name}"
        
        # 引用元URL
        item_url = item.get('url', f"https://x.com/{item['id']}")
        
        content = f"""
        <p>アカウント名：{item['name']}</p>
        {sns_links_html}
        {image_html}
        {x_embed_html}
        {dmm_section}
        <p style="margin-top: 20px;"><a href="{item_url}" target="_blank" style="color: #666; font-size: 12px;">引用元表示</a></p>
        """
        
        if dry_run:
            print(f"--- [DRY RUN] ---")
            print(f"Title: {title}")
            print(f"Thumbnail: {thumbnail_url}")
            print(f"Content snippet: {content[:200]}...")
            print(f"-----------------")
            posted_this_run += 1
            if item.get('source_type') == 'priority':
                posted_priority_ids.append(item['id'])
            else:
                posted_regular_count += 1
        else:
            try:
                client.post_article(title, content, category=CATEGORY, thumbnail_url=thumbnail_url)
                history.add(item['id'].lower())
                posted_this_run += 1
                if item.get('source_type') == 'priority':
                    posted_priority_ids.append(item['id'].lower())
                else:
                    posted_regular_count += 1
            except Exception as e:
                error_msg = f"Failed to post {item.get('id', 'unknown')}: {e}"
                print(error_msg)
                # エラーをファイルに記録（GitHub Actionsでの確認用）
                try:
                    with open('error_log.txt', 'a', encoding='utf-8') as ef:
                        ef.write(f"{datetime.datetime.now()}: {error_msg}\n")
                except:
                    pass
                continue
    
    if not dry_run:
        # 状態の更新
        # 全てのアイテムが既知だった場合、かつ通常投稿が1件もなかった場合
        if posted_regular_count == 0 and len(regular_items) > 0 and current_page > 2:
            # ページ内の未投稿がなくなったと判断
            all_known = True
            for r_item in regular_items:
                if r_item['id'].lower() not in history:
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
        if source_queue_path:
            with open(source_queue_path, 'r', encoding='utf-8') as f:
                q_data = json.load(f)
                items = q_data.get("items", [])
                # 履歴にあるものをすべて除外
                remaining_items = [i for i in items if i['id'].lower() not in history]
                
            with open(source_queue_path, 'w', encoding='utf-8') as f:
                json.dump({"items": remaining_items}, f, indent=2, ensure_ascii=False)
            print(f"Queue {source_queue_path} updated. {len(remaining_items)} items remaining.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="実際に投稿せずに内容を表示する")
    args = parser.parse_args()
    process_posts(dry_run=args.dry_run)
