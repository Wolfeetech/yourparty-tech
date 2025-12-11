from azuracast_client import AzuraCastClient
import json
import os

# Credentials (hardcoded for test as discovered)
AC_URL = "http://192.168.178.210"
AC_KEY = "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c"
STATION_ID = 1

def test():
    print(f"Connecting to {AC_URL}...")
    import requests
    headers = {
        "Authorization": f"Bearer {AC_KEY}",
        "Content-Type": "application/json"
    }
    
    # Check Playlists
    try:
        print("Checking Playlists...")
        resp = requests.get(f"{AC_URL}/api/station/{STATION_ID}/playlists", headers=headers, verify=False)
        print(f"Playlists Status: {resp.status_code}")
    except Exception as e:
        print(f"Playlist check error: {e}")

    # Check Media
    try:
        print("Checking Media...")
        resp = requests.get(f"{AC_URL}/api/station/{STATION_ID}/files", headers=headers, verify=False)
        print(f"Media Status: {resp.status_code}")
    except Exception as e:
         print(f"Media check error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    test()
