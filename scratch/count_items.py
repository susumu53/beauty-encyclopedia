
import json
import os

def count_items():
    history_path = 'history.txt'
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            h_count = len([line for line in f if line.strip()])
    else:
        h_count = 0
    
    print(f"■ 投稿済み (history.txt): {h_count}件")
    
    queues = [
        ('queue_reinasex.json', 'ReinaSex'),
        ('queue_aru18.json', 'A-RU18'),
        ('queue_ranking_net.json', 'Ranking.net')
    ]
    
    total_queue = 0
    print("\n■ 待機中 (キュー):")
    for path, name in queues:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items = data.get("items", [])
                count = len(items)
                print(f"  - {name}: {count}件")
                total_queue += count
        else:
            print(f"  - {name}: ファイルなし")
            
    print(f"\n合計待機数: {total_queue}件")

if __name__ == "__main__":
    count_items()
