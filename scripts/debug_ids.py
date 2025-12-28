
import os
import sys
sys.path.append('/opt/radio-api')
from dotenv import load_dotenv
from apps.api.mongo_client import MongoDatabaseClient

load_dotenv('/opt/radio-api/.env')
db = MongoDatabaseClient(os.getenv("MONGO_URI"), database_name="yourparty").db

print("=== ID TYPE DEBUG ===")
sample = db.tracks.find_one({"azuracast_id": {"$exists": True}})
if sample:
    ac_id = sample.get('azuracast_id')
    print(f"Sample Track: {sample.get('title')}")
    print(f"AC_ID: {ac_id} (Type: {type(ac_id)})")
else:
    print("No tracks with azuracast_id found.")

print("\n=== MOOD DEBUG ===")
mood_sample = db.moods.find_one({})
if mood_sample:
    print(f"Sample Mood: {mood_sample}")
else:
    print("No moods found.")
