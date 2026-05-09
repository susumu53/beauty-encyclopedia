import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_bing_images(query, limit=10):
    """
    Bing画像検索を使って画像を検索し、URLのリストを返す。
    """
    safe_query = query.encode('ascii', 'ignore').decode('ascii') or "Beauty"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Searching Bing for: {safe_query}...")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"Bing search failed with status {res.status_code}")
            return []
            
        soup = BeautifulSoup(res.text, "html.parser")
        image_urls = []
        
        # Bingの画像は class="mimg" の img タグに含まれる
        imgs = soup.find_all("img", class_="mimg")
        for img in imgs:
            src = img.get("src") or img.get("data-src")
            if src and "http" in src:
                # サムネイルURLを可能な限り高画質化 (w, hパラメータを調整)
                if "w=" in src:
                    src = re.sub(r"w=\d+", "w=600", src)
                if "h=" in src:
                    src = re.sub(r"h=\d+", "h=800", src)
                image_urls.append(src)
            
            if len(image_urls) >= limit:
                break
                
        print(f"Found {len(image_urls)} images on Bing.")
        return image_urls
        
    except Exception as e:
        print(f"Bing scraping error: {e}")
        return []

if __name__ == "__main__":
    # テスト実行
    test_results = search_bing_images("今田美桜", limit=12)
    for i, url in enumerate(test_results):
        print(f"{i+1}: {url}")
