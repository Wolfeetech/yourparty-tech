
import os
import asyncio
from dotenv import load_dotenv
from azuracast_client import AzuraCastClient

load_dotenv('/srv/radioapi/.env')

async def main():
    ac_url = os.getenv("AZURACAST_URL")
    ac_key = os.getenv("AZURACAST_API_KEY")
    print(f"Connecting to {ac_url}...")
    
    client = AzuraCastClient(ac_url, ac_key, 1)
    
    # Test Get
    print("Fetching playlists...")
    playlists = await client.get_playlists()
    print(f"Found {len(playlists)} playlists.")
    for p in playlists:
        print(f" - {p['id']}: {p['name']} (Type: {p.get('type','?')})")
        
    target = next((p for p in playlists if p['name'] == "Top Rated"), None)
    if target:
        print(f"FOUND 'Top Rated' with ID: {target['id']}")
    else:
        print(" 'Top Rated' NOT found.")
        # Try Create
        print("Attempting creation...")
        try:
            # Minimal payload test
            new_pl = client.create_playlist("Top Rated")
            print("Creation success!", new_pl)
        except Exception as e:
            print(f"Creation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
