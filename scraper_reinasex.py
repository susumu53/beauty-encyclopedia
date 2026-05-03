import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

def scrape_reinasex(category=12, max_pages=10):
    """
    ReinaSexブログから情報を取得する
    category: 12 (Cosplayers), 1 (AV Actresses)
    max_pages: 取得する最大ページ数
    """
    base_url = f"https://reinasex.blog.2nt.com/blog-category-{category}"
    # ページ指定のリストを作成
    pages = [f"{category}.html"] + [f"{category}-{i}.html" for i in range(1, max_pages)]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    all_items = []
    
    for page_suffix in pages:
        url = f"https://reinasex.blog.2nt.com/blog-category-{page_suffix}"
        print(f"Scanning category page: {url}")
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 各記事のリンクを取得
            # 2ntブログの標準的な構造: h2 a または entry-title a
            post_links = soup.select('h2 a, .entry-title a, .post-title a')
            
            for link in post_links:
                post_url = link['href']
                if 'blog-entry' not in post_url:
                    continue
                
                print(f"  Scraping post: {post_url}")
                try:
                    p_res = requests.get(post_url, headers=headers, timeout=20)
                    p_soup = BeautifulSoup(p_res.text, 'html.parser')
                    
                    # 名前 (タイトルから推測するか、本文から探す)
                    title = p_soup.find('title').get_text(strip=True).split('|')[0].strip()
                    # 名前だけに絞り込む
                    name = title.split('さん')[0].split('-')[0].replace('SNSアカウント情報', '').replace('【', '').replace('】', '').strip()
                    # entry IDをIDの代わりとして抽出 (例: blog-entry-1617.html -> 1617)
                    entry_id_match = re.search(r'blog-entry-(\d+)', post_url)
                    entry_id = entry_id_match.group(1) if entry_id_match else str(int(time.time()))
                    
                    # 本文
                    content_body = p_soup.select_one('.entry-content, .entry_body, .post-body, .post_content')
                    if not content_body:
                        # フォールバック
                        content_body = p_soup
                        
                    # SNSリンク
                    x_id = ""
                    insta_url = ""
                    
                    all_links = content_body.find_all('a', href=True)
                    for a in all_links:
                        href = a['href']
                        if 'twitter.com' in href or 'x.com' in href:
                            match = re.search(r'(twitter\.com|x\.com)/([^/?]+)', href)
                            if match and match.group(2) not in ['intent', 'share', 'home', 'hashtag', 'search']:
                                x_id = match.group(2)
                        elif 'instagram.com' in href:
                            insta_url = href
                            
                    # 画像 (最初の1-3枚)
                    images = []
                    img_tags = content_body.find_all('img')
                    for img in img_tags:
                        src = img.get('src') or img.get('data-src')
                        if src and ('static' not in src and 'icon' not in src and 'ad' not in src):
                            # フルURLに変換
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = 'https://reinasex.blog.2nt.com' + src
                            
                            images.append(src)
                            if len(images) >= 3:
                                break
                    
                    if name:
                        all_items.append({
                            "name": name,
                            "id": x_id if x_id else f"reina_{entry_id}",
                            "insta": insta_url,
                            "images": images,
                            "url": post_url,
                            "source": "reinasex"
                        })
                except Exception as e:
                    print(f"    Error scraping post {post_url}: {e}")
                
                time.sleep(0.5) # 負荷軽減
                
        except Exception as e:
            print(f"Error scanning category page {url}: {e}")
            
    return all_items

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=int, default=1, help="Category ID (1 for AV, 12 for Cosplay)")
    parser.add_argument("--pages", type=int, default=5, help="Number of pages to scrape")
    args = parser.parse_args()

    data = scrape_reinasex(category=args.category, max_pages=args.pages)
    
    # 既存のキューを読み込む（マージするため）
    queue_path = 'queue_reinasex.json'
    if os.path.exists(queue_path):
        with open(queue_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            old_items = old_data.get("items", [])
    else:
        old_items = []

    # 重複除去してマージ（URLをキーにする）
    seen_urls = {item['url'] for item in old_items}
    new_items = old_items
    for item in data:
        if item['url'] not in seen_urls:
            new_items.append(item)
            seen_urls.add(item['url'])

    with open(queue_path, 'w', encoding='utf-8') as f:
        json.dump({"items": new_items}, f, indent=2, ensure_ascii=False)
    print(f"Finished! Total items in queue: {len(new_items)} (Added {len(new_items) - len(old_items)} new items)")
