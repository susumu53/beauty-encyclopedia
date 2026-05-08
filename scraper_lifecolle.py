import requests
from bs4 import BeautifulSoup
import json
import os
import re

def scrape_lifecolle():
    url = "https://www.lifecolle.com/instagram-bijyo/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Scraping {url}...")
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    
    if res.status_code != 200:
        print(f"Failed to fetch {url}")
        return []
    
    soup = BeautifulSoup(res.text, "html.parser")
    # 記事本文のコンテナを探す
    content = soup.select_one(".entry-content")
    if not content:
        print("Could not find entry-content")
        return []
        
    items = []
    # h3タグが各美人のセクション
    h3_tags = content.find_all("h3")
    
    for h3 in h3_tags:
        name = h3.get_text(strip=True)
        # 次の要素からInstagramリンクと画像を探す
        insta_url = ""
        images = []
        
        # 記事全体の代表画像をデフォルトとして保持
        fallback_img = "https://www.lifecolle.com/wp-content/uploads/2021/04/instagram-bijyo-summary.png"
        
        curr = h3.find_next_sibling()
        # 次のh3か、要素がなくなるまでループ
        while curr and curr.name != "h3":
            # Instagramリンクの抽出
            if not insta_url:
                links = curr.find_all("a", href=re.compile(r"instagram\.com/"))
                for link in links:
                    href = link.get("href", "")
                    # 投稿URL (/p/...) ではなくプロフィールURLを優先
                    if "/p/" not in href and "/reels/" not in href:
                        insta_url = href.split("?")[0].rstrip("/")
                        break
                    elif not insta_url: # 投稿URLしかない場合はとりあえず保持
                        insta_url = href.split("?")[0].rstrip("/")
            
            # 画像の抽出
            img_tags = curr.find_all("img")
            for img in img_tags:
                src = img.get("src") or img.get("data-src")
                if src and "http" in src and "avatar" not in src.lower():
                    # 特定のアイコンや小さい画像を除外
                    if "lazy" not in src:
                        images.append(src)
            
            curr = curr.find_next_sibling()
            
        if insta_url:
            insta_id = insta_url.split("/")[-1]
            if not images:
                images.append(fallback_img)
                
            # IDが数字などの場合はスキップするか検討が必要だが、基本的には保存
            items.append({
                "name": name,
                "id": insta_id,
                "insta": insta_url,
                "images": list(dict.fromkeys(images))[:5], # 重複排除して最大5枚
                "url": url,
                "source": "lifecolle",
                "source_type": "priority" # 新規ソースなので優先的に
            })
            
    print(f"Extracted {len(items)} items from lifecolle")
    return items

def update_queue(new_items):
    queue_file = "queue_lifecolle.json"
    history_file = "history.txt"
    
    # 履歴の読み込み
    history = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = set(line.strip().lower() for line in f)
            
    # キューの読み込み
    queue = {"items": []}
    if os.path.exists(queue_file):
        with open(queue_file, "r", encoding="utf-8") as f:
            queue = json.load(f)
            
    existing_ids = set(item["id"].lower() for item in queue["items"])
    
    added_count = 0
    for item in new_items:
        if item["id"].lower() not in history and item["id"].lower() not in existing_ids:
            queue["items"].append(item)
            existing_ids.add(item["id"].lower())
            added_count += 1
            
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
        
    print(f"Added {added_count} new items to {queue_file}")

if __name__ == "__main__":
    items = scrape_lifecolle()
    if items:
        update_queue(items)
