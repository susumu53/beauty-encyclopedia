# DMMアフィリエイト連携機能 実装プラン

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** 各モデルのDMM作品（一般・FANZA両方）を検索し、ヒットした場合は画像リンクとしてブログ記事に自動挿入する。

**Architecture:** 
1. `dmm_client.py` を新規作成し、DMMアフィリエイトAPI v3を使用して検索を行う `DMMClient` クラスを実装。
2. `main.py` の投稿テンプレートを更新し、DMMのジャケット画像をタイル状に並べるHTMLセクションを追加。

**Tech Stack:** Python 3.10, requests, pytest

---

### Task 1: DMMClientの実装 (DMM.com 検索)

**Files:**
- Create: `dmm_client.py`
- Test: `tests/test_dmm_client.py`

**Step 1: 失敗するテストを書く**
`DMMClient` が `DMM.com`（一般サイト）からアイテムを取得できることを検証するテスト。

**Step 2: テストを実行して失敗を確認する**
`python -m pytest tests/test_dmm_client.py`

**Step 3: 最小限の実装を行う**
`requests.get` を使用して `ItemList` APIを呼び出すロジック。

**Step 4: テストを実行して合格を確認する**
`python -m pytest tests/test_dmm_client.py`

**Step 5: コミット**
`git add dmm_client.py tests/test_dmm_client.py; git commit -m "feat: Add DMMClient with DMM.com search support"`

### Task 2: DMMClientの拡張 (FANZA 検索 & マージ)

**Files:**
- Modify: `dmm_client.py`
- Test: `tests/test_dmm_client.py`

**Step 1: 失敗するテストを書く**
`FANZA` サイトからも検索し、結果をマージして重複を除去するテスト。

**Step 2: テストを実行して失敗を確認する**

**Step 3: 実装を行う**
`search_all(keyword)` メソッドを追加。

**Step 4: テストを実行して合格を確認する**

**Step 5: コミット**
`git commit -am "feat: Support FANZA search and result merging in DMMClient"`

### Task 3: main.py への統合

**Files:**
- Modify: `main.py`
- Test: `tests/test_main.py`

**Step 1: 失敗するテストを書く**
`process_posts` が `DMMClient` を呼び出し、HTMLに `<img>` タグが追加されることを検証する。

**Step 2: テストを実行して失敗を確認する**

**Step 3: 実装を行う**
`main.py` 内で `DMMClient` をインスタンス化し、取得した画像を既存の `content` に追記する。

**Step 4: テストを実行して合格を確認する**

**Step 5: コミット**
`git commit -am "feat: Integrate DMM image links into blog posts"`
