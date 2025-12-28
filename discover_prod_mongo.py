import os
import sys
from pymongo import MongoClient

def discover():
    try:
        # Production URI from config_secrets.py
        uri = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        print(f"Connecting to production: 192.168.178.222")
        
        dbs = client.list_database_names()
        print(f"Databases found: {dbs}")
        
        for db_name in dbs:
            if db_name in ['admin', 'config', 'local']: continue
            db = client[db_name]
            cols = db.list_collection_names()
            print(f"\nDB: {db_name}")
            for col in cols:
                count = db[col].count_documents({})
                print(f"  - {col}: {count} docs")
                if count > 0:
                    sample = db[col].find_one()
                    # Only print sample keys if it's a media/track collection
                    if 'track' in col or 'rating' in col or 'mood' in col:
                        print(f"    Sample keys: {list(sample.keys())}")
                    
    except Exception as e:
        print(f"Discovery failed: {e}")

if __name__ == "__main__":
    discover()
