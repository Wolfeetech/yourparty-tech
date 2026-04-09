import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

url = "http://localhost:8000/mood-tag"
payload = {
    "song_id": "test_tag_123",
    "mood": "Euphoric",
    "station_id": 1,
    "title": "Debug Test Track",
    "artist": "Debug Assistant"
}

try:
    print(f"Sending POST to {url} with payload: {payload}")
    res = requests.post(url, json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    if res.status_code == 200:
        print("✅ SUCCESS: Mood Tag Accepted")
    else:
        print("❌ FAILED: API Error")
        
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
