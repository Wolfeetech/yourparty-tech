#!/usr/bin/env python3
"""
MongoDB to Directus V2 Migration Script
YourParty.tech - Project Renovate

Migrates all data from legacy MongoDB to Directus:
- Ratings
- Mood votes
- Song metadata
- User stats (gamification)
- Shoutouts

Run with: python scripts/migrate_v1_to_v2.py [--dry-run]
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("v2-migration")

# Load .env
def load_env():
    env_paths = ['.env', 'infrastructure/docker/.env', 'apps/api/.env']
    for path in env_paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, _, value = line.partition('=')
                        if key and value:
                            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env()

# Configuration
class Config:
    # MongoDB (Source)
    MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
    MONGO_DB = os.getenv("MONGO_DB", "radio_ratings")
    
    # Directus (Target)
    DIRECTUS_URL = os.getenv("DIRECTUS_URL", "http://localhost:8055")
    DIRECTUS_TOKEN = os.getenv("DIRECTUS_STATIC_TOKEN") or os.getenv("DIRECTUS_TOKEN")
    DIRECTUS_EMAIL = os.getenv("DIRECTUS_ADMIN_EMAIL")
    DIRECTUS_PASSWORD = os.getenv("DIRECTUS_ADMIN_PASSWORD")
    
    # Migration settings
    BATCH_SIZE = 50
    DRY_RUN = False


class DirectusClient:
    """Wrapper for Directus REST API"""
    
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
            
    def login(self, email, password) -> bool:
        """Login to get token"""
        try:
            resp = requests.post(f"{self.base_url}/auth/login", json={
                "email": email, "password": password
            })
            if resp.status_code == 200:
                token = resp.json()['data']['access_token']
                self.headers["Authorization"] = f"Bearer {token}"
                return True
            logger.error(f"Login failed: {resp.text}")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Verify Directus is reachable"""
        try:
            resp = requests.get(f"{self.base_url}/server/health", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Directus connection failed: {e}")
            return False
    
    def create_collection(self, name: str, fields: List[Dict]) -> bool:
        """Create a collection if it doesn't exist"""
        # Check if exists
        resp = requests.get(f"{self.base_url}/collections/{name}", headers=self.headers)
        if resp.status_code == 200:
            logger.info(f"Collection '{name}' already exists")
            return True
        
        # Create
        payload = {
            "collection": name,
            "meta": {
                "collection": name,
                "icon": "star",
                "note": f"Migrated from MongoDB on {datetime.now().isoformat()}"
            },
            "schema": {},
            "fields": fields
        }
        resp = requests.post(f"{self.base_url}/collections", headers=self.headers, json=payload)
        if resp.status_code in (200, 201):
            logger.info(f"Created collection '{name}'")
            return True
        else:
            logger.error(f"Failed to create collection '{name}': {resp.text}")
            return False
    
    def bulk_insert(self, collection: str, items: List[Dict]) -> int:
        """Insert multiple items into a collection with retry logic"""
        if not items:
            return 0
        
        import time
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            resp = requests.post(
                f"{self.base_url}/items/{collection}",
                headers=self.headers,
                json=items
            )
            
            if resp.status_code in (200, 201):
                return len(items)
            elif resp.status_code == 429:
                wait = retry_delay * (attempt + 1)
                logger.warning(f"Rate limited on '{collection}'. Waiting {wait}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                logger.error(f"Bulk insert to '{collection}' failed: {resp.text}")
                return 0
                
        logger.error(f"Failed to insert batch to '{collection}' after {max_retries} retries")
        return 0
    
    def get_count(self, collection: str) -> int:
        """Get item count in a collection"""
        resp = requests.get(
            f"{self.base_url}/items/{collection}?aggregate[count]=*",
            headers=self.headers
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', [{}])[0].get('count', 0)
        return 0


class MongoMigrator:
    """Handles MongoDB to Directus migration"""
    
    def __init__(self, mongo_uri: str, mongo_db: str, directus: DirectusClient, dry_run: bool = False):
        self.mongo = MongoClient(mongo_uri)
        self.db = self.mongo[mongo_db]
        self.directus = directus
        self.dry_run = dry_run
        self.stats = {
            "ratings": {"source": 0, "migrated": 0},
            "moods": {"source": 0, "migrated": 0},
            "metadata": {"source": 0, "migrated": 0},
            "user_stats": {"source": 0, "migrated": 0},
            "shoutouts": {"source": 0, "migrated": 0}
        }
    
    def setup_collections(self):
        """Create Directus collections with proper schema"""
        collections = {
            "ratings": [
                {"field": "id", "type": "integer", "meta": {"primary": True, "unique": True}, "schema": {"is_primary_key": True, "has_auto_increment": True}},
                {"field": "song_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "user_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "station_id", "type": "integer", "schema": {"default_value": 1}},
                {"field": "rating", "type": "integer", "schema": {}},
                {"field": "file_path", "type": "string", "schema": {"max_length": 1024}},
                {"field": "title", "type": "string", "schema": {"max_length": 512}},
                {"field": "artist", "type": "string", "schema": {"max_length": 512}},
                {"field": "created_at", "type": "timestamp", "schema": {}},
                {"field": "mongo_id", "type": "string", "schema": {"max_length": 50}}
            ],
            "mood_votes": [
                {"field": "id", "type": "integer", "meta": {"primary": True, "unique": True}, "schema": {"is_primary_key": True, "has_auto_increment": True}},
                {"field": "song_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "user_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "station_id", "type": "integer", "schema": {"default_value": 1}},
                {"field": "mood_current", "type": "string", "schema": {"max_length": 100}},
                {"field": "mood_next", "type": "string", "schema": {"max_length": 100}},
                {"field": "created_at", "type": "timestamp", "schema": {}},
                {"field": "mongo_id", "type": "string", "schema": {"max_length": 50}}
            ],
            "song_metadata": [
                {"field": "id", "type": "integer", "meta": {"primary": True, "unique": True}, "schema": {"is_primary_key": True, "has_auto_increment": True}},
                {"field": "song_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "title", "type": "string", "schema": {"max_length": 512}},
                {"field": "artist", "type": "string", "schema": {"max_length": 512}},
                {"field": "album", "type": "string", "schema": {"max_length": 512}},
                {"field": "genre", "type": "string", "schema": {"max_length": 255}},
                {"field": "bpm", "type": "float", "schema": {}},
                {"field": "initial_key", "type": "string", "schema": {"max_length": 10}},
                {"field": "art_url", "type": "string", "schema": {"max_length": 1024}},
                {"field": "bandcamp_url", "type": "string", "schema": {"max_length": 1024}},
                {"field": "discogs_url", "type": "string", "schema": {"max_length": 1024}},
                {"field": "file_path", "type": "string", "schema": {"max_length": 1024}},
                {"field": "created_at", "type": "timestamp", "schema": {}},
                {"field": "updated_at", "type": "timestamp", "schema": {}},
                {"field": "mongo_id", "type": "string", "schema": {"max_length": 50}}
            ],
            "user_stats": [
                {"field": "id", "type": "integer", "meta": {"primary": True, "unique": True}, "schema": {"is_primary_key": True, "has_auto_increment": True}},
                {"field": "user_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "total_points", "type": "integer", "schema": {"default_value": 0}},
                {"field": "streak_days", "type": "integer", "schema": {"default_value": 0}},
                {"field": "last_active", "type": "timestamp", "schema": {}},
                {"field": "actions", "type": "json", "schema": {}},
                {"field": "mongo_id", "type": "string", "schema": {"max_length": 50}}
            ],
            "shoutouts": [
                {"field": "id", "type": "integer", "meta": {"primary": True, "unique": True}, "schema": {"is_primary_key": True, "has_auto_increment": True}},
                {"field": "message", "type": "text", "schema": {}},
                {"field": "sender", "type": "string", "schema": {"max_length": 255}},
                {"field": "user_id", "type": "string", "schema": {"max_length": 255}},
                {"field": "station_id", "type": "integer", "schema": {"default_value": 1}},
                {"field": "created_at", "type": "timestamp", "schema": {}},
                {"field": "mongo_id", "type": "string", "schema": {"max_length": 50}}
            ]
        }
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create collections: " + ", ".join(collections.keys()))
            return
        
        for name, fields in collections.items():
            self.directus.create_collection(name, fields)
    
    # MongoDB source collection names
    COLLECTION_RATINGS = "rating_events"
    COLLECTION_MOODS = "moods"
    COLLECTION_METADATA = "song_metadata"

    def migrate_ratings(self):
        """Migrate ratings collection"""
        collection = self.db[self.COLLECTION_RATINGS]
        count = collection.count_documents({})
        self.stats["ratings"]["source"] = count
        logger.info(f"Migrating {count} ratings from '{self.COLLECTION_RATINGS}'...")
        
        if self.dry_run:
            return
        
        batch = []
        migrated = 0
        
        for doc in collection.find({}):
            item = {
                "song_id": doc.get("song_id", ""),
                "user_id": doc.get("user_id", "anonymous"),
                "station_id": doc.get("station_id", 1),
                "rating": doc.get("rating", 0),
                "file_path": doc.get("file_path", ""),
                "title": doc.get("title", ""),
                "artist": doc.get("artist", ""),
                "created_at": doc.get("timestamp", datetime.now()).isoformat() if doc.get("timestamp") else None,
                "mongo_id": str(doc.get("_id", ""))
            }
            batch.append(item)
            
            if len(batch) >= Config.BATCH_SIZE:
                migrated += self.directus.bulk_insert("ratings", batch)
                batch = []
        
        if batch:
            migrated += self.directus.bulk_insert("ratings", batch)
        
        self.stats["ratings"]["migrated"] = migrated
        logger.info(f"Migrated {migrated}/{count} ratings")
    
    def migrate_mood_votes(self):
        """Migrate moods collection"""
        collection = self.db[self.COLLECTION_MOODS]
        count = collection.count_documents({})
        self.stats["moods"]["source"] = count
        logger.info(f"Migrating {count} mood votes from '{self.COLLECTION_MOODS}'...")
        
        if self.dry_run:
            return
        
        batch = []
        migrated = 0
        
        for doc in collection.find({}):
            # Handle both 'mood' and 'mood_current' fields from different V1 iterations
            mood = doc.get("mood") or doc.get("mood_current") or ""
            
            item = {
                "song_id": doc.get("song_id", ""),
                "user_id": doc.get("user_id", "anonymous"),
                "station_id": doc.get("station_id", 1),
                "mood_current": mood,
                "mood_next": doc.get("mood_next", ""),
                "created_at": doc.get("timestamp", datetime.now()).isoformat() if doc.get("timestamp") else None,
                "mongo_id": str(doc.get("_id", ""))
            }
            batch.append(item)
            
            if len(batch) >= Config.BATCH_SIZE:
                migrated += self.directus.bulk_insert("mood_votes", batch)
                batch = []
        
        if batch:
            migrated += self.directus.bulk_insert("mood_votes", batch)
        
        self.stats["moods"]["migrated"] = migrated
        logger.info(f"Migrated {migrated}/{count} mood votes")
    
    def migrate_metadata(self):
        """Migrate song_metadata collection"""
        collection = self.db[self.COLLECTION_METADATA]
        count = collection.count_documents({})
        self.stats["metadata"]["source"] = count
        logger.info(f"Migrating {count} song metadata records...")
        
        if self.dry_run:
            return
        
        batch = []
        migrated = 0
        
        for doc in collection.find({}):
            # Unpack nested V1 metadata
            meta = doc.get("metadata", {})
            
            item = {
                "song_id": doc.get("song_id", ""),
                "title": meta.get("title") or doc.get("title", ""),
                "artist": meta.get("artist") or doc.get("artist", ""),
                "album": meta.get("album") or doc.get("album", ""),
                "genre": meta.get("genre") or doc.get("genre", ""),
                "bpm": meta.get("bpm") or doc.get("bpm"),
                "initial_key": meta.get("initial_key") or doc.get("initial_key", ""),
                "art_url": meta.get("art") or doc.get("art", ""),
                "bandcamp_url": meta.get("bandcamp_url") or doc.get("bandcamp_url", ""),
                "discogs_url": meta.get("discogs_url") or doc.get("discogs_url", ""),
                "file_path": doc.get("file_path", ""),
                "created_at": doc.get("created_at", datetime.now()).isoformat() if doc.get("created_at") else None,
                "updated_at": doc.get("updated_at", datetime.now()).isoformat() if doc.get("updated_at") else None,
                "mongo_id": str(doc.get("_id", ""))
            }
            batch.append(item)
            
            if len(batch) >= Config.BATCH_SIZE:
                migrated += self.directus.bulk_insert("song_metadata", batch)
                batch = []
        
        if batch:
            migrated += self.directus.bulk_insert("song_metadata", batch)
        
        self.stats["metadata"]["migrated"] = migrated
        logger.info(f"Migrated {migrated}/{count} metadata records")
    
    def migrate_user_stats(self):
        """Migrate user_stats collection (gamification)"""
        collection = self.db["user_stats"]
        count = collection.count_documents({})
        self.stats["user_stats"]["source"] = count
        logger.info(f"Migrating {count} user stats...")
        
        if self.dry_run:
            return
        
        batch = []
        migrated = 0
        
        for doc in collection.find({}):
            item = {
                "user_id": doc.get("user_id", ""),
                "total_points": doc.get("total_points", 0),
                "streak_days": doc.get("streak_days", 0),
                "last_active": doc.get("last_active", datetime.now()).isoformat() if doc.get("last_active") else None,
                "actions": json.dumps(doc.get("actions", {})),
                "mongo_id": str(doc.get("_id", ""))
            }
            batch.append(item)
            
            if len(batch) >= Config.BATCH_SIZE:
                migrated += self.directus.bulk_insert("user_stats", batch)
                batch = []
        
        if batch:
            migrated += self.directus.bulk_insert("user_stats", batch)
        
        self.stats["user_stats"]["migrated"] = migrated
        logger.info(f"Migrated {migrated}/{count} user stats")
    
    def migrate_shoutouts(self):
        """Migrate shoutouts collection"""
        collection = self.db["shoutouts"]
        count = collection.count_documents({})
        self.stats["shoutouts"]["source"] = count
        logger.info(f"Migrating {count} shoutouts...")
        
        if self.dry_run:
            return
        
        batch = []
        migrated = 0
        
        for doc in collection.find({}):
            item = {
                "message": doc.get("message", ""),
                "sender": doc.get("sender", ""),
                "user_id": doc.get("user_id", "anonymous"),
                "station_id": doc.get("station_id", 1),
                "created_at": doc.get("timestamp", datetime.now()).isoformat() if doc.get("timestamp") else None,
                "mongo_id": str(doc.get("_id", ""))
            }
            batch.append(item)
            
            if len(batch) >= Config.BATCH_SIZE:
                migrated += self.directus.bulk_insert("shoutouts", batch)
                batch = []
        
        if batch:
            migrated += self.directus.bulk_insert("shoutouts", batch)
        
        self.stats["shoutouts"]["migrated"] = migrated
        logger.info(f"Migrated {migrated}/{count} shoutouts")
    
    def run_all(self):
        """Execute full migration"""
        logger.info("=" * 60)
        logger.info("V2 MIGRATION: MongoDB -> Directus")
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("*** DRY RUN MODE - No changes will be made ***")
        
        # Setup collections first
        self.setup_collections()
        
        # Migrate each collection
        self.migrate_ratings()
        self.migrate_mood_votes()
        self.migrate_metadata()
        self.migrate_user_stats()
        self.migrate_shoutouts()
        
        # Summary
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        for name, counts in self.stats.items():
            status = "✓" if counts["source"] == counts["migrated"] else "⚠"
            logger.info(f"{status} {name}: {counts['migrated']}/{counts['source']}")
        
        return self.stats


def main():
    parser = argparse.ArgumentParser(description="Migrate MongoDB to Directus V2")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--mongo-uri", help="Override MONGO_URI")
    parser.add_argument("--directus-url", help="Override DIRECTUS_URL")
    args = parser.parse_args()
    
    # Override config
    if args.mongo_uri:
        Config.MONGO_URI = args.mongo_uri
    if args.directus_url:
        Config.DIRECTUS_URL = args.directus_url
    Config.DRY_RUN = args.dry_run
    
    # Validate config
    if not Config.MONGO_URI:
        logger.error("MONGO_URI not set. Use --mongo-uri or set environment variable.")
        sys.exit(1)
    
    # Initialize clients
    directus = DirectusClient(Config.DIRECTUS_URL, Config.DIRECTUS_TOKEN)
    
    # Try login if no token
    if not Config.DIRECTUS_TOKEN:
        if Config.DIRECTUS_EMAIL and Config.DIRECTUS_PASSWORD:
            logger.info(f"Authenticating as {Config.DIRECTUS_EMAIL}...")
            if not directus.login(Config.DIRECTUS_EMAIL, Config.DIRECTUS_PASSWORD):
                sys.exit(1)
        else:
            logger.error("No token or credentials provided.")
            sys.exit(1)
    
    if not directus.check_connection():
        logger.error(f"Cannot connect to Directus at {Config.DIRECTUS_URL}")
        sys.exit(1)
    
    # Run migration
    migrator = MongoMigrator(
        Config.MONGO_URI,
        Config.MONGO_DB,
        directus,
        dry_run=Config.DRY_RUN
    )
    
    stats = migrator.run_all()
    
    # Exit code based on success
    total_source = sum(s["source"] for s in stats.values())
    total_migrated = sum(s["migrated"] for s in stats.values())
    
    if total_migrated == total_source:
        logger.info("Migration completed successfully!")
        sys.exit(0)
    else:
        logger.warning(f"Migration incomplete: {total_migrated}/{total_source} records")
        sys.exit(1)


if __name__ == "__main__":
    main()
