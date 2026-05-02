"""
GitHub APIを使ってワークフローを手動トリガーし、結果を確認するスクリプト。
Personal Access Token (PAT) が必要です。
"""
import requests
import time
import sys

# GitHubリポジトリ情報
OWNER = "susumu53"
REPO  = "beauty-encyclopedia"

# PAT（個人アクセストークン）を引数または環境変数から取得
import os
PAT = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GITHUB_PAT", "")

if not PAT:
    print("使い方: python trigger_workflow.py <GitHub_Personal_Access_Token>")
    print("または環境変数 GITHUB_PAT に設定してください。")
    sys.exit(1)

headers = {
    "Authorization": f"token {PAT}",
    "Accept": "application/vnd.github.v3+json"
}

# ワークフローをトリガー
print("ワークフローを手動実行中...")
trigger_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/autopost.yml/dispatches"
resp = requests.post(trigger_url, headers=headers, json={"ref": "master"})

if resp.status_code == 204:
    print("✅ ワークフロー実行リクエスト送信成功！")
    print("   少し待ってからActionsタブで結果を確認してください。")
    print(f"   URL: https://github.com/{OWNER}/{REPO}/actions")
else:
    print(f"❌ 失敗: {resp.status_code}")
    print(resp.text)
