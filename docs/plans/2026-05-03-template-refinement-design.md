# 2026-05-03 記事テンプレートの再調整（ソース別出し分けとX誘導の強化）

## 概要
Xタイムラインの埋め込みがライブドアブログの仕様により正常に表示されない（単なるリンクになる）ため、ソースごとに最適な表示形式に切り替えます。また、全記事においてX（旧Twitter）への誘導をより分かりやすく強化します。

## 目的
- `bi-girl.net` からの投稿において画像を復活させ、視覚的な魅力を取り戻す。
- 画像が表示されない `ReinaSex` 等の投稿においても、Xへの誘導を強化することでコンテンツ不足を補う。
- JavaScriptに依存しない、確実で分かりやすいボタン形式のSNS誘導を導入する。

## 変更内容

### 1. ソース判定ロジックの導入
`main.py` 内で、アイテムのソース（`bi-girl.net` かそれ以外か）を判定します。
- `source_type == 'regular'` の場合：`bi-girl.net` と判断。
- `source == 'reinasex'` の場合：画像ブロック対象と判断。

### 2. テンプレートの出し分け
#### bi-girl.net 記事
1. アカウント情報
2. SNSリンク
3. **メイン画像（最大3枚）**：復活
4. **Xへの誘導ボタン**：新規（「Xで最新の投稿をチェック」）
5. DMM作品

#### ReinaSex 等（画像ブロック対象）記事
1. アカウント情報
2. SNSリンク
3. **Xへの誘導ボタン**：新規（「Xで最新の画像・投稿をチェック」として大きく表示）
4. DMM作品

### 3. Xへの誘導ボタンのデザイン
JavaScriptを使わず、CSSスタイルをインラインで適用した分かりやすいリンクボタンを作成します。
例：
```html
<div style="margin: 20px 0; text-align: center;">
    <a href="https://x.com/[ID]" target="_blank" 
       style="display: inline-block; padding: 15px 30px; background-color: #000; color: #fff; text-decoration: none; border-radius: 30px; font-weight: bold; font-size: 18px;">
       🐦 X (Twitter) で最新の投稿を見る
    </a>
</div>
```

## テスト計画
- `python main.py --dry-run` で、`regular` と `priority` それぞれのソースに対して期待通りのHTMLが生成されるか確認。
- 実際にテスト投稿を行い、スマホ・PC両方でボタンが押しやすく表示されているか確認。
