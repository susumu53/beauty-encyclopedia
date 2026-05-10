import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_ranking_net(max_pages=5):
    base_url = "https://ranking.net/twitter-follower-ranking/gravure-idol/woman"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    
    items = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"Fetching {url}...")
        
        try:
            # ページ遷移時に prefetch ヘッダーをつけると JSON が返ってくる場合があるが、
            # 確実なのは HTML を取得して __NEXT_DATA__ をパースすること
            res = requests.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            res.encoding = 'utf-8'
            
            soup = BeautifulSoup(res.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            
            if not script:
                print(f"DEBUG: __NEXT_DATA__ not found on page {page}")
                # フォールバック: 直接 JSON を期待してリクエスト（ヘッダー調整）
                continue
                
            data = json.loads(script.string)
            
            # JSON構造の探索 (サブエージェントの報告に基づく)
            # props -> pageProps -> initialItems (または ranking -> items)
            try:
                page_props = data.get('props', {}).get('pageProps', {})
                # 構造はサイト更新により変わる可能性があるため、柔軟に探す
                ranking_data = page_props.get('ranking', {})
                raw_items = ranking_data.get('items', [])
                
                if not raw_items:
                    # 別の場所を探す
                    raw_items = page_props.get('initialItems', [])
                
                print(f"DEBUG: Found {len(raw_items)} items in JSON on page {page}")
                
                for ri in raw_items:
                    name = ri.get('name')
                    x_id = ri.get('twitter_id') or ri.get('twitterId')
                    
                    # twitter_id がない場合はスキップ
                    if not x_id:
                        continue
                        
                    insta_id = ri.get('instagram_id') or ri.get('instagramId')
                    tiktok_id = ri.get('tiktok_id') or ri.get('tiktokId')
                    
                    # URL形式に変換
                    insta_url = f"https://www.instagram.com/{insta_id}/" if insta_id else ""
                    # TikTok ID が @ から始まる場合とそうでない場合を考慮
                    if tiktok_id:
                        if not tiktok_id.startswith('@'):
                            tiktok_url = f"https://www.tiktok.com/@{tiktok_id}"
                        else:
                            tiktok_url = f"https://www.tiktok.com/{tiktok_id}"
                    else:
                        tiktok_url = ""
                    
                    # 画像取得 (Bing停止中)
                    images = []
                    
                    items.append({
                        "name": name,
                        "id": x_id,
                        "insta": insta_url,
                        "tiktok": tiktok_url,
                        "images": images
                    })
            except Exception as je:
                print(f"Error parsing JSON data: {je}")
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            break
            
        if page < max_pages:
            time.sleep(1)
            
    return items

if __name__ == "__main__":
    results = scrape_ranking_net(max_pages=1)
    print(f"Found {len(results)} items.")
    for r in results[:5]:
        print(r)
