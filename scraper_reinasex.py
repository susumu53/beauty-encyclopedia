import requests
from bs4 import BeautifulSoup
import re
import time
import json

def scrape_reinasex_all():
    base_url = "https://reinasex.blog.2nt.com/blog-category-12"
    # ページ指定のリストを作成 (12, 12-1, ..., 12-24)
    pages = ["12.html"] + [f"12-{i}.html" for i in range(1, 25)]
    
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
                    # 名前だけに絞り込む (例: "女優名 SNSアカウント情報" -> "女優名")
                    name = title.replace('SNSアカウント情報', '').replace('【', '').replace('】', '').strip()
                    
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
                    
                    if name and x_id:
                        all_items.append({
                            "name": name,
                            "id": x_id,
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
    data = scrape_reinasex_all()
    with open('queue_reinasex.json', 'w', encoding='utf-8') as f:
        json.dump({"items": data}, f, indent=2, ensure_ascii=False)
    print(f"Finished! Total items: {len(data)}")
