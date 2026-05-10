import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def search_bing_images(query, limit=10):
    """
    Bing画像検索を停止中（処理軽量化のため）
    """
    # print(f"Bing image search is disabled: {query}")
    return []

if __name__ == "__main__":
    # テスト実行
    print("Bing search is currently disabled.")
    test_results = search_bing_images("今田美桜", limit=12)
    print(f"Results: {test_results}")
