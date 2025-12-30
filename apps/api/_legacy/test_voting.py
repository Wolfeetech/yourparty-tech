import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

BASE_URL = "https://api.yourparty.tech"
TOKEN = None # Add token if needed, but voting is public for now (or anonymous user)

def test_voting_flow():
    print(f"Testing Voting System against {BASE_URL}...\n")
    
    # 1. Get Candidates
    print("1. Fetching Candidates (GET /vote-next-candidates)...")
    try:
        resp = requests.get(f"{BASE_URL}/vote-next-candidates")
        resp.raise_for_status()
        data = resp.json()
        
        candidates = data.get("candidates", [])
        print(f"✅ Received {len(candidates)} candidates.")
        for c in candidates:
            print(f"   - {c.get('title')} by {c.get('artist')} (ID: {c.get('id')})")
            
        expires_at = data.get("expires_at")
        print(f"   - Expires at: {expires_at}")
        
        if not candidates:
            print("❌ No candidates returned! Aborting.")
            return

        # 2. Vote for the first candidate
        candidate_id = candidates[0].get('id')
        print(f"\n2. Voting for candidate: {candidate_id} (POST /vote-next-track)...")
        
        vote_payload = {
            "track_id": candidate_id,
            "user_id": "test_script_user",
            "vote": "like" # Schema says TrackVoteRequest has track_id and user_id, vote logic handled by endpoint?
            # Wait, schemas.py check needed. interactive.py says request: TrackVoteRequest
        }
        
        # Let's check TrackVoteRequest schema if possible, or assume simple dict
        # Based on interactive.py: request.track_id, request.user_id. 
        # mongo_client.submit_next_track_vote takes track_id, user_id.
        
        resp = requests.post(f"{BASE_URL}/vote-next-track", json=vote_payload)
        resp.raise_for_status()
        print(f"✅ Vote response: {resp.json()}")

        # 3. Verify Vote Count
        print(f"\n3. Verifying Vote Count (GET /vote-next-candidates)...")
        resp = requests.get(f"{BASE_URL}/vote-next-candidates")
        data = resp.json()
        votes = data.get("votes", {})
        count = votes.get(candidate_id, 0)
        
        print(f"✅ Vote count for {candidate_id}: {count}")
        if count > 0:
            print("✅ Vote persistence verified!")
        else:
            print("❌ Vote persistence FAILED (Count is 0).")

        # 4. Trigger Winner Calculation
        print(f"\n4. Triggering Winner Calculation (POST /control/vote-next-winner)...")
        resp = requests.post(f"{BASE_URL}/control/vote-next-winner")
        resp.raise_for_status()
        winner_data = resp.json()
        print(f"✅ Winner Result: {json.dumps(winner_data, indent=2)}")
        
        if winner_data.get("success") and winner_data.get("winner", {}).get("id") == candidate_id:
             print("✅ CORRECT WINNER SELECTED!")
        else:
             print("⚠️ Unexpected winner or failure.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_voting_flow()
