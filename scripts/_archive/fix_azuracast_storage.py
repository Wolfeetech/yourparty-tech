
import os
import requests
import json
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load env manually since we are running as script
load_dotenv('/opt/radio-api/.env')

API_URL = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech").rstrip('/')
API_KEY = os.getenv("AZURACAST_API_KEY")

if not API_KEY:
    print("Error: AZURACAST_API_KEY not found in env")
    exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def main():
    print(f"Connecting to {API_URL}...")
    
    # 1. Get Storage Locations
    try:
        resp = requests.get(f"{API_URL}/api/admin/storage_locations", headers=HEADERS, verify=False)
        resp.raise_for_status()
        locations = resp.json()
    except Exception as e:
        print(f"Failed to fetch locations: {e}")
        exit(1)

    print(f"Found {len(locations)} storage locations.")
    target_id = None
    
    for loc in locations:
        print(f" - ID: {loc['id']}, Path: {loc['path']}, Adapter: {loc['adapter']}")
        # We want the one that is NOT radio_nas, and matches the 171GB metadata ideally.
        # Based on user info: /var/azuracast/music_storage
        if "music_storage" in loc['path'] and "radio_nas" not in loc['path']:
            target_id = loc['id']
            print(f"   -> MATCH! This looks like the correct storage.")
    
    if not target_id:
        print("Could not find a storage location with 'music_storage' that matches criteria.")
        exit(1)

    # 2. Update Station 1
    print(f"Updating Station 1 to use Storage ID {target_id}...")
    
    try:
        st_resp = requests.get(f"{API_URL}/api/admin/station/1", headers=HEADERS, verify=False)
        st_resp.raise_for_status()
        station_data = st_resp.json()
        
        current_loc = station_data.get('media_storage_location_id')
        print(f"Current Station Storage ID: {current_loc}")
        
        if current_loc == target_id:
            print("Station is already using the correct storage ID. Nothing to do.")
        else:
            station_data['media_storage_location_id'] = target_id
            
            # Update
            update_resp = requests.put(f"{API_URL}/api/admin/station/1", headers=HEADERS, json=station_data, verify=False)
            update_resp.raise_for_status()
            print("✅ Station Updated Successfully!")
            
    except Exception as e:
        print(f"Failed to update station: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response: {e.response.text}")
        exit(1)

if __name__ == "__main__":
    main()
