import os
import sys
import urllib.request
import json

sys.stdout.reconfigure(encoding='utf-8')

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_catholic")
os.makedirs(DEST_DIR, exist_ok=True)

def report_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = (downloaded / total_size) * 100
        if block_num % 100 == 0:
            print(f"Downloading: {downloaded}/{total_size} bytes ({pct:.1f}%)", flush=True)

# 1. Download Tamil Catholic t_verses.sql if not exists
t_verses_path = os.path.join(DEST_DIR, "t_verses.sql")
if not os.path.exists(t_verses_path) or os.path.getsize(t_verses_path) < 10000000:
    url = "https://raw.githubusercontent.com/jayarathina/Tamil-Bible-Database/master/MySQL/archive/t_verses.sql"
    print(f"Fetching Tamil Catholic t_verses.sql from {url}...", flush=True)
    urllib.request.urlretrieve(url, t_verses_path, reporthook=report_hook)
    print(f"[DONE] Saved {t_verses_path} ({os.path.getsize(t_verses_path)} bytes)", flush=True)
else:
    print(f"[EXISTS] {t_verses_path} ({os.path.getsize(t_verses_path)} bytes)", flush=True)

# 2. Download English Douay-Rheims Deuterocanonical Books
dr_books = ['tobias', 'judith', 'wisdom', 'ecclesiasticus', 'baruch', '1-machabees', '2-machabees']
for b in dr_books:
    b_path = os.path.join(DEST_DIR, f"{b}.json")
    if not os.path.exists(b_path):
        url = f"https://raw.githubusercontent.com/janvier-s/original-douay-rheims/master/bible/raw/{b}.json"
        print(f"Fetching English DR {b}...", flush=True)
        urllib.request.urlretrieve(url, b_path)
        print(f"[DONE] Saved {b_path}", flush=True)
    else:
        print(f"[EXISTS] {b_path}", flush=True)

print("ALL CATHOLIC SOURCE DATA ACQUIRED SUCCESSFULLY!", flush=True)
