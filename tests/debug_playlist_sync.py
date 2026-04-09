#!/usr/bin/env python3
"""Debug playlist sync directly"""
import sys
sys.path.insert(0, '/opt/radio-api')
from mongo_client import MongoDatabaseClient  
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID
from azuracast_client import AzuraCastClient
from playlist_service import PlaylistService

mc = MongoDatabaseClient(MONGO_URI)
ac = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)

print("Testing get_tracks_for_playlist...")
for mood in ['Euphoric', 'Chill', 'Energy']:
    ids = mc.get_tracks_for_playlist(mood=mood, limit=10)
    print(f"  {mood}: {len(ids)} track IDs -> {ids[:5]}...")

print("\nTesting PlaylistService...")
ps = PlaylistService(mc, ac)
import asyncio

async def test_sync():
    results = await ps.sync_all_playlists()
    for r in results:
        print(f"  {r}")

asyncio.run(test_sync())
