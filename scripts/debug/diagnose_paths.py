#!/usr/bin/env python3
"""Diagnostic to compare AzuraCast and MongoDB paths."""
import os
import sys
import asyncio

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

async def diagnose():
    mongo = MongoDatabaseClient(MONGO_URI)
    azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
    
    # Sample MongoDB paths
    print("=== MongoDB Sample Paths ===")
    for doc in mongo.tracks_collection.find().limit(3):
        fp = doc.get('file_path', 'N/A')
        sid = doc.get('song_id', 'N/A')
        print(f"  file_path: {fp}")
        print(f"  song_id: {sid}")
        print(f"  Normalized: {mongo.normalize_path(fp)}")
        print()
    
    # Sample AzuraCast paths
    print("=== AzuraCast Sample Paths ===")
    media = await azura.get_station_media()
    for m in media[:3]:
        print(f"  path: {m.get('path')}")
        print(f"  id: {m.get('id')}")
        print(f"  song_id: {m.get('song_id')}")
        print()
    
    # Check if any song_ids match
    print("=== Song ID Match Test ===")
    az_song_ids = {m.get('song_id') for m in media if m.get('song_id')}
    mongo_song_ids = set()
    for doc in mongo.tracks_collection.find({}, {'song_id': 1}):
        if doc.get('song_id'):
            mongo_song_ids.add(doc['song_id'])
    
    overlap = az_song_ids & mongo_song_ids
    print(f"AzuraCast song_ids: {len(az_song_ids)}")
    print(f"MongoDB song_ids: {len(mongo_song_ids)}")
    print(f"Matching song_ids: {len(overlap)}")
    
    if overlap:
        print(f"Sample match: {list(overlap)[:3]}")

if __name__ == "__main__":
    asyncio.run(diagnose())
