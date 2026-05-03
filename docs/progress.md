# 美女図鑑 自動投稿システム — 進捗記録

> 最終更新: 2026-05-03 09:06

---

## 完了済みの作業

### 1. 基本システム (以前のセッションで完成済み)
- `livedoor_client.py` — AtomPub API 経由でブログ自動投稿
- `scraper.py` — bi-girl.net を通常の巡回ソースとしてスクレイピング
- `dmm_client.py` — 女優名でDMM/FANZAを検索しアフィリエイトリンクを生成
- `.github/workflows/autopost.yml` — GitHub Actions で1時間ごとに `main.py` を自動実行

### 2. 優先キューシステム (2026-05-03 完成)

#### ソース① a-ru18.com Top 100
- スクレーパー: `scraper_aru18.py`
- キュー: `queue_aru18.json`
- URL: https://a-ru18.com/twitter-top100/
- 内容: セクシー女優100人分のX IDを抽出
- 状態: **投稿中（残り95件）**

#### ソース② ranking.net グラビアアイドル 50人
- キュー: `queue_ranking_net.json`
- URL: https://ranking.net/twitter-follower-ranking/gravure-idol/woman
- 内容: グラビアアイドル50人 X / Instagram / TikTok リンク収録
- 状態: **待機中（50件）**

#### ソース③ reinasex.blog コスプレ系
- スクレーパー: `scraper_reinasex.py`
- キュー: `queue_reinasex.json`
- URL: https://reinasex.blog.2nt.com/blog-category-12.html ～ 12-22.html
- 内容: コスプレイヤー59人 X / Instagram / 画像（最大3枚）
- 状態: **待機中（59件）**
- 備考: カテゴリー12-23, 12-24 はDNSエラーで取得不可（サイト側の問題の可能性あり）

### 3. main.py の優先ロジック (2026-05-03 完成)
```
優先度1: queue_aru18.json      (残り95件) ← 現在処理中
優先度2: queue_ranking_net.json (50件)    ← 待機中
優先度3: queue_reinasex.json   (59件)    ← 待機中
フォールバック: bi-girl.net 巡回 (無限)
```

### 4. テンプレート機能追加 (2026-05-03 完成)
- Instagram リンクがある場合: 「📸 Instagram: [URL]」を表示
- TikTok リンクがある場合: 「🎵 TikTok: [URL]」を表示
- 画像: 最大3枚まで縦並びで表示

### 5. GitHub プッシュ完了 (2026-05-03 09:05)
- コミット: `feat: add multi-source priority queue system (a-ru18, ranking.net, reinasex) with Instagram/TikTok links and multi-image support`
- 自動投稿が GitHub Actions 経由で再開済み

---

## 現在の投稿予約状況

| キュー | 件数 | 状態 | 予想時間 |
|--------|------|------|----------|
| a-ru18.com Top 100 | 95件 | 投稿中 | 約19時間 |
| ranking.net グラビア 50 | 50件 | 待機中 | 約10時間 |
| reinasex.blog コスプレ | 59件 | 待機中 | 約12時間 |
| **合計** | **204件** | — | **約41時間** |

※ 1時間あたり5件ペース（GitHub Actions による自動実行）

---

## 残っている作業

### 優先度 高
- [ ] reinasex.blog のカテゴリー12-23, 12-24 が取得できるか再確認（サイトのDNSが復旧したら再実行）

### 優先度 低
- [ ] bi-girl.net フォールバックの動作確認（204件全消化後）
- [ ] GitHub Actions のログで正常実行を確認

---

## ファイル一覧

| ファイル | 役割 |
|----------|------|
| `main.py` | メイン投稿スクリプト（優先キュー管理込み） |
| `livedoor_client.py` | Livedoor AtomPub APIクライアント |
| `dmm_client.py` | DMM アフィリエイト検索クライアント |
| `scraper.py` | bi-girl.net スクレーパー |
| `scraper_aru18.py` | a-ru18.com スクレーパー |
| `scraper_reinasex.py` | reinasex.blog スクレーパー |
| `queue_aru18.json` | 投稿待ちリスト① |
| `queue_ranking_net.json` | 投稿待ちリスト② |
| `queue_reinasex.json` | 投稿待ちリスト③ |
| `history.txt` | 投稿済みX ID一覧（重複防止） |
| `state.json` | bi-girl.net の現在ページ番号 |
| `.github/workflows/autopost.yml` | GitHub Actions 自動実行設定 |
