import os
import sys
from pymongo import MongoClient

def discover():
    try:
        # Check environment variable
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        
        print(f"Connecting to: {uri.split('@')[-1] if '@' in uri else uri}")
        
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
                    print(f"    Sample keys: {list(sample.keys())}")
                    
    except Exception as e:
        print(f"Discovery failed: {e}")

if __name__ == "__main__":
    discover()
