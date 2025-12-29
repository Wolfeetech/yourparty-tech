
import logging
import time
import sys
from pathlib import Path
try:
    from apps.api.music_scanner import MusicScanner
    from apps.api.mongo_client import MongoDatabaseClient
    from apps.api.config_secrets import (
        MONGO_URI, SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD,
        LIBRARY_ROOT_WIN
    )
except ImportError:
    from music_scanner import MusicScanner
    from mongo_client import MongoDatabaseClient
    from config_secrets import (
        MONGO_URI, SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD,
        LIBRARY_ROOT_WIN
    )

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("LibraryService")

def get_library_service(mongo_client=None):
    """Factory function to get a LibraryService instance."""
    # Return a simple wrapper that doesn't require library_path
    # since we may not always have a local path on the API server
    class LibraryServiceWrapper:
        def __init__(self, mc):
            self.mongo = mc
        def check_promotion(self, song_id):
            # Placeholder - can be expanded later
            pass
            
        async def get_all_tracks(self):
            """Fetch all tracks from MongoDB."""
            try:
                # Limit to 2000 to prevent overload
                cursor = self.mongo.tracks_collection.find().limit(2000)
                tracks = []
                for doc in cursor:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    tracks.append(doc)
                return tracks
            except Exception as e:
                logger.error(f"Error fetching all tracks: {e}")
                return []
                
        async def sync_azuracast_ids(self, azura_client):
            """Sync AzuraCast Media IDs to MongoDB."""
            import re
            try:
                # Run blocking sync in thread if needed, or just run it (it's sync requests)
                # For safety in async context:
                media_list = await azura_client.get_station_media()
                count = 0
                
                for media in media_list:
                    az_song_id = media.get('song_id')
                    az_media_id = media.get('id')
                    az_path = media.get('path')
                    
                    if not az_media_id:
                        continue
                        
                    # 1. Match by Song ID (Hash)
                    if az_song_id:
                        res = self.mongo.tracks_collection.update_one(
                            {"song_id": az_song_id},
                            {"$set": {"azuracast_id": az_media_id, "azuracast_path": az_path}}
                        )
                        if res.modified_count > 0:
                            count += 1
                            continue
                            
                    # 2. Match by Filename (Fallback)
                    if az_path:
                        # Normalize path separators (Azura uses /, Windows typically \)
                        # We try to match the end of the file_path in Mongo
                        search_path = az_path.replace('/', '[\\\\/]') 
                        res = self.mongo.tracks_collection.update_one(
                            {"file_path": {"$regex": search_path + "$", "$options": "i"}},
                            {"$set": {"azuracast_id": az_media_id}}
                        )
                        if res.modified_count > 0:
                            count += 1
                            
                return {"success": True, "synced_count": count}
            except Exception as e:
                logger.error(f"AzuraCast Sync Logic Failed: {e}")
                return {"success": False, "error": str(e)}
    return LibraryServiceWrapper(mongo_client)

class LibraryService:
    def __init__(self, library_path: str):
        self.library_path = library_path
        self.scanner = MusicScanner()
        try:
             self.mongo = MongoDatabaseClient(MONGO_URI)
        except Exception:
             self.mongo = None
             logger.error("Failed to connect to Mongo")

    def run_ingestion(self):
        """
        Scans the library path and upserts tracks into MongoDB.
        """
        if not self.mongo:
            logger.error("Cannot run ingestion: No DB connection.")
            return

        logger.info(f"🎤 Starting Library Ingestion from {self.library_path}")
        
        count_new = 0
        count_updated = 0
        
        # Scan
        for track_data in self.scanner.scan_directory(self.library_path):
            file_path = track_data['path']
            metadata = track_data['metadata']
            rel_path = self.mongo.normalize_path(file_path)
            
            # Upsert to Mongo
            try:
                # We use file_path as unique key (or could use hash)
                # Note: Windows paths might differ if mounted differently.
                # Ideally store relative path from library root?
                # For now using absolute path from scanner (which sees Z:\...)
                
                # Check exist
                existing = self.mongo.tracks_collection.find_one({"file_path": file_path})
                
                doc = {
                    "file_path": file_path,
                    "relative_path": rel_path,
                    "filename": track_data['filename'],
                    "metadata": metadata,
                    "last_scanned": time.time()
                }
                
                if not existing:
                    # New Track
                    # Generate a simple song_id if not present? 
                    # Usually Mongo generates _id. We might want a string song_id.
                    # Let's let Mongo handle _id, and map string(id) to song_id if needed?
                    # Mongo Client uses song_id often.
                    # Lets create a string song_id if generic.
                    pass
                else:
                    # Preserve existing song_id if present
                    doc['song_id'] = existing.get('song_id')

                result = self.mongo.tracks_collection.update_one(
                    {"file_path": file_path},
                    {"$set": doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    count_new += 1
                    # Set song_id to string of ObjectId for easier use
                    self.mongo.tracks_collection.update_one(
                        {"_id": result.upserted_id},
                        {"$set": {"song_id": str(result.upserted_id)}}
                    )
                else:
                    count_updated += 1
                    # Ensure song_id exists if missing
                    if not existing.get('song_id'):
                         self.mongo.tracks_collection.update_one(
                            {"file_path": file_path},
                            {"$set": {"song_id": str(existing['_id'])}}
                        )

            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
        
        logger.info(f"✅ Ingestion Complete. New: {count_new}, Updated: {count_updated}")

if __name__ == "__main__":
    import subprocess
    
    # Ensure Drive Mount
    drive_letter = Path(LIBRARY_ROOT_WIN).drive or "Z:"
    unc_path = f"\\\\{SMB_SERVER}\\{SMB_SHARE}"
    
    # Check if mounted
    if not Path(drive_letter).exists():
        print(f"🔌 Mounting {unc_path}...")
        cmd = f'net use {drive_letter} "{unc_path}" /USER:{SMB_USERNAME} "{SMB_PASSWORD}"'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not Path(drive_letter).exists():
            print("❌ Failed to mount.")
            sys.exit(1)
    
    # Run Service
    service = LibraryService(LIBRARY_ROOT_WIN)
    service.run_ingestion()
