#!/usr/bin/env python3
"""
Auto-assign Moods based on Genre (ID3 tag)
Quick Fix to populate mood field for playlist automation
"""
import sys
sys.path.insert(0, '/opt/radio-api')
from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

# Genre -> Mood mapping
GENRE_MOOD_MAP = {
    # High Energy
    "drum and bass": "Energy",
    "drum & bass": "Energy",
    "dubstep": "Energy",
    "hardstyle": "Energy",
    "hardcore": "Energy",
    "bass house": "Energy",
    "breaks": "Energy",
    "breakbeat": "Energy",
    
    # Euphoric / Peak
    "trance": "Euphoric",
    "progressive house": "Euphoric",
    "electro house": "Euphoric",
    "big room": "Euphoric",
    "dance": "Euphoric",
    "edm": "Euphoric",
    "house": "Euphoric",
    
    # Chill / Deep
    "deep house": "Chill",
    "lo-fi": "Chill",
    "lounge": "Chill",
    "ambient": "Chill",
    "chillout": "Chill",
    "downtempo": "Chill",
    "afro house": "Chill",
    "melodic house": "Chill",
    "organic house": "Chill",
}

mc = MongoDatabaseClient(MONGO_URI)

updated = 0
no_genre = 0
unknown_genre = 0

cursor = mc.tracks_collection.find({'mood': {'$exists': False}})

for track in cursor:
    metadata = track.get('metadata', {})
    genre = metadata.get('genre', '').lower().strip()
    
    if not genre:
        no_genre += 1
        continue
    
    # Find matching mood
    mood = None
    for g, m in GENRE_MOOD_MAP.items():
        if g in genre:
            mood = m
            break
    
    if mood:
        mc.tracks_collection.update_one(
            {'_id': track['_id']},
            {'$set': {'mood': mood}}
        )
        updated += 1
    else:
        unknown_genre += 1

print(f"✅ Updated: {updated} tracks with mood")
print(f"⚠️  No genre tag: {no_genre}")
print(f"⚠️  Unknown genre: {unknown_genre}")

# Verify
moods = mc.tracks_collection.aggregate([
    {'$group': {'_id': '$mood', 'count': {'$sum': 1}}}
])
print("\nMood Distribution:")
for m in moods:
    print(f"  {m['_id']}: {m['count']}")
