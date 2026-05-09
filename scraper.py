import requests
from bs4 import BeautifulSoup

def scrape_bi_girl_page(page_num):
    """bi-girl.netの一覧ページからアカウント情報を取得する"""
    url = f"https://bi-girl.net/search-images/page/{page_num}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    
    # カード要素を取得（実際のクラス名: img_wrapper_inner）
    cards = soup.find_all('div', class_='img_wrapper_inner')
    for card in cards:
        try:
            name_el   = card.select_one('.all_tweet_profile_name')
            id_el     = card.select_one('.all_tweet_profile_screenName')
            # メイン画像セクション (.img_a) 内の全ての画像を取得
            img_container = card.select_one('.img_a')
            images = []
            if img_container:
                img_tags = img_container.find_all('img')
                for img in img_tags:
                    src = img.get('data-src') or img.get('src')
                    if src and 'avatar' not in src.lower():
                        images.append(src)
            
            tweet_link_el = card.find('a', href=lambda h: h and ('x.com' in h or 'twitter.com' in h) and '/status/' in h)
            
            if name_el and id_el and tweet_link_el:
                raw_id = id_el.text.strip().lstrip('@')
                results.append({
                    "name": name_el.text.strip(),
                    "id":   raw_id,
                    "url":  tweet_link_el['href'],
                    "images": images
                })
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue
            
    return results
