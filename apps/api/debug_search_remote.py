import sys
import os
import logging
import asyncio

# Ensure we can find modules in /app
sys.path.append('/app')

from azuracast_client import AzuraCastClient
try:
    from config_secrets import AZURACAST_API_URL, AZURACAST_API_KEY
except ImportError:
    AZURACAST_API_URL = os.getenv("AZURACAST_API_URL", "https://radio.yourparty.tech/api")
    AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "")

logging.basicConfig(level=logging.INFO)

async def main():
    print("=== AzuraSearch Debugger (Async) ===")
    print(f"URL: {AZURACAST_API_URL}")
    masked_key = (AZURACAST_API_KEY[:4] + "***" + AZURACAST_API_KEY[-4:]) if AZURACAST_API_KEY else "NONE"
    print(f"KEY: {masked_key}")

    client = AzuraCastClient(
        base_url=AZURACAST_API_URL,
        api_key=AZURACAST_API_KEY,
        station_id=1
    )

    queries = ["rave", "techno", "deep"]
    for q in queries:
        print(f"\nSearching for query: '{q}'...")
        try:
            results = await client.search_requests(q)
            print(f"Search Results Count: {len(results)}")
            
            for i, r in enumerate(results[:3]):
                song = r.get('song', {})
                print(f"  Result {i}: {song.get('title')} - {song.get('artist')} [ID: {song.get('id')}]")
                
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
