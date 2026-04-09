import os
import requests
import sys
from pymongo import MongoClient
import time

# --- CONFIG ---
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/yourparty?authSource=admin"
API_URL = "http://localhost:8000"
HA_IP = "192.168.178.179"

def check(name, func):
    print(f"\n[CHECK] {name}...")
    try:
        if func():
            print(f"✅ PASS: {name}")
            return True
        else:
            print(f"❌ FAIL: {name}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {name} - {e}")
        return False

# 1. DATABASE INTEGRITY
def verify_mongo():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client["yourparty"]
    
    # Count tracks
    count = db.tracks.count_documents({})
    print(f"   -> Total Tracks: {count}")
    if count < 4000: return False
    
    # Check Smart Tags
    smart_count = db.tracks.count_documents({"genre": {"$nin": ["Unknown", "Music", ""]}})
    print(f"   -> Smart Tagged Tracks: {smart_count}")
    
    # Check Sample
    sample = db.tracks.find_one({"genre": "Tech House"})
    if sample:
        print(f"   -> Sample 'Tech House': {sample.get('title', 'Unknown Title')}")
        return True
    return False

# 2. API HEALTH
def verify_api():
    # Health/Root
    try:
        r = requests.get(f"{API_URL}/")
        print(f"   -> Root Status: {r.status_code}")
    except:
        pass # Root might not exist, checking specific endpoints
        
    # Track Metadata (The critical fix)
    # Using ID 999 (likely exists or returns valid empty)
    r = requests.get(f"{API_URL}/track-metadata?song_id=1")
    print(f"   -> /track-metadata Status: {r.status_code}")
    print(f"   -> Response: {r.text[:100]}")
    
    if r.status_code == 200:
        return True
    return False

# 3. HOME ASSISTANT CONNECTIVITY
def verify_ha():
    # Simple socket connect or ping logic via OS
    response = os.system(f"ping -c 1 -W 1 {HA_IP} > /dev/null 2>&1")
    if response == 0:
        print(f"   -> Ping {HA_IP}: SUCCESS")
        return True
    else:
        print(f"   -> Ping {HA_IP}: FAILED")
        return False

# 4. PLAYLIST COMPLIANCE
def verify_playlists():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client["yourparty"]
    
    # Check if we have tracks with mood assigned
    mood_count = db.tracks.count_documents({"mood": {"$in": ["Energy", "Euphoric", "Chill"]}})
    print(f"   -> Mood Tagged Tracks: {mood_count}")
    return mood_count > 0

def main():
    print("=== TRIPLE VERIFICATION PROTOCOL ===")
    results = [
        check("MongoDB Access & Smart Tags", verify_mongo),
        check("Radio API Endpoint (/track-metadata)", verify_api),
        check("Home Assistant Connectivity", verify_ha),
        check("Playlist/Mood Data Existence", verify_playlists)
    ]
    
    if all(results):
        print("\n🏆 ALL SYSTEMS GO! Verification Successful.")
        sys.exit(0)
    else:
        print("\n⚠️ SYSTEM ALERTS DETECTED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
