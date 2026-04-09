import requests
import json
import time
import random

API_BASE = "https://yourparty.tech/wp-json/yourparty/v1"
COOKIE = "wordpress_logged_in_..." # We will run this via python on the server which has direct access or simple auth if needed. 
# Actually, better to run this as a local script checking the API externally to prove it works from outside.
# But for simplicity and auth, I'll run it as a standalone python script on the API container or creating a python script that hits the local fastapi directly to prove persistence.

# Let's hit the FastAPI directly on port 8000 to verify the *backend* logic first.
API_INTERNAL = "http://localhost:8000"

def test_voting_logic():
    print("=== TESTING MOOD VOTING LOGIC ===")
    
    # 1. Pick a random test song ID
    song_id = f"test_song_{random.randint(1000, 9999)}"
    print(f"Test Song ID: {song_id}")
    
    # 2. Simulate Votes: 5x Chill, 2x Dark, 5x Energy
    votes = ["Chill"] * 5 + ["Dark"] * 2 + ["Energy"] * 5
    random.shuffle(votes)
    
    print(f"Simulating {len(votes)} votes: 5x Chill, 5x Energy, 2x Dark")
    
    for vote in votes:
        try:
            requests.post(f"{API_INTERNAL}/mood-tag", json={
                "song_id": song_id,
                "mood": vote,
                "station_id": 1
            })
            print(f"Voted: {vote}")
            time.sleep(0.1)
        except Exception as e:
            print(f"Vote failed: {e}")

    # 3. Fetch Result
    print("\nFetching Aggregated Moods...")
    try:
        res = requests.get(f"{API_INTERNAL}/moods?song_id={song_id}")
        data = res.json()
        
        print("\n--- RESULTS ---")
        print(json.dumps(data, indent=2))
        
        counts = data.get("mood_counts", {})
        top = data.get("top_mood")
        
        # Verification
        if counts.get("Chill") == 5 and counts.get("Dark") == 2 and counts.get("Energy") == 5:
            print("\nSUCCESS: All votes counted correctly.")
        else:
            print("\nFAILURE: Vote counts mismatch!")
            
        if top in ["Chill", "Energy"]: # Tie is possible
            print(f"Top Mood '{top}' is valid (tied leader).")
        else:
             print(f"FAILURE: Top mood '{top}' is unexpected.")
             
    except Exception as e:
        print(f"Fetch failed: {e}")

if __name__ == "__main__":
    test_voting_logic()
