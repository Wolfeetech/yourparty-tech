from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv("/opt/radio-api/.env")

uri = os.getenv("MONGO_URI")
if not uri:
    print("ERROR: MONGO_URI not found in .env")
    exit(1)

client = MongoClient(uri)
db = client.get_database()

print("=== Collections in DB ===")
print(db.list_collection_names())

print("\n=== moods Collection Sample ===")
moods_coll = db["moods"]
count = moods_coll.count_documents({})
print(f"Total moods: {count}")
for m in moods_coll.find().limit(5):
    print(f"  song_id={m.get('song_id')}, mood={m.get('mood')}")

print("\n=== mood_next_votes Sample ===")
votes_coll = db["mood_next_votes"]
count2 = votes_coll.count_documents({})
print(f"Total votes: {count2}")
for v in votes_coll.find().sort("timestamp", -1).limit(5):
    print(f"  mood_next={v.get('mood_next')}, song_id={v.get('song_id')}")
