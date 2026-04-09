#!/usr/bin/env python3
"""Check MongoDB Track Statistics"""
import sys
sys.path.insert(0, '/opt/radio-api')
from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

mc = MongoDatabaseClient(MONGO_URI)

total = mc.tracks_collection.count_documents({})
with_azura = mc.tracks_collection.count_documents({'azuracast_id': {'$exists': True, '$ne': None}})
with_mood = mc.tracks_collection.count_documents({'mood': {'$exists': True, '$ne': None}})

print(f"Total tracks: {total}")
print(f"With AzuraCast ID: {with_azura}")
print(f"With Mood: {with_mood}")

# Sample moods
moods = mc.tracks_collection.distinct('mood')
print(f"Distinct moods: {moods[:10] if moods else 'None'}")

# Sample track with azuracast_id
sample = mc.tracks_collection.find_one({'azuracast_id': {'$exists': True}})
if sample:
    print(f"\nSample track: {sample.get('metadata', {}).get('title', 'N/A')}")
    print(f"  Mood: {sample.get('mood', 'NOT SET')}")
    print(f"  AzuraCast ID: {sample.get('azuracast_id')}")
