#!/usr/bin/env python3
"""
MongoDB Cleanup Script - Remove test/debug entries from ratings collection.

Run on server: python3 cleanup_test_data.py

This removes entries with IDs matching patterns like:
- debug_test
- test123
- final_1761434058
- limit_test_final
- etc.
"""
import os
import re
from pymongo import MongoClient

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["yourparty"]

# Patterns that indicate test data
TEST_PATTERNS = [
    r"^debug",
    r"^test",
    r"^final_\d+",
    r"limit_test",
    r"_test_\d+$"
]

def is_test_entry(song_id: str) -> bool:
    """Check if song_id matches a test pattern."""
    for pattern in TEST_PATTERNS:
        if re.match(pattern, song_id, re.IGNORECASE):
            return True
    return False

def cleanup_ratings():
    """Remove test entries from ratings collection."""
    ratings = db.ratings.find({})
    removed = 0
    kept = 0
    
    for rating in ratings:
        song_id = rating.get("song_id", "")
        if is_test_entry(song_id):
            print(f"  Removing: {song_id}")
            db.ratings.delete_one({"_id": rating["_id"]})
            removed += 1
        else:
            kept += 1
    
    return removed, kept

def cleanup_moods():
    """Remove test entries from moods collection."""
    moods = db.moods.find({})
    removed = 0
    
    for mood in moods:
        song_id = mood.get("song_id", "")
        if is_test_entry(song_id):
            print(f"  Removing mood: {song_id}")
            db.moods.delete_one({"_id": mood["_id"]})
            removed += 1
    
    return removed

def main():
    print("=" * 50)
    print("MongoDB Cleanup - Removing Test Data")
    print("=" * 50)
    print()
    
    print("Cleaning ratings collection...")
    removed_ratings, kept_ratings = cleanup_ratings()
    print(f"  Removed: {removed_ratings}, Kept: {kept_ratings}")
    print()
    
    print("Cleaning moods collection...")
    removed_moods = cleanup_moods()
    print(f"  Removed: {removed_moods}")
    print()
    
    print("=" * 50)
    print("Cleanup complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
