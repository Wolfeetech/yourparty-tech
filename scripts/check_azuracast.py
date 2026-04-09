#!/usr/bin/env python3
"""
Quick AzuraCast Status Check and Station Restart
"""
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE = "https://192.168.178.210"

print("="*60)
print("AzuraCast Quick Status Check")
print("="*60)

# Check nowplaying
resp = requests.get(f"{BASE}/api/nowplaying/1", verify=False, timeout=10)
if resp.status_code == 200:
    data = resp.json()
    song = data['now_playing']['song']
    listeners = data['listeners']['current']
    
    print(f"\n🎵 Now Playing: {song['title']} - {song['artist']}")
    print(f"   👥 Listeners: {listeners}")
    
    if song['title'] == 'Station Offline':
        print("\n❌ Station is OFFLINE")
    else:
        print("\n✅ Station is BROADCASTING!")
        
    # Check backend/frontend status
    station = data.get('station', {})
    print(f"\n📡 Station: {station.get('name')}")
    print(f"   Backendmodule: {station.get('backend')}")  
    print(f"   Frontend: {station.get('frontend')}")
else:
    print(f"\n❌ Cannot reach AzuraCast API: {resp.status_code}")

print("\n" + "="*60)
