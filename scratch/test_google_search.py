import requests
import json
import os

# ユーザーから提供された情報
API_KEY = "AIzaSyA-ruJRF1-hnKbk1odmz4rtVpkZNmhk6WA"
CX = "642f3d58fce0040de"

def test_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CX,
        'q': query,
        'num': 3,
        'searchType': 'image'
    }
    
    print(f"Searching for: {query}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            print(f"SUCCESS! {len(data['items'])} images found.")
            for i, item in enumerate(data['items']):
                print(f"Image {i+1}: {item['link']}")
        else:
            print("FAILED: No images found. 'Search the entire web' might be OFF.")
            print("Response:", json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # テスト検索
    test_search("石原さとみ 高画質 ポートレート")
