
import os
import requests
import json

# Configuration
DIRECTUS_URL = "http://localhost:8055"
EMAIL = "admin@yourparty.tech"
PASSWORD = "change_me_admin"

def main():
    print(f"Connecting to {DIRECTUS_URL} as {EMAIL}...")
    
    # 1. Login
    try:
        resp = requests.post(f"{DIRECTUS_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login FAILED: {resp.status_code} {resp.text}")
            return
        
        token = resp.json()['data']['access_token']
        print(f"Login SUCCESS. Token: {token[:10]}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    except Exception as e:
        print(f"Login ERROR: {e}")
        return

    # 2. Who am I?
    try:
        resp = requests.get(f"{DIRECTUS_URL}/users/me", headers=headers)
        print(f"User Info: {resp.status_code}")
        if resp.status_code == 200:
            user = resp.json()['data']
            print(f"ID: {user['id']}")
            print(f"Role: {user['role']}")
            
            # Check Role Admin Access
            role_resp = requests.get(f"{DIRECTUS_URL}/roles/{user['role']}", headers=headers)
            if role_resp.status_code == 200:
                role = role_resp.json()['data']
                print(f"Role Name: {role.get('name')}")
                print(f"Admin Access: {role.get('admin_access')}")
    except Exception as e:
        print(f"User Check ERROR: {e}")

    # 3. List Collections
    try:
        resp = requests.get(f"{DIRECTUS_URL}/collections", headers=headers)
        print(f"Collections Check: {resp.status_code}")
        if resp.status_code == 200:
            cols = [c['collection'] for c in resp.json()['data'] if not c['collection'].startswith('directus_')]
            print(f"User Collections: {cols}")
    except Exception as e:
        print(f"Collection List ERROR: {e}")

    # 4. Try Create Test Collection
    test_col = "debug_test"
    try:
        print(f"Creating collection '{test_col}'...")
        payload = {
            "collection": test_col,
            "schema": {},
            "fields": [
                {"field": "name", "type": "string"}
            ]
        }
        resp = requests.post(f"{DIRECTUS_URL}/collections", headers=headers, json=payload)
        print(f"Create Collection: {resp.status_code}")
        if resp.status_code not in (200, 201) and "already exists" not in resp.text:
            print(f"Create FAILED: {resp.text}")
        
    except Exception as e:
        print(f"Create ERROR: {e}")

    # 5. Try Insert Item
    try:
        print(f"Inserting item into '{test_col}'...")
        payload = {"name": "test_item"}
        resp = requests.post(f"{DIRECTUS_URL}/items/{test_col}", headers=headers, json=payload)
        print(f"Insert Item: {resp.status_code}")
        if resp.status_code not in (200, 201):
            print(f"Insert FAILED: {resp.text}")
        else:
            print("Insert SUCCESS")
            
    except Exception as e:
        print(f"Insert ERROR: {e}")

if __name__ == "__main__":
    main()
