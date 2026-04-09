
import requests
import json
from apps.api.secrets import AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

HEADERS = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

def list_playlists():
    url = f"{AZURACAST_API_URL}/station/{AZURACAST_STATION_ID}/playlists"
    try:
        resp = requests.get(url, headers=HEADERS, verify=False)
        resp.raise_for_status()
        playlists = resp.json()
        print(f"Found {len(playlists)} playlists:")
        for p in playlists:
            print(f"- {p['name']} (ID: {p['id']})")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")

if __name__ == "__main__":
    list_playlists()
