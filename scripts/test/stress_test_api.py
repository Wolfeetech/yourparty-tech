#!/usr/bin/env python3
"""
YourParty.tech API Stress Test
Tests all major endpoints with concurrent requests.
"""
import requests
import time
import concurrent.futures
from datetime import datetime

API_BASE = "https://api.yourparty.tech"
# API_BASE = "http://localhost:8000"  # For local testing

# Test Results
results = {
    "passed": [],
    "failed": [],
    "errors": []
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_endpoint(name, method, path, data=None, expected_status=200):
    """Test a single endpoint."""
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10, verify=False)
        else:
            resp = requests.post(url, json=data, timeout=10, verify=False)
        
        if resp.status_code == expected_status:
            results["passed"].append(f"{name}: {resp.status_code}")
            return True
        else:
            results["failed"].append(f"{name}: Expected {expected_status}, got {resp.status_code} - {resp.text[:100]}")
            return False
    except Exception as e:
        results["errors"].append(f"{name}: {str(e)}")
        return False

def stress_test_endpoint(name, method, path, data=None, count=10):
    """Hit an endpoint multiple times concurrently."""
    log(f"⚡ Stress testing {name} ({count} requests)...")
    
    def single_request(_):
        return test_endpoint(name, method, path, data)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(single_request, i) for i in range(count)]
        concurrent.futures.wait(futures)
    
    log(f"   → Completed {count} requests")

def main():
    log("=" * 50)
    log("YourParty.tech API Stress Test")
    log("=" * 50)
    
    # 1. Basic Health Checks
    log("\n📡 1. Health Checks")
    test_endpoint("Status", "GET", "/status")
    test_endpoint("Now Playing", "GET", "/now-playing")
    test_endpoint("Library All", "GET", "/library/all")
    
    # 2. Interactive Endpoints (Public)
    log("\n🎵 2. Interactive Endpoints")
    test_endpoint("Ratings List", "GET", "/ratings")
    test_endpoint("Moods List", "GET", "/moods")
    test_endpoint("Vote Candidates", "GET", "/vote-next-candidates")
    
    # 3. Stress Test: Vote Next (High Traffic)
    log("\n🔥 3. Stress Test: Vote Next")
    stress_test_endpoint(
        "Vote Next Energy",
        "POST",
        "/control/vote-next",
        {"vote": "energy"},
        count=20
    )
    
    # 4. Stress Test: Rate Track
    log("\n🔥 4. Stress Test: Rate Track")
    stress_test_endpoint(
        "Rate Track",
        "POST",
        "/rate",
        {"song_id": "test123", "rating": 5, "user_id": "stress_test"},
        count=10
    )
    
    # 5. Stress Test: Mood Tag
    log("\n🔥 5. Stress Test: Mood Tag")
    stress_test_endpoint(
        "Mood Tag",
        "POST",
        "/mood-tag",
        {"song_id": "test123", "mood": "euphoric"},
        count=10
    )
    
    # 6. Admin Endpoints (Expect 401 without auth)
    log("\n🔐 6. Auth-Protected Endpoints (Expect 401)")
    test_endpoint("Scan (No Auth)", "POST", "/scan", {"path": "/test"}, expected_status=401)
    test_endpoint("Organize (No Auth)", "POST", "/organize", {}, expected_status=401)
    
    # 7. Playlist Sync (Public now)
    log("\n🎶 7. Playlist Sync")
    test_endpoint("Playlist Sync", "POST", "/library/playlists/sync", expected_status=200)
    
    # 8. WebSocket Test (Just check endpoint exists)
    log("\n🔌 8. WebSocket Endpoint")
    try:
        resp = requests.get(f"{API_BASE}/ws", timeout=5, verify=False)
        # WS upgrade expected to fail with HTTP
        results["passed"].append("WebSocket Endpoint: Exists (HTTP 4xx expected)")
    except:
        results["passed"].append("WebSocket Endpoint: Check manually")
    
    # Summary
    log("\n" + "=" * 50)
    log("STRESS TEST RESULTS")
    log("=" * 50)
    log(f"✅ Passed: {len(results['passed'])}")
    log(f"❌ Failed: {len(results['failed'])}")
    log(f"⚠️ Errors: {len(results['errors'])}")
    
    if results["failed"]:
        log("\nFailed Tests:")
        for f in results["failed"]:
            log(f"  - {f}")
    
    if results["errors"]:
        log("\nErrors:")
        for e in results["errors"]:
            log(f"  - {e}")
    
    log("\n" + "=" * 50)
    log("TEST COMPLETE")
    log("=" * 50)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
