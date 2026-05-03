# a-ru18.com Integration (X Top 100) Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Integrate a new content source from a-ru18.com to prioritize 100 actresses in the automated posting pipeline.

**Architecture:** Use a persistent JSON queue to store scraped items. Modify `main.py` to prioritize this queue before falling back to the regular source.

**Tech Stack:** Python, BeautifulSoup (requests), JSON.

---

### Task 1: Create a-ru18.com Scraper
**Files:**
- Create: `scraper_aru18.py`
- Test: `tests/test_scraper_aru18.py`

**Step 1: Write the failing test for the scraper**
```python
import pytest
from scraper_aru18 import scrape_aru18_top100

def test_scrape_aru18_top100():
    items = scrape_aru18_top100()
    assert len(items) > 0
    assert "name" in items[0]
    assert "id" in items[0]
    # Check if ID doesn't have @
    assert not items[0]["id"].startswith("@")
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_scraper_aru18.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Implement `scraper_aru18.py`**
```python
import requests
from bs4 import BeautifulSoup

def scrape_aru18_top100():
    url = "https://a-ru18.com/twitter-top100/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    
    soup = BeautifulSoup(res.text, 'html.parser')
    items = []
    
    # Structure based on browser inspection:
    # Each item has a name and a Twitter follow link
    # Example link: https://twitter.com/intent/follow?screen_name=XXXX
    links = soup.find_all('a', href=lambda h: h and 'twitter.com/intent/follow' in h)
    
    for link in links:
        screen_name = link['href'].split('screen_name=')[-1]
        # Name is usually in the parent or sibling element
        # Looking at the structure: the name is often in a tag nearby
        parent = link.find_parent()
        # Find the text content that looks like a name
        name = parent.get_text().replace("フォローする", "").strip()
        
        if name and screen_name:
            items.append({"name": name, "id": screen_name})
            
    return items
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_scraper_aru18.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add scraper_aru18.py tests/test_scraper_aru18.py
git commit -m "feat: add a-ru18.com scraper"
```

---

### Task 2: Implement Queue System in `main.py`
**Files:**
- Modify: `main.py`

**Step 1: Add queue loading and initialization logic**
Modify `main.py` to:
- Define `QUEUE_FILE = "queue_aru18.json"`
- Add a function `get_items_from_queue()` that handles scraping if file is missing.

**Step 2: Update `process_posts` to prioritize queue**
Modify the loop in `process_posts` to check the queue first.

**Step 3: Run dry-run to verify prioritization**
Run: `python main.py --dry-run`
Expected: Should show "Pulling from a-ru18.com queue..." and show items.

**Step 4: Commit**
```bash
git add main.py
git commit -m "feat: integrate a-ru18.com queue into main posting loop"
```

---

### Task 3: Final Verification
**Step 1: Run a real test post (if safe)**
Run: `python main.py` (with env vars)
Expected: Should post items from the new source.

**Step 2: Commit and Cleanup**
```bash
git add history.txt state.json queue_aru18.json
git commit -m "chore: initial queue population and test post"
```
