import os
from dmm_client import DMMClient

api_id = "3NAaSFF1dNDrqngpJXNX"
aff_id = "namasoku-993"

client = DMMClient(api_id, aff_id)
items = client.search_all("えなこ")

print(f"Found {len(items)} items for 'えなこ'")
for item in items:
    print(f"- {item['title']}: {item['url']}")
    print(f"  Image: {item['image']}")
