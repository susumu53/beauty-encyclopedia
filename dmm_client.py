import requests

class DMMClient:
    def __init__(self, api_id, affiliate_id):
        self.api_id = api_id
        self.affiliate_id = affiliate_id
        self.base_url = "https://api.dmm.com/affiliate/v3/ItemList"

    def search_items(self, keyword, site="DMM.com"):
        """DMM APIで商品を検索する"""
        params = {
            "api_id": self.api_id,
            "affiliate_id": self.affiliate_id,
            "site": site,
            "keyword": keyword,
            "output": "json",
            "hits": 10
        }
        
        try:
            res = requests.get(self.base_url, params=params)
            res.raise_for_status()
            data = res.json()
            
            items = []
            result = data.get("result", {})
            if result.get("status") == 200:
                for item in result.get("items", []):
                    items.append({
                        "title": item.get("title") or "",
                        "url":   item.get("affiliateURL") or "",
                        "image": (item.get("imageURL") or {}).get("large") or ""
                    })
            return items
        except Exception as e:
            print(f"DMM API Error ({site}): {e}")
            return []

    def search_all(self, keyword):
        """DMM.com と FANZA の両方から検索してマージする"""
        items_general = self.search_items(keyword, site="DMM.com")
        items_adult   = self.search_items(keyword, site="FANZA")
        
        # 重複除去（URLをキーにする）
        seen_urls = set()
        merged = []
        for item in items_general + items_adult:
            if item['url'] not in seen_urls:
                merged.append(item)
                seen_urls.add(item['url'])
        
        return merged[:4] # 最大4件
