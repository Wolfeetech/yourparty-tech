
import pymongo
from datetime import datetime

uri = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"
client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
db = client.yourparty_radio

print("--- UNKNOWN_RATINGS_INSPECTION ---")
ratings_cursor = db.ratings.find({})

count = 0
for r in ratings_cursor:
    title = r.get("title", "")
    artist = r.get("artist", "")
    metadata = r.get("metadata", {}) # sometimes it's here?
    
    # Check top level or metadata
    t_check = title or metadata.get("title")
    a_check = artist or metadata.get("artist")
    
    if not t_check or t_check == "Unknown" or not a_check:
        print(f"Deleting Junk Record: {r.get('_id')}")
        db.ratings.delete_one({"_id": r.get("_id")})
        count += 1

print(f"Total Deleted: {count}")

