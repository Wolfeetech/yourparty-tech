import requests
import sys
import os
import subprocess

# 1. Get Status to find current song
try:
    print(">>> 1. Fetching Status...")
    r = requests.get("http://localhost:8000/status")
    data = r.json()
    song = data['now_playing']['song']
    song_id = song['id']
    print(f"Current Song: {song['title']} (ID: {song_id})")
except Exception as e:
    print(f"FAILED to fetch status: {e}")
    sys.exit(1)

# 2. Rate the Song
try:
    print(f">>> 2. Submitting 5 Star Rating for {song['title']}...")
    payload = {
        "song_id": song_id,
        "rating": 5,
        "user_id": "auto_test_agent"
    }
    r = requests.post("http://localhost:8000/rate", json=payload)
    print(f"Rating Response: {r.text}")
    
    if r.status_code != 200:
        print("FAILED to submit rating")
        sys.exit(1)
except Exception as e:
    print(f"FAILED to submit rating: {e}")
    sys.exit(1)

# 3. Verify via API that rating sticks
try:
    print(">>> 3. Verifying Rating via API...")
    r = requests.get("http://localhost:8000/status")
    data = r.json()
    new_rating = data['now_playing']['song']['rating']
    print(f"New Rating Data: {new_rating}")
    
    if new_rating['total'] > 0:
        print("SUCCESS: Rating visible in API.")
    else:
        print("FAILURE: Rating NOT visible in API.")
except Exception as e:
    print(f"FAILED to verify rating: {e}")

# 4. Run Sync Script
try:
    print(">>> 4. Running ID3 Sync Script...")
    # Manual call using the same python env
    result = subprocess.run(
        ["/opt/radio-api/venv/bin/python", "/app/sync_ratings_to_id3.py"], 
        capture_output=True, 
        text=True
    )
    print("Sync Script Output:")
    print(result.stdout)
    if result.stderr:
        print("Sync Script Errors:")
        print(result.stderr)
        
    if "Success: 1" in result.stdout or "Sync Complete" in result.stdout:
         print("SUCCESS: Sync script executed seemingly correctly.")
    else:
         print("WARNING: Sync script might not have found the file or failed.")

except Exception as e:
    print(f"FAILED to run sync script: {e}")
