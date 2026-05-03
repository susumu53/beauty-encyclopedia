# ranking.net Integration Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Integrate a secondary priority source from ranking.net with multi-SNS links (X, Instagram, TikTok).

**Architecture:** Use a second JSON queue and update `main.py` to check queues in priority order.

**Tech Stack:** Python, BeautifulSoup, JSON.

---

### Task 1: Create ranking.net Scraper
**Files:**
- Create: `scraper_ranking_net.py`
- Test: `tests/test_scraper_ranking_net.py`

**Step 1: Write the failing test**
```python
import pytest
from scraper_ranking_net import scrape_ranking_net

def test_scrape_ranking_net():
    items = scrape_ranking_net(max_pages=1)
    assert len(items) > 0
    assert "name" in items[0]
    assert "id" in items[0] # X ID
    # Optional fields
    assert "insta" in items[0]
    assert "tiktok" in items[0]
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_scraper_ranking_net.py -v`

**Step 3: Implement `scraper_ranking_net.py`**
- Scrape `https://ranking.net/twitter-follower-ranking/gravure-idol/woman`.
- Extract name, X, Instagram, TikTok.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_scraper_ranking_net.py -v -s`

**Step 5: Commit**

---

### Task 2: Multi-Queue Integration in `main.py`
**Files:**
- Modify: `main.py`

**Step 1: Update queue handling logic**
- Check `queue_aru18.json` first.
- If empty/missing, check `queue_ranking_net.json`.
- If missing, initialize it by scraping.

**Step 2: Update template to show Instagram/TikTok**
- Modify the `content` HTML generation.

**Step 3: Run dry-run to verify prioritization**
Run: `python main.py --dry-run`
Note: You might need to empty `queue_aru18.json` to test the fallback to ranking.net.

**Step 4: Commit**

---

### Task 3: Final Verification
**Step 1: Run a real test post**
Run: `python main.py` (with ranking.net queue active).

**Step 2: Commit and Cleanup**
