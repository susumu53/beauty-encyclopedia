# Instagram Grid and Twitter Fix Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implement Instagram-style image grids and fix Twitter embedding issues to enhance blog post quality.

**Architecture:** 
- Unified image collection across all scrapers (list of URLs).
- CSS Grid based responsive layout in the generated HTML.
- Robust Twitter handle detection for embedding.

**Tech Stack:** Python, BeautifulSoup, CSS Grid, Livedoor AtomPub API.

---

### Task 1: Update bi-girl.net scraper for multiple images

**Files:**
- Modify: `scraper.py`

**Step 1: Modify `scrape_bi_girl_page` to collect all images in a card**
```python
# Change lines 23-38 in scraper.py to:
            # メイン画像セクション (.img_a) 内の全ての画像を取得
            img_container = card.select_one('.img_a')
            images = []
            if img_container:
                img_tags = img_container.find_all('img')
                for img in img_tags:
                    src = img.get('data-src') or img.get('src')
                    if src and 'avatar' not in src.lower():
                        images.append(src)
            
            if name_el and id_el and tweet_link_el:
                raw_id = id_el.text.strip().lstrip('@')
                results.append({
                    "name": name_el.text.strip(),
                    "id":   raw_id,
                    "url":  tweet_link_el['href'],
                    "images": images # image_urlからimagesに変更
                })
```

**Step 2: Run a manual test script to verify multiple images**
Run: `python -c "from scraper import scrape_bi_girl_page; print(scrape_bi_girl_page(2000)[0])"`
Expected: Output dict contains an 'images' list with multiple URLs.

**Step 3: Commit**
```bash
git add scraper.py
git commit -m "feat: collect multiple images from bi-girl.net"
```

### Task 2: Update main.py to handle unified image data

**Files:**
- Modify: `main.py`

**Step 1: Update image extraction in `process_posts` loop**
```python
# Modify main.py lines 201-203 to handle both old 'image_url' and new 'images' format
        images = item.get('images', [])
        if not images and item.get('image_url'):
            images = [item['image_url']]
```

**Step 2: Commit**
```bash
git add main.py
git commit -m "refactor: handle unified image format in main.py"
```

### Task 3: Implement CSS Grid for Instagram-style image display

**Files:**
- Modify: `main.py`

**Step 1: Replace `image_html` generation logic**
```python
# Modify main.py lines 206-210
        image_html = ""
        if images:
            grid_style = "display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin: 15px 0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
            
            # 1枚目だけ大きく見せる、または3列グリッド
            image_items_html = ""
            for i, img_url in enumerate(images[:9]): # 最大9枚
                item_style = "aspect-ratio: 1/1; object-fit: cover; width: 100%; display: block;"
                if len(images) == 1:
                    image_items_html += f'<img src="{img_url}" style="max-width: 100%; border-radius: 8px;">'
                    grid_style = "margin: 15px 0;" # グリッド解除
                else:
                    image_items_html += f'<img src="{img_url}" style="{item_style}">'
            
            if len(images) > 1:
                image_html = f'<div style="{grid_style}">{image_items_html}</div>'
            else:
                image_html = f'<div style="{grid_style}">{image_items_html}</div>'
```

**Step 2: Commit**
```bash
git add main.py
git commit -m "feat: implement CSS Grid for image display"
```

### Task 4: Fix Twitter Embedding Logic

**Files:**
- Modify: `main.py`

**Step 1: Improve `has_x` detection**
```python
# Modify main.py lines 171-176
        # IDが英数字のみ（Twitter IDの形式）かつ、プレースホルダでない場合にXを表示
        is_valid_x_id = bool(re.match(r'^[a-zA-Z0-9_]+$', item['id'])) and not item.get('is_placeholder_id', False)
        # reinasexの暫定IDや、特定のソースでもIDが有効なら許可するように緩和
        has_x = is_valid_x_id and not item['id'].startswith('reina_')
```

**Step 2: Commit**
```bash
git add main.py
git commit -m "fix: improve Twitter ID detection for embedding"
```

### Task 5: Final Layout Polish and SNS Buttons

**Files:**
- Modify: `main.py`

**Step 1: Update SNS link styling to look like buttons**
```python
# Modify main.py lines 187-197 to use styled <a> tags
        sns_links_html = '<div style="margin: 20px 0; display: flex; flex-wrap: wrap; gap: 10px;">'
        if has_x:
            sns_links_html += f'<a href="https://x.com/{item["id"]}" target="_blank" style="background: #000; color: #fff; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold;">X (Twitter)</a>'
        if has_insta:
            insta_id = item['insta'].rstrip('/').split('/')[-1]
            sns_links_html += f'<a href="{item["insta"]}" target="_blank" style="background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); color: #fff; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold;">Instagram</a>'
        sns_links_html += '</div>'
```

**Step 2: Verify with Dry Run**
Run: `python main.py --dry-run`
Expected: Title and content snippet show new HTML structure.

**Step 3: Commit**
```bash
git add main.py
git commit -m "style: add premium SNS buttons"
```
