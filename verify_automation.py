import asyncio
import httpx
import os
import random
import time

# Use localhost since we run this on the container itself 
# OR use the internal IP if running from another container.
# If running on CT 211 via 'pct exec', localhost:8000 works.
API_URL = "http://127.0.0.1:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Get Current Song
        print("🎵 Fetching current song...")
        try:
            resp = await client.get(f"{API_URL}/status")
            data = resp.json()
            song = data['now_playing']['song']
            song_id = song['id']
            title = song['title']
            print(f"✅ Current Song: {title} (ID: {song_id})")
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
            return

        # 2. Simulate 3 Votes for ENERGY
        target_mood = "energy"
        print(f"🗳️  Simulating 3 votes for '{target_mood}'...")
        
        users = ["verifier_1", "verifier_2", "verifier_3"]
        
        for uid in users:
            payload = {
                "song_id": str(song_id),
                "mood_current": target_mood,
                "user_id": uid,
                "vote": "like"
            }
            try:
                r = await client.post(f"{API_URL}/vote-mood", json=payload)
                if r.status_code == 200:
                    print(f"   ✅ Vote sent for {uid}")
                else:
                    print(f"   ❌ Vote failed: {r.status_code} {r.text}")
            except Exception as e:
                print(f"   ❌ Request error: {e}")
            
            # Small delay to ensure DB writes
            await asyncio.sleep(0.5)

        print("\n⏳ Votes cast. Checking logs for PROMOTION...")
        # We can't easily grep logs from python inside the container unless we read headers
        # But we can rely on the user (agent) to check journalctl next.
        print("Done. Please check 'journalctl -u radio-api | grep PROMOTED'")

if __name__ == "__main__":
    asyncio.run(main())
