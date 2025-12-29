#!/usr/bin/env python3
"""
Professional AzuraCast Station Startup Script
Triggers media library scan and starts broadcasting
"""
import requests
import time
import sys
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

AZURACAST_BASE = "https://192.168.178.210"
API_KEY = "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c"
STATION_ID = 1

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def api_call(method, endpoint, **kwargs):
    url = f"{AZURACAST_BASE}{endpoint}"
    kwargs['verify'] = False
    kwargs['headers'] = headers
    kwargs['timeout'] = 30
    
    try:
        resp = requests.request(method, url, **kwargs)
        print(f"[{method}] {endpoint} -> {resp.status_code}")
        return resp
    except Exception as e:
        print(f"ERROR: {e}")
        return None

print("="*60)
print("AzuraCast Station Startup - Professional Mode")
print("="*60)

# Step 1: Get station info
print("\n[1/4] Getting station status...")
resp = api_call("GET", f"/api/station/{STATION_ID}")
if resp and resp.status_code == 200:
    data = resp.json()
    print(f"  Station: {data.get('name', 'Unknown')}")
    print(f"  Backend Running: {data.get('backend_running', False)}")
    print(f"  Frontend Running: {data.get('frontend_running', False)}")
else:
    print("  ⚠️  Could not get station status")

# Step 2: Trigger media rescan
print("\n[2/4] Triggering media library scan...")
# Try the files/rescan endpoint
resp = api_call("POST", f"/api/station/{STATION_ID}/files/rescan")
if resp and resp.status_code in [200, 202]:
    print("  ✅ Media scan triggered successfully")
elif resp:
    print(f"  ⚠️  Rescan response: {resp.text[:200]}")
    # Try alternative endpoint
    print("  Trying alternative: reindex...")
    resp = api_call("POST", f"/api/station/{STATION_ID}/reindex")
    if resp and resp.status_code in [200, 202]:
        print("  ✅ Reindex triggered")

# Step 3: Start backend (Liquidsoap/AutoDJ)
print("\n[3/4] Starting backend (AutoDJ)...")
resp = api_call("POST", f"/api/station/{STATION_ID}/backend/start")
if resp and resp.status_code in [200, 204]:
    print("  ✅ Backend started")
elif resp:
    print(f"  ⚠️  Backend response: {resp.text[:200]}")

# Step 4: Start frontend (Icecast/Streaming)
print("\n[4/4] Starting frontend (Streaming)...")
resp = api_call("POST", f"/api/station/{STATION_ID}/frontend/start")
if resp and resp.status_code in [200, 204]:
    print("  ✅ Frontend started")
elif resp:
    print(f"  ⚠️  Frontend response: {resp.text[:200]}")

# Verification
print("\n" + "="*60)
print("Waiting 10 seconds for station to initialize...")
print("="*60)
time.sleep(10)

resp = api_call("GET", f"/api/nowplaying/{STATION_ID}")
if resp and resp.status_code == 200:
    data = resp.json()
    song = data.get('now_playing', {}).get('song', {})
    print(f"\n🎵 Now Playing: {song.get('title', 'N/A')} - {song.get('artist', 'N/A')}")
    print(f"   Listeners: {data.get('listeners', {}).get('current', 0)}")
    
    if song.get('title') == 'Station Offline':
        print("\n⚠️  Station still offline. Media scan may take time.")
        print("   Check back in 5-10 minutes.")
    else:
        print("\n✅ SUCCESS! Station is broadcasting!")
else:
    print("\n⚠️  Could not verify station status")

print("\n" + "="*60)
print("Script complete.")
print("="*60)
