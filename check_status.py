import json
a = json.load(open('queue_aru18.json', 'r', encoding='utf-8'))
r = json.load(open('queue_ranking_net.json', 'r', encoding='utf-8'))
s = json.load(open('queue_reinasex.json', 'r', encoding='utf-8'))
print(f'Aru18: {len(a["items"])} items')
print(f'Ranking.net: {len(r["items"])} items')
print(f'ReinaSex: {len(s["items"])} items')
print(f'Total queued: {len(a["items"]) + len(r["items"]) + len(s["items"])} items')
print(f'At 5 per hour, that is {(len(a["items"]) + len(r["items"]) + len(s["items"])) / 5:.0f} hours of content')
