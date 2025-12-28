#!/usr/bin/env python3
"""Debug the actual update mechanism."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

def debug():
    mongo = MongoDatabaseClient(MONGO_URI)
    
    # Get a real document
    doc = mongo.tracks_collection.find_one()
    print(f"Sample doc _id: {doc['_id']} (type: {type(doc['_id'])})")
    print(f"Sample file_path: {doc.get('file_path', 'N/A')}")
    
    # Extract filename
    fp = doc.get('file_path', '')
    filename = fp.replace("\\", "/").split("/")[-1].lower()
    print(f"Extracted filename: {filename}")
    
    # Try direct update
    result = mongo.tracks_collection.update_one(
        {"_id": doc['_id']},
        {"$set": {"azuracast_id": 99999, "test_update": "works"}}
    )
    print(f"Direct update - Matched: {result.matched_count}, Modified: {result.modified_count}")
    
    # Verify
    updated = mongo.tracks_collection.find_one({"_id": doc['_id']})
    print(f"After update azuracast_id: {updated.get('azuracast_id')}")
    print(f"After update test_update: {updated.get('test_update')}")

if __name__ == "__main__":
    debug()
