from pymongo import MongoClient
import time
import datetime
import sys

# Credentials from main.py
MONGO_USER = "root"
MONGO_PASS = "4f5cd00532af49b5941d6f6385b2e0bf"
MONGO_HOST = "192.168.178.222" # LXC 202 IP
MONGO_PORT = "27017"

try:
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
    client = MongoClient(uri)
    db = client["yourparty"] # Correct DB Name

    print("--- LATEST RATING ---")
    # Check if collection has data
    if db.ratings.count_documents({}) == 0:
         print("No ratings found.")
    else:
        rating = db.ratings.find_one(sort=[("updated_at", -1)]) # Use updated_at usually? Or timestamp?
        # main.py code: "updated_at": int(time.time())
        # Let's check keys.
        if rating:
            ts = rating.get('updated_at', 0)
            age = time.time() - ts
            print(f"ID: {rating.get('_id')} | Avg: {rating.get('average')} | Total: {rating.get('total')} | Age: {age:.1f}s")
        else:
            print("None")

    print("\n--- LATEST MOOD UPDATE ---")
    if db.moods.count_documents({}) > 0:
        mood = db.moods.find_one(sort=[("last_mood_update", -1)])
        if mood:
            ts = mood.get('last_mood_update', 0)
            age = time.time() - ts
            print(f"ID: {mood.get('_id')} | TopMood: {mood.get('top_mood')} | Age: {age:.1f}s")
        else:
            print("None")
    else:
        print("No moods found.")

    print("\n--- LATEST VIBE VOTE ---")
    col_name = "steering_votes"
    if col_name in db.list_collection_names():
        vibe = db[col_name].find_one(sort=[("timestamp", -1)])
        if vibe:
            ts = vibe.get('timestamp', 0)
            age = time.time() - ts
            print(f"Vote: {vibe.get('vote')} | IP: {vibe.get('ip')} | Age: {age:.1f}s")
        else:
            print("None")
    else:
        print(f"No {col_name} collection found.")

except Exception as e:
    print(f"Error: {e}")
