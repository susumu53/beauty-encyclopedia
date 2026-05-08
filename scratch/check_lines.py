
import os

history_path = 'history.txt'
if os.path.exists(history_path):
    with open(history_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:10]):
            print(f"Line {i+1}: {repr(line)}")
else:
    print("history.txt not found")
