import requests
from bs4 import BeautifulSoup
import json
import os
import re

from scraper_image_search import search_bing_images

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
    content = soup.select_one(".entry-content")
    if not content:
        print("Could not find entry-content")
        return []
        
    items = []
    h3_tags = content.find_all("h3")
    
    for h3 in h3_tags:
        name = h3.get_text(strip=True)
        insta_url = ""
        profile_url = ""
        username = ""
        images = []
        
        fallback_img = "https://www.lifecolle.com/wp-content/uploads/2021/05/6227e9ce70d9a9e331d381333e02648c.png"
        
        curr = h3.find_next_sibling()
        while curr and curr.name != "h3":
            links = curr.find_all("a", href=re.compile(r"instagram\.com/"))
            for link in links:
                href = link.get("href", "").split("?")[0].rstrip("/")
                if "/p/" not in href and "/reels/" not in href:
                    profile_url = href
                    username = href.split("/")[-1]
                elif not insta_url:
                    insta_url = href
            
            embed = curr.find("blockquote", class_="instagram-media")
            if embed and embed.has_attr("data-instgrm-permalink"):
                insta_url = embed["data-instgrm-permalink"].split("?")[0].rstrip("/")
            
            img_tags = curr.find_all("img")
            for img in img_tags:
                src = img.get("src") or img.get("data-src")
                if src and "http" in src and "avatar" not in src.lower():
                    if "lazy" not in src:
                        images.append(src)
            
            curr = curr.find_next_sibling()
            
        if username:
            final_insta_url = insta_url if insta_url else profile_url
            
            # Bing画像検索で画像を補強 (名前で検索)
            # 画像が少ない場合に補強する
            if len(images) < 12:
                safe_name = name.encode('ascii', 'ignore').decode('ascii') or "Beauty"
                print(f"Supplementing images for {safe_name} using Bing...")
                bing_images = search_bing_images(f"{name} 高画質 ポートレート", limit=12 - len(images))
                images.extend(bing_images)

            if not images:
                images.append(fallback_img)
                
            items.append({
                "name": name,
                "id": username,
                "insta": final_insta_url,
                "images": list(dict.fromkeys(images))[:12], # 最大12枚
                "url": url,
                "source": "lifecolle",
                "source_type": "priority"
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
    updated_count = 0
    for item in new_items:
        if item["id"].lower() not in history:
            # 既存のキューを検索
            existing_item = next((i for i in queue["items"] if i["id"].lower() == item["id"].lower()), None)
            
            if existing_item:
                # 投稿URLが見つかった場合、または画像数が増えた場合にアップグレード
                should_update = False
                if "/p/" in item["insta"] and "/p/" not in existing_item.get("insta", ""):
                    should_update = True
                if len(item["images"]) > len(existing_item.get("images", [])):
                    should_update = True
                
                if should_update:
                    existing_item["insta"] = item["insta"]
                    existing_item["images"] = item["images"]
                    updated_count += 1
            else:
                queue["items"].append(item)
                added_count += 1
            
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
        
    print(f"Added {added_count} new items, Updated {updated_count} existing items to {queue_file}")

if __name__ == "__main__":
    items = scrape_lifecolle()
    if items:
        update_queue(items)
