
import requests
import json

DIRECTUS_URL = "http://localhost:8055"
EMAIL = "admin@yourparty.tech"
PASSWORD = "change_me_admin"

def main():
    # Login
    resp = requests.post(f"{DIRECTUS_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    token = resp.json()['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Me
    me = requests.get(f"{DIRECTUS_URL}/users/me", headers=headers).json()['data']
    print(f"User Role: {me['role']}")
    
    # Get Permissions
    perms = requests.get(f"{DIRECTUS_URL}/permissions", headers=headers, params={"filter[role][_eq]": me['role']})
    print(f"Permissions Status: {perms.status_code}")
    if perms.status_code == 200:
        data = perms.json()['data']
        print(f"Permissions Count: {len(data)}")
        print(json.dumps(data, indent=2))
    
    # Get Role Details
    role_resp = requests.get(f"{DIRECTUS_URL}/roles/{me['role']}", headers=headers)
    print(f"Role Details: {json.dumps(role_resp.json()['data'], indent=2)}")

if __name__ == "__main__":
    main()
