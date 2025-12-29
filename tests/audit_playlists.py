import sys
import os
import requests
import json
from tabulate import tabulate

# Add backend to path to import client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.api.config_secrets import AZURACAST_API_URL, AZURACAST_API_KEY
STATION_ID = 1

def audit_playlists():
    sys.stdout.reconfigure(encoding='utf-8')
    # Direct Requests because AzuraCastClient might not have list_playlists yet or be async
    headers = {'Authorization': f'Bearer {AZURACAST_API_KEY}'}
    url = f"{AZURACAST_API_URL}/station/{STATION_ID}/playlists"
    
    print(f"Fetching playlists from {url}...")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return

    playlists = resp.json()
    
    # Valid/Protected Playlists
    PROTECTED_NAMES = ['default', 'General Rotation', 'Jingles', 'Station IDs']
    VALID_MOODS = ['energy', 'chill', 'euphoric', 'dark', 'melancholic', 'groovy', 'hypnotic', 'aggressive', 'trippy', 'warm', 'uplifting', 'deep', 'funky']
    
    report = []
    
    print(f"\n--- PLAYLIST AUDIT ---")
    for pl in playlists:
        name = pl['name']
        pl_id = pl['id']
        count = pl['num_songs']
        is_jingle = pl['is_jingle']
        
        status = "UNKNOWN"
        action = "KEEP"
        
        if name in PROTECTED_NAMES or is_jingle:
            status = "SYSTEM/PROTECTED"
            action = "KEEP"
        elif name.lower() in VALID_MOODS:
            status = "VALID MOOD"
            action = "KEEP" if count > 0 else "KEEP (Empty Mood)"
        elif "test" in name.lower() or count == 0:
             status = "CANDIDATE"
             action = "DELETE"
        else:
            status = "CUSTOM"
            action = "REVIEW"
            
        report.append({"id": pl_id, "name": name, "count": count, "status": status, "action": action})

    print(tabulate(report, headers="keys"))
    
    with open("playlists_audit.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    return playlists

if __name__ == "__main__":
    audit_playlists()
