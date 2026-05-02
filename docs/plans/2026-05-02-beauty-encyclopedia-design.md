# 美女図鑑 自動投稿システム 設計書 (2026-05-02)

## 1. 概要
`bi-girl.net` の検索結果ページから美女（インフルエンサー）の情報を抽出し、Livedoorブログへ自動投稿するシステム。1人につき1記事を作成し、公式のX（Twitter）ポストを埋め込む。

## 2. ターゲット
- **ソース**: `https://bi-girl.net/search-images/page/{2-2000}`
- **投稿先**: `https://bijozukan.doorblog.jp/` (Livedoor Blog)
- **API**: AtomPub API

## 3. 構成要素

### 3.1 スクレイパー (`scraper.py`)
- `requests` と `BeautifulSoup4` を使用。
- 指定されたページ範囲（2〜2000）を巡回。
- 以下の情報を抽出：
    - アカウント名
    - X ID (@handle)
    - 埋め込み用ツイートURL
- 重複チェック：`processed_ids.txt` を参照し、既投稿のIDはスキップ。

### 3.2 Livedoor投稿クライアント (`livedoor_client.py`)
- AtomPub API を使用。
- WSSE認証の実装。
- 記事作成（新規エントリのPOST）。

### 3.3 自動投稿エンジン (`main.py`)
- スクレイパーとクライアントを統合。
- 1回の実行で5〜10件程度の記事を投稿。
- 進行状況（現在のページ番号など）を `state.json` に保存。

### 3.4 自動化 (`.github/workflows/autopost.yml`)
- GitHub Actions を使用して定期実行（例：1時間おき）。
- 実行後に `state.json` と `processed_ids.txt` をリポジトリに書き戻す（自動コミット）。

## 4. 記事のデザイン
- **タイトル**: `ネットで見つけた美女 [名前] (@[ID])`
- **本文構成**:
    - アカウント名: [名前]
    - X ID: @[ID]
    - [Xポストの埋め込み用ブロックコード]

## 5. 運用ルール
- GitHubの規約に配慮し、短時間での大量実行を避ける。
- クレデンシャル（APIキー）は GitHub Secrets で管理。
