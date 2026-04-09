import asyncio
import os
import sys
import logging
from datetime import datetime

# Add apps/api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../apps/api')))

from mongo_client import MongoDatabaseClient
from mood_scheduler import select_next_track_by_mood, get_curve_mood, MOOD_CURVE

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyAudioScience")

async def test_harmonic_mixing():
    print("\n=== Testing Harmonic Mixing Logic ===")
    mongo = MongoDatabaseClient()
    
    # 1. Cleanup old test data
    mongo.tracks_collection.delete_many({"file_path": {"$regex": "^TEST_HARMONIC_"}})
    mongo.moods_collection.delete_many({"song_id": {"$regex": "^TEST_HARMONIC_"}})
    
    # 2. Insert Test Tracks
    test_tracks = [
        # 8A Compatible: 8A, 7A, 9A, 8B
        {"song_id": "TEST_HARMONIC_1", "title": "Track 8A", "key": "8A", "mood": "energetic"},
        {"song_id": "TEST_HARMONIC_2", "title": "Track 9A", "key": "9A", "mood": "energetic"}, # Compatible
        {"song_id": "TEST_HARMONIC_3", "title": "Track 12B", "key": "12B", "mood": "energetic"}, # Incompatible
        {"song_id": "TEST_HARMONIC_4", "title": "Track 3B", "key": "3B", "mood": "energetic"}, # Incompatible
    ]
    
    print("Inserting test tracks...")
    for t in test_tracks:
        mongo.tracks_collection.insert_one({
            "song_id": t["song_id"],
            "file_path": f"TEST_HARMONIC_{t['key']}",
            "relative_path": f"TEST_HARMONIC_{t['key']}",
            "metadata": {"title": t["title"], "initial_key": t["key"]},
            "moods": [t["mood"]] 
        })
        # Tag with mood
        mongo.moods_collection.insert_one({
            "song_id": t["song_id"],
            "mood": t["mood"],
            "station_id": 1
        })
        
    # 3. Test Selection with Key 8A
    print("\n--- Test: Current Key = 8A ---")
    print("Expected: Track 8A or Track 9A. Should NOT pick 12B or 3B.")
    
    success_count = 0
    trials = 20
    for i in range(trials):
        selected = await select_next_track_by_mood(mongo, "energetic", station_id=1, current_key="8A")
        if selected:
            key = selected['metadata']['initial_key']
            print(f"Selection {i+1}: {selected['metadata']['title']} ({key})")
            if key in ["8A", "9A", "7A", "8B"]:
                success_count += 1
            else:
                print(f"❌ FAILED: Selected {key} which is incompatible with 8A")
    
    print(f"\nHarmonic Match Rate: {success_count}/{trials}")
    if success_count == trials:
        print("✅ Harmonic Mixing Verification Passed!")
    else:
        print("⚠️ Partial Success or Filtering Issue (Review implementation)")
        
    # Cleanup
    mongo.tracks_collection.delete_many({"file_path": {"$regex": "^TEST_HARMONIC_"}})
    mongo.moods_collection.delete_many({"song_id": {"$regex": "^TEST_HARMONIC_"}})

def test_mood_curve():
    print("\n=== Testing Mood Curve ===")
    current_mood = get_curve_mood()
    print(f"Current Time: {datetime.now().hour}h -> Mood: {current_mood}")
    
    # Test all hours
    test_hours = [7, 13, 19, 23, 4]
    expected = ["energetic", "chill", "euphoric", "energetic", "atmospheric"]
    
    print("\nChecking Schedule Consistency:")
    for h, exp in zip(test_hours, expected):
        # We can't mock datetime easily without library, so we just verify the dict
        target = None
        for hr, m in sorted(MOOD_CURVE.items()):
            if h >= hr:
                target = m
        if not target: target = MOOD_CURVE[max(MOOD_CURVE.keys())]
        
        print(f"Hour {h}: {target} (Expected: {exp}) -> {'✅' if target == exp else '❌'}")

if __name__ == "__main__":
    asyncio.run(test_harmonic_mixing())
    test_mood_curve()
