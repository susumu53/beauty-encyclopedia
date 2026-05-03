import sys
import os
sys.path.append(os.getcwd())
from dmm_client import DMMClient

api_id = "3NAaSFF1dNDrqngpJXNX"
aff_id = "namasoku-993"

client = DMMClient(api_id, aff_id)
keyword = "小倉由菜"
print(f"Searching for '{keyword}'...")
items = client.search_all(keyword)

print(f"Found {len(items)} items")
for item in items:
    print(f"- {item['title']}")
