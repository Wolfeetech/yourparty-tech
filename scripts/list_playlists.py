import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load env from the standard location
load_dotenv('/opt/radio-api/.env')

AZURA_URL = os.getenv('AZURACAST_URL')
AZURA_KEY = os.getenv('AZURACAST_API_KEY')
STATION_ID = 1

async def main():
    if not AZURA_URL or not AZURA_KEY:
        print("❌ Missing Env Vars")
        return

    headers = {'Authorization': f'Bearer {AZURA_KEY}'}
    async with httpx.AsyncClient(verify=False) as client:
        # Get Playlists
        resp = await client.get(f"{AZURA_URL}/api/station/{STATION_ID}/playlists", headers=headers, follow_redirects=True)
        if resp.status_code != 200:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            return
        
        playlists = resp.json()
        print(f"\n--- AZURACAST PLAYLISTS ({len(playlists)}) ---\n")
        print(f"{'ID':<5} {'NAME':<30} {'WEIGHT':<8} {'TYPE':<10}")
        print("-" * 60)
        
        for pl in playlists:
            p_id = pl.get('id')
            p_name = pl.get('name')
            p_weight = pl.get('weight')
            p_type = pl.get('type') # 'default' usually means rotation
            print(f"{p_id:<5} {p_name:<30} {p_weight:<8} {p_type:<10}")

if __name__ == "__main__":
    asyncio.run(main())
