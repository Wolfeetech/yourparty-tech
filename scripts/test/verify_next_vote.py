import requests
import pymongo
import os
import time

# 1. Simulate User Vote
print("Simulating User Vote...")
payload = {
    "song_id": "manual_verify_id",
    "mood_next": "euphoric"
}

try:
    response = requests.post("http://127.0.0.1:8000/vote-next-mood", json=payload)
    print(f"API Response: {response.status_code}")
    print(f"API Body: {response.text}")
except Exception as e:
    print(f"API Request Failed: {e}")
    exit(1)

# 2. Check Database Persistence
print("\nChecking MongoDB...")
try:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://192.168.178.29:27017/yourparty")
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    collection = db["mood_next_votes"]
    
    # Find the vote we just cast
    vote = collection.find_one({"song_id": "manual_verify_id", "mood_next": "euphoric"})
    
    if vote:
        print("✅ SUCCESS: Vote found in MongoDB!")
        print(f"Document: {vote}")
    else:
        print("❌ FAILURE: Vote NOT found in MongoDB.")
        
except Exception as e:
    print(f"Database Check Failed: {e}")
