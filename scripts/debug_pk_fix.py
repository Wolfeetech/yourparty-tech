
import requests
import json
import logging

DIRECTUS_URL = "http://localhost:8055"
EMAIL = "admin@yourparty.tech"
PASSWORD = "change_me_admin"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug-pk")

def main():
    # Login
    resp = requests.post(f"{DIRECTUS_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    headers = {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}

    col_name = "ratings_pk_test"
    requests.delete(f"{DIRECTUS_URL}/collections/{col_name}", headers=headers)

    # Define Schema WITH Auto-Increment ID
    fields = [
        {
            "field": "id", 
            "type": "integer", 
            "meta": {"primary": True, "unique": True}, 
            "schema": {"is_primary_key": True, "has_auto_increment": True}
        },
        {"field": "song_id", "type": "string"}
    ]

    payload = {
        "collection": col_name,
        "schema": {},
        "fields": fields
    }

    logger.info(f"Creating '{col_name}' with PK...")
    resp = requests.post(f"{DIRECTUS_URL}/collections", headers=headers, json=payload)
    if resp.status_code not in (200, 201):
        logger.error(f"Create Failed: {resp.text}")
        return

    # Insert WITHOUT ID (should auto-increment)
    item = {"song_id": "pk_test_1"}
    logger.info(f"Inserting item into '{col_name}'...")
    resp = requests.post(f"{DIRECTUS_URL}/items/{col_name}", headers=headers, json=item)
    
    if resp.status_code in (200, 201):
        logger.info(f"Insert SUCCESS: {resp.json()}")
    else:
        logger.error(f"Insert FAILED: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    main()
