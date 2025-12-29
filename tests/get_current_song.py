import requests
import json
import sys

try:
    resp = requests.get("https://yourparty.tech/wp-json/yourparty/v1/status?station_id=1", verify=False)
    data = resp.json()
    song = data.get('now_playing', {}).get('song', {})
    print(f"SONG_ID={song.get('id')}")
    print(f"TITLE={song.get('title')}")
    print(f"ARTIST={song.get('artist')}")
except Exception as e:
    print(f"ERROR: {e}")
