
import os

history_path = 'history.txt'
if os.path.exists(history_path):
    with open(history_path, 'rb') as f:
        content = f.read(10)
        print(f"First 10 bytes of history.txt: {content.hex()}")
        if content.startswith(b'\xef\xbb\xbf'):
            print("UTF-8 BOM detected")
        elif content.startswith(b'\xff\xfe'):
            print("UTF-8 LE detected")
else:
    print("history.txt not found")
