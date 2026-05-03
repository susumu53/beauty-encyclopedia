import pytest
from scraper_ranking_net import scrape_ranking_net

def test_scrape_ranking_net():
    # テスト時間を短縮するため1ページ目のみ取得
    items = scrape_ranking_net(max_pages=1)
    assert len(items) > 0
    
    item = items[0]
    assert "name" in item
    assert "id" in item # X ID
    assert "insta" in item # Instagram (URL or ID)
    assert "tiktok" in item # TikTok (URL or ID)
    
    # 型チェック
    assert isinstance(item["name"], str)
    assert isinstance(item["id"], str)
    
    print(f"\nFound {len(items)} items. Sample: {items[0]}")
