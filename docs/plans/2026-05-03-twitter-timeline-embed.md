# X Timeline Embed Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Replace broken hotlinked images with an embedded X (Twitter) timeline and ensure DMM affiliate links are correctly displayed.

**Architecture:** Modify the HTML generation logic in `main.py` to include the X timeline widget and remove the direct image links.

**Tech Stack:** Python, X Timeline Widget (HTML/JS)

---

### Task 1: Update main.py to include X timeline embed

**Files:**
- Modify: `main.py:145-180`

**Step 1: Write a failing test for timeline embed**

Modify `tests/test_main.py` to assert that the `twitter-timeline` class is present in the output HTML and the `img` tags from the source are gone (except for DMM images).

```python
    def test_process_posts_timeline_embed(self):
        """Xタイムラインの埋め込みタグが含まれているかテスト"""
        with patch('os.getenv') as mock_getenv, \
             patch('os.path.exists') as mock_exists, \
             patch('livedoor_client.LivedoorClient') as mock_client_class, \
             patch('main.scrape_bi_girl_page') as mock_scrape:
            
            mock_getenv.side_effect = lambda k, default=None: {
                "LIVEDOOR_ID": "test_user",
                "LIVEDOOR_API_KEY": "test_key",
                "LIVEDOOR_BLOG_ID": "test_blog"
            }.get(k, default)
            
            mock_exists.return_value = True
            mock_scrape.return_value = [{'name': 'Girl A', 'id': 'girla_id', 'url': 'url1', 'images': ['img1.jpg']}]
            
            m = mock_open(read_data='{"current_page": 2000}')
            m.side_effect = [
                mock_open(read_data='{"current_page": 2000}').return_value,
                mock_open(read_data='').return_value,
                mock_open().return_value,
                mock_open().return_value
            ]

            with patch('builtins.open', m):
                mock_client = mock_client_class.return_value
                from main import process_posts
                process_posts(dry_run=False)

            args, _ = mock_client.post_article.call_args
            content = args[1]
            
            # Xタイムラインの埋め込みが含まれているか
            self.assertIn('class="twitter-timeline"', content)
            self.assertIn('data-height="600"', content)
            self.assertIn('girla_id', content)
            self.assertIn('widgets.js', content)
            
            # 元の画像タグが含まれていないか (Hotlinking対策)
            self.assertNotIn('img1.jpg', content)
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_main.py`
Expected: FAIL (AttributeError or AssertionError because `twitter-timeline` is missing)

**Step 3: Modify main.py to implement timeline embed**

Update the HTML generation logic:
- Replace `image_html` logic.
- Add `timeline_html` logic.
- Assemble final `content`.

```python
        # SNSリンクの構築 (既存のリンクを維持しつつ)
        sns_links_html = f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🐦 X (Twitter)：<a href="https://x.com/{item["id"]}" target="_blank" style="font-size: 24px;">@{item["id"]}</a></p>'
        
        if item.get('insta'):
            insta_id = item['insta'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">📸 Instagram：<a href="{item["insta"]}" target="_blank" style="font-size: 24px;">@{insta_id}</a></p>'
        
        if item.get('tiktok'):
            tiktok_id = item['tiktok'].rstrip('/').split('/')[-1]
            sns_links_html += f'<p style="font-size: 24px; font-weight: bold; margin: 20px 0;">🎵 TikTok：<a href="{item["tiktok"]}" target="_blank" style="font-size: 24px;">{tiktok_id}</a></p>'

        # Xタイムライン埋め込み
        timeline_html = f"""
        <div style="margin: 20px 0;">
            <a class="twitter-timeline" data-height="600" href="https://twitter.com/{item['id']}?ref_src=twsrc%5Etfw">Tweets by @{item['id']}</a>
            <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        </div>
        """

        title = f"ネットで見つけた美女 {item['name']} (@{item['id']})"
        
        # 以前の画像表示(image_html)は直リンク制限のため廃止
        
        item_url = item.get('url', f"https://x.com/{item['id']}")
        content = f"""
        <p>アカウント名：{item['name']}</p>
        {sns_links_html}
        {timeline_html}
        {dmm_section}
        <p style="margin-top: 20px;"><a href="{item_url}" target="_blank" style="color: #666; font-size: 12px;">引用元表示</a></p>
        """
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_main.py`
Expected: PASS

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: replace broken images with X timeline embed"
```

### Task 2: Manual Verification (Dry Run)

**Step 1: Run dry run**

Run: `python main.py --dry-run`
Expected: Output HTML should contain the `twitter-timeline` tags and no ReinaSex image URLs.

**Step 2: Commit (if any tweaks needed)**

```bash
git add main.py
git commit -m "chore: tweak timeline embed layout"
```
