import requests

def debug_html(page):
    url = f"https://bi-girl.net/search-images/page/{page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    with open("scratch/debug_page.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("Saved HTML to scratch/debug_page.html")

if __name__ == "__main__":
    debug_html(1993)
