import requests
import json
import sys

BASE_URL = "https://yourparty.tech/wp-json/yourparty/v1"
SONG_ID = "a49998e617b05f526a3dd2d495304076"  # Friendly Fires - Essential

def test_rating():
    print(f"--- Testing Rating for {SONG_ID} ---")
    payload = {"song_id": SONG_ID, "rating": 5}
    try:
        resp = requests.post(f"{BASE_URL}/rate", json=payload, verify=False)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Rating Error: {e}")

def test_tagging():
    print(f"\n--- Testing Tagging for {SONG_ID} ---")
    # Matches mood-dialog.js: /vote-mood
    payload = {"song_id": SONG_ID, "mood_current": "euphoric", "title": "Test Title", "artist": "Test Artist"}
    try:
        resp = requests.post(f"{BASE_URL}/vote-mood", json=payload, verify=False)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Tagging Error: {e}")

if __name__ == "__main__":
    test_rating()
    test_tagging()

