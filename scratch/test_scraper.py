import sys
import os
sys.path.append(os.getcwd())
from scraper import scrape_bi_girl_page
import json

page = 2026
print(f"Testing page {page}...")
try:
    items = scrape_bi_girl_page(page)
    print(f"Found {len(items)} items")
    
    with open('history.txt', 'r', encoding='utf-8') as f:
        history = set(line.strip().lower() for line in f if line.strip())
    
    new_items = []
    for item in items:
        if item['id'].lower() not in history:
            new_items.append(item)
    
    print(f"New items on this page: {len(new_items)}")
    for item in new_items[:5]:
        print(f"- {item['name']} (@{item['id']})")
except Exception as e:
    print(f"Error: {e}")
