from mongo_client import MongoDatabaseClient
import os

print("--- MongoDB Diagnostics ---")
try:
    # Use environment variables if set, otherwise default
    db = MongoDatabaseClient(
        connection_string=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        database_name=os.getenv("MONGO_DB", "radio_ratings")
    )
    
    track_count = db.tracks_collection.count_documents({})
    rating_count = db.ratings_collection.count_documents({})
    
    print(f"Tracks Collection: {track_count}")
    print(f"Ratings Collection: {rating_count}")
    
    if track_count > 0:
        print("\nSample Track:")
        print(db.tracks_collection.find_one())
    else:
        print("\n[!] Tracks collection is EMPTY.")
        
    print("\n---------------------------")
    
except Exception as e:
    print(f"Error connecting to DB: {e}")
