
import pymongo
import sys

uri = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"

try:
    print(f"Attempting connection to {uri}...")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    info = client.server_info()
    print("✅ Connected to MongoDB!")
    print(f"Version: {info.get('version')}")
    
    db = client.yourparty_radio
    count = db.ratings.count_documents({})
    print(f"Ratings count: {count}")
    
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)
