
import requests
import json
import logging

# Config
DIRECTUS_URL = "http://localhost:8055"
EMAIL = "admin@yourparty.tech"
PASSWORD = "change_me_admin"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug-insert")

def main():
    # 1. Login
    resp = requests.post(f"{DIRECTUS_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        logger.error(f"Login failed: {resp.text}")
        return
    
    token = resp.json()['data']['access_token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. Cleanup
    col_name = "ratings_debug"
    requests.delete(f"{DIRECTUS_URL}/collections/{col_name}", headers=headers)

    # 3. Create Collection (Mimic Migration Script)
    fields = [
        # {"field": "id", "type": "integer", "meta": {"primary": True}, "schema": {"is_primary_key": True}},
        # REMOVED ID AS PER LATEST MIGRATION SCRIPT
        {"field": "song_id", "type": "string", "schema": {"max_length": 255}},
        {"field": "user_id", "type": "string", "schema": {"max_length": 255}},
        {"field": "rating", "type": "integer", "schema": {}}
    ]

    payload = {
        "collection": col_name,
        "meta": {
            "collection": col_name,
            "icon": "bug_report",
            "note": "Debug collection"
        },
        "schema": {},
        "fields": fields
    }

    logger.info(f"Creating '{col_name}'...")
    resp = requests.post(f"{DIRECTUS_URL}/collections", headers=headers, json=payload)
    if resp.status_code not in (200, 201):
        logger.error(f"Create Failed: {resp.text}")
        return
    logger.info("Collection created.")

    # 4. Insert Item (Mimic Migration Script)
    item = {
        "song_id": "test_song_123",
        "user_id": "test_user_456",
        "rating": 5
    }

    logger.info(f"Inserting item into '{col_name}'...")
    resp = requests.post(f"{DIRECTUS_URL}/items/{col_name}", headers=headers, json=item)
    
    if resp.status_code in (200, 201):
        logger.info(f"Insert SUCCESS: {resp.json()}")
    else:
        logger.error(f"Insert FAILED: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    main()
