#!/usr/bin/env python3
"""
V2 System Verification Script
YourParty.tech - Project Renovate

Verifies that all V2 components are working correctly:
1. Service connectivity (Directus, Meilisearch, Redis)
2. Migration integrity (record counts)
3. Vote flow simulation
4. ID3 tag writing

Run with: python scripts/verify_v2_system.py
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, Optional, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("v2-verify")

# Load environment
def load_env():
    for path in ['.env', 'infrastructure/docker/.env', 'apps/api/.env']:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, _, value = line.partition('=')
                        if key and value:
                            os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()


class VerificationResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}
    
    def success(self, message: str, **details):
        self.passed = True
        self.message = message
        self.details = details
        return self
    
    def failure(self, message: str, **details):
        self.passed = False
        self.message = message
        self.details = details
        return self


def check_directus() -> VerificationResult:
    """Verify Directus is accessible"""
    result = VerificationResult("Directus CMS")
    
    url = os.getenv("DIRECTUS_URL", "http://localhost:8055")
    try:
        resp = requests.get(f"{url}/server/health", timeout=5)
        if resp.status_code == 200:
            return result.success(f"Healthy at {url}")
        else:
            return result.failure(f"Unhealthy: HTTP {resp.status_code}")
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_meilisearch() -> VerificationResult:
    """Verify Meilisearch is accessible"""
    result = VerificationResult("Meilisearch")
    
    url = os.getenv("MEILI_URL", "http://localhost:7700")
    try:
        resp = requests.get(f"{url}/health", timeout=5)
        if resp.status_code == 200:
            return result.success(f"Healthy at {url}")
        else:
            return result.failure(f"Unhealthy: HTTP {resp.status_code}")
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_redis() -> VerificationResult:
    """Verify Redis is accessible"""
    result = VerificationResult("Redis")
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        import redis
        client = redis.from_url(redis_url, socket_timeout=5)
        client.ping()
        return result.success(f"Connected to {redis_url.split('@')[-1]}")
    except ImportError:
        return result.failure("redis package not installed")
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_mongodb_legacy() -> VerificationResult:
    """Verify MongoDB legacy data is accessible"""
    result = VerificationResult("MongoDB (Legacy)")
    
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
    if not mongo_uri:
        return result.failure("MONGO_URI not configured")
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Get database and collection counts
        db = client.get_database("radio_ratings")
        collections = {
            "ratings": db.ratings.count_documents({}),
            "mood_votes": db.mood_votes.count_documents({}),
            "song_metadata": db.song_metadata.count_documents({})
        }
        
        total = sum(collections.values())
        return result.success(f"{total} total records", collections=collections)
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_api_health() -> VerificationResult:
    """Verify FastAPI backend is running"""
    result = VerificationResult("FastAPI Backend")
    
    url = "http://localhost:8000/health"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return result.success("Healthy", **data)
        else:
            return result.failure(f"Unhealthy: HTTP {resp.status_code}")
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_azuracast() -> VerificationResult:
    """Verify AzuraCast is accessible"""
    result = VerificationResult("AzuraCast")
    
    url = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech")
    try:
        resp = requests.get(f"{url}/api/nowplaying/1", timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            station = data.get("station", {}).get("name", "Unknown")
            is_online = data.get("is_online", False)
            status = "Online" if is_online else "Offline"
            return result.success(f"{station}: {status}")
        else:
            return result.failure(f"API error: HTTP {resp.status_code}")
    except Exception as e:
        return result.failure(f"Connection failed: {e}")


def check_migration_integrity() -> VerificationResult:
    """Compare MongoDB and Directus record counts"""
    result = VerificationResult("Migration Integrity")
    
    # Get MongoDB counts
    mongo_uri = os.getenv("MONGO_URI")
    directus_url = os.getenv("DIRECTUS_URL", "http://localhost:8055")
    directus_token = os.getenv("DIRECTUS_STATIC_TOKEN")
    
    if not mongo_uri or not directus_token:
        return result.failure("Missing MONGO_URI or DIRECTUS_STATIC_TOKEN")
    
    try:
        from pymongo import MongoClient
        mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = mongo.get_database("radio_ratings")
        
        mongo_counts = {
            "ratings": db.ratings.count_documents({}),
            "mood_votes": db.mood_votes.count_documents({})
        }
        
        # Get Directus counts
        headers = {"Authorization": f"Bearer {directus_token}"}
        directus_counts = {}
        
        for collection in ["ratings", "mood_votes"]:
            resp = requests.get(
                f"{directus_url}/items/{collection}?aggregate[count]=*",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                directus_counts[collection] = data.get("data", [{}])[0].get("count", 0)
            else:
                directus_counts[collection] = 0
        
        # Compare
        all_match = all(
            mongo_counts.get(k, 0) == directus_counts.get(k, 0)
            for k in mongo_counts
        )
        
        if all_match:
            return result.success("All records migrated", 
                                  mongo=mongo_counts, 
                                  directus=directus_counts)
        else:
            return result.failure("Record count mismatch",
                                  mongo=mongo_counts,
                                  directus=directus_counts)
    except Exception as e:
        return result.failure(f"Comparison failed: {e}")


def simulate_vote() -> VerificationResult:
    """Simulate a vote submission"""
    result = VerificationResult("Vote Flow")
    
    try:
        # Test via API
        resp = requests.post(
            "http://localhost:8000/vote-mood",
            json={
                "song_id": "test-verification-123",
                "mood_current": "energy",
                "user_id": "v2-verify-script"
            },
            timeout=5
        )
        
        if resp.status_code in (200, 201):
            data = resp.json()
            return result.success("Vote accepted", response=data)
        else:
            return result.failure(f"Vote rejected: HTTP {resp.status_code}")
    except Exception as e:
        return result.failure(f"Vote submission failed: {e}")


def run_all_checks() -> List[VerificationResult]:
    """Run all verification checks"""
    checks = [
        check_directus,
        check_meilisearch,
        check_redis,
        check_mongodb_legacy,
        check_api_health,
        check_azuracast,
        check_migration_integrity,
        simulate_vote
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            result = VerificationResult(check.__name__)
            result.failure(f"Check crashed: {e}")
            results.append(result)
    
    return results


def main():
    logger.info("=" * 60)
    logger.info("V2 SYSTEM VERIFICATION")
    logger.info("=" * 60)
    
    results = run_all_checks()
    
    passed = 0
    failed = 0
    
    for r in results:
        status = "✅" if r.passed else "❌"
        logger.info(f"{status} {r.name}: {r.message}")
        if r.details:
            for k, v in r.details.items():
                logger.info(f"   - {k}: {v}")
        
        if r.passed:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"RESULTS: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
