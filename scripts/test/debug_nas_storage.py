
import logging
import requests
from apps.api.config_secrets import AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugNAS")

def debug_nas():
    headers = {
        "Authorization": f"Bearer {AZURACAST_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Get Storage Locations to find the new one
    try:
        resp = requests.get(f"{AZURACAST_API_URL}/admin/storage_locations", headers=headers, verify=False)
        locations = resp.json()
        
        nas_loc = None
        for loc in locations:
            # We look for the one with the NAS path
            if "radio_nas" in loc.get("path", ""):
                nas_loc = loc
                break
        
        if not nas_loc:
            logger.error("Could not find NAS storage location in API response.")
            # print all paths
            for loc in locations:
                logger.info(f"Found Location: {loc.get('path')} (ID: {loc.get('id')})")
            return

        logger.info(f"Found NAS Location: {nas_loc['path']} (ID: {nas_loc['id']})")
        
        # 2. List files in this location
        # Endpoint: /admin/storage_locations/{id}/files?path=
        # Or station specific? usually storage locations have a file browser endpoint
        # Use the Station Files endpoint but filtered?
        # Actually /station/{id}/files uses the assigned storage.
        
        logger.info("Listing files via Station API (since it is assigned)...")
        files_url = f"{AZURACAST_API_URL}/station/{AZURACAST_STATION_ID}/files"
        files_resp = requests.get(files_url, headers=headers, verify=False)
        files = files_resp.json()
        
        if isinstance(files, dict) and 'message' in files:
             logger.error(f"Error listing files: {files['message']}")
             return

        file_list = files if isinstance(files, list) else files.get('rows', [])
        logger.info(f"Root Files: {len(file_list)}")
        for f in file_list:
            logger.info(f" - [Root] {f.get('path')} ({f.get('type')})")

        # Try specific folder "yourparty_Libary"
        logger.info("Listing 'yourparty_Libary'...")
        path_url = f"{files_url}?path=yourparty_Libary"
        sub_resp = requests.get(path_url, headers=headers, verify=False)
        sub_list = sub_resp.json()
        rows = sub_list if isinstance(sub_list, list) else sub_list.get('rows', [])
        logger.info(f"Subfolder Files: {len(rows)}")
        for f in rows[:10]:
             logger.info(f" - [Sub] {f.get('path')}")
            
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    debug_nas()
