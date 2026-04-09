import sys
import os
import requests
import json
import time

# Add backend to path to import client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.api.config_secrets import AZURACAST_API_URL, AZURACAST_API_KEY
STATION_ID = 1

def cleanup_playlists():
    sys.stdout.reconfigure(encoding='utf-8')
    
    if not os.path.exists("playlists_audit.json"):
        print("Error: playlists_audit.json not found. Run audit first.")
        return

    with open("playlists_audit.json", "r", encoding="utf-8") as f:
        audit = json.load(f)

    headers = {'Authorization': f'Bearer {AZURACAST_API_KEY}'}
    base_url = f"{AZURACAST_API_URL}/station/{STATION_ID}/playlist"

    print(f"--- STARTING CLEANUP ---")
    deleted_count = 0
    
    for item in audit:
        if item.get("action") == "DELETE":
            pl_id = item["id"]
            name = item["name"]
            print(f"Deleting '{name}' (ID: {pl_id})...", end=" ")
            
            try:
                resp = requests.delete(f"{base_url}/{pl_id}", headers=headers)
                if resp.status_code in [204, 200]:
                    print("SUCCESS")
                    deleted_count += 1
                else:
                    print(f"FAILED ({resp.status_code})")
            except Exception as e:
                print(f"ERROR: {e}")
            
            time.sleep(0.5) # Be gentle

    print(f"\n--- CLEANUP COMPLETE ---")
    print(f"Deleted {deleted_count} playlists.")

if __name__ == "__main__":
    cleanup_playlists()
