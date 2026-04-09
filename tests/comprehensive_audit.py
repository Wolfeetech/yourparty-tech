#!/usr/bin/env python3
import sys
import os
import asyncio
import httpx
import time
from datetime import datetime

# Adjust path
sys.path.insert(0, '/opt/radio-api')

# ANSI Colors for Output
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_pass(msg):
    print(f"{Colors.OKGREEN}[PASS]{Colors.ENDC} {msg}")

def print_fail(msg, error=""):
    print(f"{Colors.FAIL}[FAIL]{Colors.ENDC} {msg} {Colors.WARNING}{error}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BOLD}[INFO]{Colors.ENDC} {msg}")

async def check_service_health():
    print(f"\n{Colors.HEADER}=== 1. Service Health Checks ==={Colors.ENDC}")
    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
        # Radio API
        try:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                print_pass("Radio API Health Check (http://localhost:8000/health)")
            else:
                print_fail(f"Radio API Health Check returned {resp.status_code}")
        except Exception as e:
            print_fail("Radio API Connection Refused (Is service running?)", str(e))

        # AzuraCast API
        try:
            # Using internal IP and HTTPS (with verify=False)
            url = "https://192.168.178.210/api" 
            resp = await client.get(url)
            if resp.status_code in [200, 401, 302, 307]: # 401 means reachable but auth required
                 print_pass(f"AzuraCast API Reachable ({url})")
            else:
                 print_fail(f"AzuraCast API returned {resp.status_code}")
        except Exception as e:
            print_fail("AzuraCast API Unreachable", str(e))

async def check_data_integrity():
    print(f"\n{Colors.HEADER}=== 2. Data Integrity Checks ==={Colors.ENDC}")
    try:
        from mongo_client import MongoDatabaseClient
        from config_secrets import MONGO_URI
        mc = MongoDatabaseClient(MONGO_URI)
        
        # Tracks
        count = mc.tracks_collection.count_documents({})
        if count > 0:
            print_pass(f"MongoDB Tracks Valid: {count} tracks")
        else:
            print_fail("MongoDB Tracks Empty")

        # Moods
        tagged = mc.tracks_collection.count_documents({'mood': {'$exists': True}})
        if tagged > 0:
            print_pass(f"Mood Tagged Tracks: {tagged} (Ready for curation)")
        else:
            print_fail("No tracks have Mood tags (Playlist automation impossible)")
            
        # AzuraCast IDs
        synced = mc.tracks_collection.count_documents({'azuracast_id': {'$exists': True}})
        if synced > 0:
             print_pass(f"AzuraCast Linked Tracks: {synced}")
        else:
             print_fail("No tracks have AzuraCast IDs (Sync required)")

    except Exception as e:
        print_fail("Database Integrity Check Failed", str(e))

async def check_playlist_automation():
    print(f"\n{Colors.HEADER}=== 3. Playlist Automation Test ==={Colors.ENDC}")
    async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
        try:
            print_info("Triggering Playlist Sync (POST /library/playlists/sync)...")
            start = time.time()
            resp = await client.post("http://localhost:8000/library/playlists/sync")
            duration = time.time() - start
            
            if resp.status_code == 200:
                print_pass(f"Sync Request Completed in {duration:.2f}s")
                data = resp.json()
                results = data.get('results', [])
                
                total_tracks = 0
                failures = 0
                
                for r in results:
                    name = r.get('playlist')
                    count = r.get('count', 0)
                    success = r.get('success')
                    
                    if success:
                        if count > 0:
                             print_pass(f"Playlist '{name}' updated with {count} tracks")
                             total_tracks += count
                        else:
                             # Warning level
                             print_fail(f"Playlist '{name}' updated but has 0 tracks (Check Moods/Matching)", r.get('message'))
                             failures += 1
                    else:
                        print_fail(f"Playlist '{name}' Sync Failed", r.get('error'))
                        failures += 1
                
                if total_tracks > 0:
                    print_pass(f"SUCCESS: {total_tracks} total tracks synced/curated via Automation")
                else:
                    print_fail("CRITICAL: Playlist Automation ran but curated ZERO tracks.")
                    
            else:
                print_fail(f"API Endpoint returned {resp.status_code}", resp.text)
                
        except Exception as e:
             print_fail("Playlist Sync Endpoint Unreachable", str(e))

async def main():
    print(f"{Colors.BOLD}--- YOURPARTY.TECH SYSTEM AUDIT ---{Colors.ENDC}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    await check_service_health()
    await check_data_integrity()
    try:
        await check_playlist_automation()
    except Exception as e:
        print_fail("Automation Test Suite Crashed", str(e))
    
    print(f"\n{Colors.BOLD}--- AUDIT END ---{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())
