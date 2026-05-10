import requests
from bs4 import BeautifulSoup
import json
import os
import re

def clean_name(name):
    """名前から不要な括弧やIDを削除する"""
    if not name: return ""
    name = re.sub(r'[（(][^）)]+[)）]', '', name)
    name = re.sub(r'[@＠][a-zA-Z0-9_]+', '', name)
    return name.strip()

def scrape_yuuzuki():
    url = "https://dougo-yuuzuki.jp/column_instaero/"
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
    content = soup.select_one(".c-entry__content") or soup.select_one(".entry-content")
    if not content:
        # 別のセレクタを試す
        content = soup.find("article")
        if not content:
            print("Could not find content container")
            return []
            
    items = []
    h3_tags = content.find_all("h3")
    
    for h3 in h3_tags:
        full_title = h3.get_text(strip=True)
        # 除外キーワード
        if any(k in full_title for k in ["スポット", "ハッシュタグ", "未成年", "効率よく", "方法", "理由", "一覧"]):
            continue
            
        # 形式: 名前（handle）
        name = clean_name(full_title)
        handle = ""
        handle_match = re.search(r"（([^）]+)）|[\((]([^)]+)[\))]|[@＠]([a-zA-Z0-9_]+)", full_title)
        if handle_match:
            handle = handle_match.group(1) or handle_match.group(2) or handle_match.group(3)
            
        insta_url = ""
        images = []
        
        curr = h3.find_next_sibling()
        while curr and curr.name != "h3":
            # Instagramリンクの抽出
            if not handle:
                links = curr.find_all("a", href=re.compile(r"instagram\.com/"))
                for link in links:
                    href = link.get("href", "")
                    if "/p/" in href:
                        # 投稿URLからハンドルを抽出するのは難しい場合があるが、
                        # このサイトは埋め込みがメイン
                        pass
                    else:
                        handle = href.split("?")[0].rstrip("/").split("/")[-1]
                        break
            
            # 画像の抽出 (wp-content/uploads/...)
            img_tags = curr.find_all("img")
            for img in img_tags:
                src = img.get("src") or img.get("data-src")
                if src and "http" in src and "avatar" not in src.lower() and "banner" not in src.lower():
                    if "wp-content/uploads" in src:
                        images.append(src)
            
            curr = curr.find_next_sibling()
            
        if handle:
            # Bing画像検索で画像を補強 (停止中)

            # 画像がない場合は空のままにする（または別の適切な処理）
            if not images:
                pass
                
            items.append({
                "name": name,
                "id": handle,
                "insta": f"https://www.instagram.com/{handle}/",
                "images": list(dict.fromkeys(images))[:12],
                "url": url,
                "source": "yuuzuki",
                "source_type": "priority"
            })
            
    print(f"Extracted {len(items)} items from yuuzuki")
    return items

def update_queue(new_items):
    queue_file = "queue_yuuzuki.json"
    history_file = "history.txt"
    
    history = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = set(line.strip().lower() for line in f)
            
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
    items = scrape_yuuzuki()
    if items:
        update_queue(items)
