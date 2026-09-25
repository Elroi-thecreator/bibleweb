import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_catholic")
os.makedirs(DEST_DIR, exist_ok=True)

def report_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        pct = (downloaded / total_size) * 100
        if block_num % 100 == 0:
            print(f"Downloading: {downloaded}/{total_size} bytes ({pct:.1f}%)", flush=True)

# 1. Check/download Tamil Catholic t_verses.sql
t_verses_path = os.path.join(DEST_DIR, "t_verses.sql")
if not os.path.exists(t_verses_path) or os.path.getsize(t_verses_path) < 10000000:
    url = "https://raw.githubusercontent.com/jayarathina/Tamil-Bible-Database/master/MySQL/archive/t_verses.sql"
    print(f"Fetching Tamil Catholic t_verses.sql from {url}...", flush=True)
    urllib.request.urlretrieve(url, t_verses_path, reporthook=report_hook)
    print(f"[DONE] Saved {t_verses_path} ({os.path.getsize(t_verses_path)} bytes)", flush=True)
else:
    print(f"[EXISTS] {t_verses_path} ({os.path.getsize(t_verses_path)} bytes)", flush=True)

# 2. Download English Douay-Rheims Complete Bible (all 73 books)
dr_json_path = os.path.join(DEST_DIR, "EntireBible-DR.json")
if not os.path.exists(dr_json_path) or os.path.getsize(dr_json_path) < 4000000:
    url = "https://raw.githubusercontent.com/xxruyle/Bible-DouayRheims/master/EntireBible-DR.json"
    print(f"Fetching English Complete Douay-Rheims Bible from {url}...", flush=True)
    urllib.request.urlretrieve(url, dr_json_path, reporthook=report_hook)
    print(f"[DONE] Saved {dr_json_path} ({os.path.getsize(dr_json_path)} bytes)", flush=True)
else:
    print(f"[EXISTS] {dr_json_path} ({os.path.getsize(dr_json_path)} bytes)", flush=True)

print("ALL CATHOLIC SOURCE DATA READY!", flush=True)
