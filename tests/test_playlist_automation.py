#!/usr/bin/env python3
"""
Test YourParty Radio Playlist Automation
Tests:  - AzuraCast ID sync with MongoDB
 - Mood playlist automatic generation
"""
import requests
import json

API_BASE = "https://yourparty.tech/api"

print("="*70)
print("YourParty Radio - Playlist Automation Test") 
print("="*70)

# Step 1: Login
print("\n[1/3] Authenticating...")
resp = requests.post(f"{API_BASE}/token", data={
    "username": "admin",
    "password": "admin"
})
if resp.status_code != 200:
    print(f"❌ Login failed: {resp.text}")
    exit(1)
    
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Authenticated")

# Step 2: Sync AzuraCast IDs
print("\n[2/3] Syncing AzuraCast Media IDs with MongoDB...")
resp = requests.post(f"{API_BASE}/library/sync-ids", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ Synced {data.get('synced_count', 0)} tracks")
else:
    print(f"⚠️  Sync response: {resp.status_code} - {resp.text[:200]}")

# Step 3: Trigger Playlist Sync
print("\n[3/3] Generating Mood Playlists...")
resp = requests.post(f"{API_BASE}/library/playlists/sync")
if resp.status_code == 200:
    data = resp.json()
    print("\n📋 Playlist Results:")
    for result in data.get("results", []):
        status = "✅" if result.get("success") else "❌"
        count = result.get("count", 0)
        playlist = result.get("playlist", "Unknown")
        message = result.get("message", "")
        print(f"  {status} {playlist}: {count} tracks {f'({message})' if message else ''}")
else:
    print(f"⚠️  Playlist sync response: {resp.status_code} - {resp.text[:200]}")

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
