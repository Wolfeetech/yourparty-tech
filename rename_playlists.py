import os
import asyncio
import httpx
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv('/opt/radio-api/.env')

AZURA_URL = os.getenv('AZURACAST_URL')
AZURA_KEY = os.getenv('AZURACAST_API_KEY')
STATION_ID = 1

# Mapping: ID -> New Name
RENAME_MAP = {
    39: "High Voltage",    # Energetic
    41: "Pocket Logic",    # Groovy
    43: "Nocturnals",      # Dark
    42: "Slow Burn",       # Warm -> Chill
    # Euphoric -> Starlight (likely doesn't exist yet, will accept default creation or I can create it)
}

async def rename_playlist(client, p_id, new_name):
    # 1. Get current details
    url = f"{AZURA_URL}/api/station/{STATION_ID}/playlist/{p_id}"
    try:
        resp = await client.get(url, follow_redirects=True)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch playlist {p_id}: {resp.status_code}")
            return
        
        data = resp.json()
        old_name = data.get('name')
        
        if old_name == new_name:
            print(f"✅ Playlist {p_id} is already '{new_name}'")
            return

        # 2. Construct Minimal Payload
        # Avod sending back complex relations that cause 500s
        payload = {
            "name": new_name,
            "weight": data.get("weight", 3),
            "type": data.get("type", "default"),
            "is_enabled": data.get("is_enabled", True),
            "include_in_requests": data.get("include_in_requests", True),
             # "source": "songs" # vital for some versions
        }
        
        # 3. PUT update
        logger.info(f"Sending payload for {p_id}: {payload}")
        resp = await client.put(url, json=payload, follow_redirects=True)
        if resp.status_code == 200:
             print(f"✅ Renamed {p_id}: '{old_name}' -> '{new_name}'")
        else:
             print(f"❌ Failed to rename {p_id}: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"❌ Exception for {p_id}: {e}")

async def main():
    if not AZURA_URL or not AZURA_KEY:
        print("❌ Missing Env Vars")
        return

    headers = {'Authorization': f'Bearer {AZURA_KEY}'}
    async with httpx.AsyncClient(verify=False, headers=headers) as client:
        print("--- RENAMING PLAYLISTS ---")
        for p_id, new_name in RENAME_MAP.items():
            await rename_playlist(client, p_id, new_name)
            
        print("\n--- Creating 'Starlight' if missing ---")
        # Check if Starlight exists
        resp = await client.get(f"{AZURA_URL}/api/station/{STATION_ID}/playlists", follow_redirects=True)
        playlists = resp.json()
        starlight = next((p for p in playlists if p['name'] == 'Starlight'), None)
        
        if not starlight:
            print("creating Starlight...")
            # Create it
            payload = {
                "name": "Starlight",
                "weight": 5,
                "is_enabled": True,
                "type": "default",
                "include_in_requests": True
            }
            res = await client.post(f"{AZURA_URL}/api/station/{STATION_ID}/playlists", json=payload, follow_redirects=True)
            if res.status_code == 200:
                print("✅ Created 'Starlight'")
            else:
                print(f"❌ Failed to create Starlight: {res.text}")
        else:
            print("✅ 'Starlight' already exists")

if __name__ == "__main__":
    asyncio.run(main())
