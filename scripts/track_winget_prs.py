import urllib.request
import json
import os
import sys
import ssl
from datetime import datetime, timezone

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl._create_unverified_context()

TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN') or ''
HEADERS = {
    'User-Agent': 'WinGet-PR-Tracker'
}
if TOKEN:
    HEADERS['Authorization'] = f'Bearer {TOKEN}'

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(ROOT_DIR, '.winget_pr_state.json')
PR_LIST = [479139, 460301, 446873]

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_pr_details(pr_num):
    url_pr = f'https://api.github.com/repos/microsoft/winget-pkgs/pulls/{pr_num}'
    pr_data = fetch_json(url_pr)
        
    url_com = f'https://api.github.com/repos/microsoft/winget-pkgs/issues/{pr_num}/comments?per_page=50'
    coms_data = fetch_json(url_com)
        
    url_reviews = f'https://api.github.com/repos/microsoft/winget-pkgs/pulls/{pr_num}/reviews'
    reviews_data = fetch_json(url_reviews)
    
    sha = pr_data['head']['sha']
    url_cr = f'https://api.github.com/repos/microsoft/winget-pkgs/commits/{sha}/check-runs?per_page=100'
    cr_data = fetch_json(url_cr)
    
    labels = [l['name'] for l in pr_data.get('labels', [])]
    return {
        'number': pr_num,
        'title': pr_data.get('title'),
        'state': pr_data.get('state'),
        'merged': pr_data.get('merged', False),
        'merged_at': pr_data.get('merged_at'),
        'closed_at': pr_data.get('closed_at'),
        'mergeable': pr_data.get('mergeable'),
        'mergeable_state': pr_data.get('mergeable_state'),
        'labels': labels,
        'head_sha': sha,
        'comments_count': len(coms_data),
        'comments': [{
            'user': c['user']['login'],
            'created_at': c['created_at'],
            'body': c['body']
        } for c in coms_data],
        'reviews': [{
            'user': r['user']['login'],
            'state': r['state'],
            'submitted_at': r.get('submitted_at'),
            'body': r.get('body')
        } for r in reviews_data],
        'check_runs': [{
            'name': cr['name'],
            'status': cr['status'],
            'conclusion': cr.get('conclusion')
        } for cr in cr_data.get('check_runs', []) if cr['name'][0].isdigit() or cr['name'] == 'license/cla']
    }

def run_check():
    prev_state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                prev_state = json.load(f)
        except Exception:
            prev_state = {}
            
    current_state = {}
    changes = []
    
    for pr_num in PR_LIST:
        try:
            curr = fetch_pr_details(pr_num)
            current_state[str(pr_num)] = curr
            
            prev = prev_state.get(str(pr_num))
            if prev:
                if curr['state'] != prev.get('state'):
                    changes.append(f"PR #{pr_num} state changed: {prev.get('state')} -> {curr['state']}")
                if curr['merged'] != prev.get('merged'):
                    changes.append(f"PR #{pr_num} merged status: {curr['merged']} (at {curr.get('merged_at')})")
                new_labels = set(curr['labels']) - set(prev.get('labels', []))
                removed_labels = set(prev.get('labels', [])) - set(curr['labels'])
                if new_labels:
                    changes.append(f"PR #{pr_num} added labels: {list(new_labels)}")
                if removed_labels:
                    changes.append(f"PR #{pr_num} removed labels: {list(removed_labels)}")
                if curr['comments_count'] > prev.get('comments_count', 0):
                    new_comms = curr['comments'][prev.get('comments_count', 0):]
                    for nc in new_comms:
                        changes.append(f"PR #{pr_num} new comment from @{nc['user']} ({nc['created_at']}): {nc['body'][:200]}")
                if len(curr['reviews']) > len(prev.get('reviews', [])):
                    new_revs = curr['reviews'][len(prev.get('reviews', [])):]
                    for nr in new_revs:
                        changes.append(f"PR #{pr_num} new review from @{nr['user']}: {nr['state']} - {nr.get('body', '')[:200]}")
            else:
                changes.append(f"PR #{pr_num} initialized tracking (State: {curr['state']}, Labels: {curr['labels']})")
        except Exception as e:
            changes.append(f"Error fetching PR #{pr_num}: {e}")
            
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=2)
        
    return current_state, changes

def main():
    is_hook = '--hook' in sys.argv
    current_state, changes = run_check()
    
    if is_hook:
        # Format for SessionStart hook (stdout JSON)
        status_lines = []
        for pr_num, d in current_state.items():
            status_lines.append(f"PR #{pr_num} ({d.get('title')}): {d.get('state')}, Labels: {d.get('labels')}")
        status_text = " | ".join(status_lines)
        changes_text = f" [Changes: {'; '.join(changes)}]" if changes else " [No new changes]"
        
        msg = f"[WinGet Watcher Hook] Session Started. Current Status: {status_text}{changes_text}. Please maintain the periodic background tracker (cron 0 */6 * * *)."
        hook_output = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": msg
                    }
                }
            ]
        }
        print(json.dumps(hook_output))
        return

    print(f"[{datetime.now(timezone.utc).isoformat()}] WinGet PR Check Complete.")
    if changes:
        print("CHANGES DETECTED:")
        for ch in changes:
            print(f"  * {ch}")
    else:
        print("No changes detected since last check.")
        
    for pr_num, d in current_state.items():
        print(f"\n--- PR #{pr_num}: {d.get('title')} ---")
        print(f"State: {d.get('state')} | Merged: {d.get('merged')} | Mergeable: {d.get('mergeable')} ({d.get('mergeable_state')})")
        print(f"Labels: {d.get('labels')}")
        print(f"Comments: {d.get('comments_count')} | Reviews: {len(d.get('reviews', []))}")
        print("Check Runs:")
        for cr in sorted(d.get('check_runs', []), key=lambda x: x['name']):
            print(f"  {cr['name']:35} : {cr['status']:12} -> {str(cr.get('conclusion'))}")

if __name__ == '__main__':
    main()
