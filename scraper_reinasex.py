import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

def scrape_reinasex(category=1, max_pages=10, exclude_urls=None):
    """
    ReinaSexブログのカテゴリ一覧ページから直接情報を取得する（詳細ページへの遷移なし）
    """
    if exclude_urls is None:
        exclude_urls = set()
    
    all_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # ページ指定のリストを作成
    pages = [f"{category}.html"] + [f"{category}-{i}.html" for i in range(1, max_pages)]
    
    for p_name in pages:
        url = f"https://reinasex.blog.2nt.com/blog-category-{p_name}"
        print(f"Scanning category page: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # h2タグ（記事タイトル）を起点にする
            h2_tags = soup.find_all('h2')
            found_on_page = 0
            
            for h2 in h2_tags:
                try:
                    link_tag = h2.find('a', href=re.compile(r'blog-entry-\d+.html'))
                    if not link_tag: continue
                    
                    post_url = link_tag['href']
                    if post_url in exclude_urls:
                        continue

                    title = link_tag.get_text(strip=True)
                    # 「きれいなお姉さん無修正」などの不要な文言を削除
                    name = title.split('さん')[0].split(' - ')[0].split('－')[0].replace('SNSアカウント情報', '').replace('きれいなお姉さん無修正', '').replace('【', '').replace('】', '').strip()
                    
                    # entry ID
                    entry_id_match = re.search(r'blog-entry-(\d+)', post_url)
                    entry_id = entry_id_match.group(1) if entry_id_match else str(int(time.time()))

                    # 本文 (h2の次のdivまたは親要素の兄弟から探す)
                    # 2ntの標準的な構造では h2 の次に .entry_body や .entry_inner が来る
                    body = h2.find_next(class_=re.compile(r'entry_body|entry_inner|content|body|post'))
                    if not body:
                        # 見つからない場合はh2の親要素から探す
                        parent = h2.parent
                        body = parent.select_one('.entry_body, .entry_inner, .content, .body') or parent
                    
                    body_html = str(body)

                    # SNSリンク抽出
                    x_id = None
                    x_match = re.search(r'x\.com/([a-zA-Z0-9_]+)', body_html) or re.search(r'twitter\.com/([a-zA-Z0-9_]+)', body_html)
                    if x_match:
                        x_id = x_match.group(1)
                    
                    insta_url = None
                    insta_match = re.search(r'(https://www\.instagram\.com/[a-zA-Z0-9_\.]+)', body_html)
                    if insta_match:
                        insta_url = insta_match.group(1)

                    tiktok_url = None
                    tiktok_match = re.search(r'(https://www\.tiktok\.com/@[a-zA-Z0-9_\.]+)', body_html)
                    if tiktok_match:
                        tiktok_url = tiktok_match.group(1)

                    # 画像抽出
                    images = []
                    img_tags = body.find_all('img')
                    for img in img_tags:
                        src = img.get('src')
                        if src and ('blog-imgs' in src or '2nt.com' in src) and 'll?' not in src:
                            # サムネイル（s.jpg）をオリジナルに変換
                            orig_src = src.replace('s.jpg', '.jpg')
                            images.append(orig_src)
                            if len(images) >= 5:
                                break
                    
                    if name:
                        all_items.append({
                            "name": name,
                            "id": x_id if x_id else f"reina_{entry_id}",
                            "insta": insta_url,
                            "tiktok": tiktok_url,
                            "images": images,
                            "url": post_url,
                            "source": "reinasex"
                        })
                        exclude_urls.add(post_url)
                        found_on_page += 1
                except Exception as e:
                    print(f"  Error parsing article: {e}")
                    continue
            
            print(f"  Found {found_on_page} new items on page.")
            time.sleep(0.5) 
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            break
            
    return all_items

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=int, default=1, help="Category ID")
    parser.add_argument("--pages", type=int, default=10, help="Number of pages")
    args = parser.parse_args()

    queue_path = 'queue_reinasex.json'
    if os.path.exists(queue_path):
        with open(queue_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            old_items = old_data.get("items", [])
    else:
        old_items = []

    seen_urls = {item['url'] for item in old_items}
    
    # 取得 (既存のURLをコピーして渡す)
    data = scrape_reinasex(category=args.category, max_pages=args.pages, exclude_urls=set(seen_urls))

    # マージ
    new_items = old_items + data

    with open(queue_path, 'w', encoding='utf-8') as f:
        json.dump({"items": new_items}, f, indent=2, ensure_ascii=False)
    print(f"Finished! Total items in queue: {len(new_items)} (Added {len(data)} new items)")
