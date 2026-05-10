import requests
from bs4 import BeautifulSoup
import re

def scrape_aru18_top100():
    url = "https://a-ru18.com/twitter-top100/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8'
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []
    
    soup = BeautifulSoup(res.text, 'html.parser')
    items = []
    
    # 各女優のアイテムを特定する
    # ブラウザの調査結果に基づき、ひとまず broader に取得してフィルタリング
    
    # 方法1: actress-item クラスを探す
    actress_items = soup.find_all(class_=re.compile(r'actress-item|rank-item'))
    
    if not actress_items:
        # 方法2: Xのフォローリンクが含まれる親要素を探す
        follow_links = soup.find_all('a', href=re.compile(r'(x|twitter)\.com/intent/follow\?screen_name='))
        for link in follow_links:
            screen_name = link['href'].split('screen_name=')[-1]
            
            # 名前を探す。リンクの親要素または近くの div.actress-name など
            parent = link.find_parent()
            # 近くの actress-name クラスを探すか、親のテキストを取得
            name_el = parent.find_previous(class_=re.compile(r'name'))
            if name_el:
                name = name_el.get_text(strip=True)
            else:
                # フォローするボタンのテキストを除去
                name = parent.get_text(strip=True).replace("フォローする", "").strip()
                # ランク番号やフォロワー数などの余計な情報を削ぎ落とす
                name = re.sub(r'^\d+位\s*', '', name)
                name = name.split(' ')[0]
            
            if name and screen_name:
                items.append({"name": name, "id": screen_name})
    else:
        for card in actress_items:
            name_el = card.find(class_=re.compile(r'name'))
            link_el = card.find('a', href=re.compile(r'(x|twitter)\.com/intent/follow\?screen_name='))
            
            if name_el and link_el:
                name = name_el.get_text(strip=True)
                screen_name = link_el['href'].split('screen_name=')[-1]
                items.append({"name": name, "id": screen_name})

    # 重複除去
    seen = set()
    unique_items = []
    for item in items:
        if item['id'] not in seen:
            seen.add(item['id'])
            
            # 画像取得 (Bing停止中)
            item['images'] = []
                
            unique_items.append(item)
            
    return unique_items

if __name__ == "__main__":
    results = scrape_aru18_top100()
    print(f"Found {len(results)} items.")
    for r in results[:5]:
        print(f"- {r['name']} (@{r['id']})")
