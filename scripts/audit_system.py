import os
import logging
from pymongo import MongoClient
from pathlib import Path

# Setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SystemAudit")

# Config
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"
LIBRARY_ROOT = os.getenv("LIBRARY_ROOT_WIN", r"Z:\yourparty_Libary")
INBOX_ROOT = os.path.join(LIBRARY_ROOT, "Inbox")

def audit_mongo():
    try:
        client = MongoClient(MONGO_URI)
        db = client["yourparty"]
        tracks = db["tracks"]
        
        total = tracks.count_documents({})
        linked = tracks.count_documents({"azuracast_id": {"$ne": None}})
        unlinked = tracks.count_documents({"azuracast_id": None})
        
        logger.info(f"=== 📊 MONGODB AUDIT ===")
        logger.info(f"Total Tracks:   {total}")
        logger.info(f"✅ Linked (Live): {linked}")
        logger.info(f"⚠️ Unlinked (Dead?): {unlinked} (Potential candidates for pruning)")
        
        return unlinked
    except Exception as e:
        logger.error(f"Mongo Error: {e}")
        return 0

def audit_files():
    try:
        logger.info(f"\n=== 📂 FILE SYSTEM AUDIT ===")
        
        # Check Inbox
        if os.path.exists(INBOX_ROOT):
            inbox_count = len([f for f in Path(INBOX_ROOT).rglob('*') if f.is_file()])
            logger.info(f"📬 Inbox Clutter: {inbox_count} files waiting to be processed.")
        else:
            logger.info("❌ Inbox folder unreachable!")

        # Check Library
        if os.path.exists(LIBRARY_ROOT):
            lib_count = len([f for f in Path(LIBRARY_ROOT).rglob('*') if f.is_file()])
            logger.info(f"📚 Library Files: {lib_count} files in {LIBRARY_ROOT}")
        else:
             logger.info("❌ Library folder unreachable!")
             
    except Exception as e:
        logger.error(f"File Error: {e}")

if __name__ == "__main__":
    audit_mongo()
    audit_files()
    print("\n[Recommendation]: If 'Unlinked' count is high (>1000) and they are not needed, run 'prune_db.py'.")
