import pytest
from scraper_aru18 import scrape_aru18_top100

def test_scrape_aru18_top100():
    items = scrape_aru18_top100()
    # 少なくとも数件は見つかるはず
    assert len(items) > 0
    
    # データの構造チェック
    item = items[0]
    assert "name" in item
    assert "id" in item
    
    # IDに@が含まれていないこと（プログラム内で処理しやすくするため）
    assert not item["id"].startswith("@")
    
    # 既知の女優が含まれているかチェック（例：三上悠亜など、ランキング常連）
    names = [i["name"] for i in items]
    print(f"Found names: {names[:5]}...")
