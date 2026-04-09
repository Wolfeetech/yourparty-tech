#!/usr/bin/env python3
"""Debug playlist query"""
import sys
sys.path.insert(0, '/opt/radio-api')
from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

mc = MongoDatabaseClient(MONGO_URI)

# Check tracks with BOTH mood AND azuracast_id
for mood in ['Euphoric', 'Chill', 'Energy']:
    count = mc.tracks_collection.count_documents({
        'mood': mood,
        'azuracast_id': {'$exists': True, '$ne': None}
    })
    print(f"{mood}: {count} tracks with azuracast_id")

# Sample
sample = mc.tracks_collection.find_one({
    'mood': 'Euphoric',
    'azuracast_id': {'$exists': True}
})
if sample:
    print(f"\nSample Euphoric track:")
    print(f"  Title: {sample.get('metadata', {}).get('title', 'N/A')}")
    print(f"  AzuraCast ID: {sample.get('azuracast_id')}")
    print(f"  Mood: {sample.get('mood')}")
