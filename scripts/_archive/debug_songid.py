#!/usr/bin/env python3
"""Check song_ids in MongoDB and compare with AzuraCast format"""
from pymongo import MongoClient
import requests
import hashlib

MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017"
AZURACAST_URL = "https://192.168.178.210"
AZURACAST_API_KEY = "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c"

client = MongoClient(MONGO_URI)
db = client.yourparty

print("=== MongoDB song_ids ===")
for i, r in enumerate(db.ratings.find({}).limit(5)):
    print(f"  {i+1}. {r['_id']}")

print("\n=== AzuraCast Now Playing ===")
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
resp = requests.get(f"{AZURACAST_URL}/api/nowplaying/1", verify=False, timeout=10)
if resp.ok:
    data = resp.json()
    np = data.get("now_playing", {}).get("song", {})
    print(f"  AzuraCast song_id: {np.get('id')}")
    print(f"  Title: {np.get('title')}")
    print(f"  Artist: {np.get('artist')}")
    
    # Try to compute what our hash would be
    title = np.get('title', '')
    artist = np.get('artist', '')
    our_hash = hashlib.md5(f"{title}{artist}".encode('utf-8')).hexdigest()
    print(f"  Our computed hash: {our_hash}")
    print(f"  Match: {our_hash == np.get('id')}")
