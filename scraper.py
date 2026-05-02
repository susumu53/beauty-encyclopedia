import requests
from bs4 import BeautifulSoup

def scrape_bi_girl_page(page_num):
    """bi-girl.netの一覧ページからアカウント情報を取得する"""
    url = f"https://bi-girl.net/search-images/page/{page_num}"
    # 403回避のためUser-Agentを設定
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    
    # カード要素を取得
    cards = soup.select('.all-tweet-card')
    for card in cards:
        try:
            name_el = card.select_one('.all_tweet_profile_name')
            id_el = card.select_one('.all_tweet_profile_id')
            # x.com または twitter.com のリンクを取得
            tweet_link_el = card.select_one('a[href*="x.com/"][href*="/status/"]') or \
                            card.select_one('a[href*="twitter.com/"][href*="/status/"]')
            
            if name_el and id_el and tweet_link_el:
                results.append({
                    "name": name_el.text.strip(),
                    "id": id_el.text.strip().replace('@', ''),
                    "url": tweet_link_el['href']
                })
        except Exception as e:
            print(f"Error parsing card: {e}")
            continue
            
    return results
