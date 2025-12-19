#!/usr/bin/env python3
"""Test if tracks collection properly joins with rating_events."""
from pymongo import MongoClient

c = MongoClient("mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017")
db = c.yourparty_radio

# Get song_ids from rating_events
rating_song_ids = list(db.rating_events.distinct("song_id"))[:10]
print(f"Sample song_ids from rating_events: {rating_song_ids[:5]}")

# Check if any exist in tracks
matches = 0
for sid in rating_song_ids:
    track = db.tracks.find_one({"song_id": sid})
    if track:
        matches += 1
        print(f"  FOUND: {sid} -> {track.get('metadata', {}).get('title', 'No title')}")
    else:
        print(f"  MISSING: {sid}")

print(f"\nMatches: {matches}/{len(rating_song_ids)}")
print(f"Total tracks in collection: {db.tracks.count_documents({})}")
c.close()
