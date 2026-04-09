
import requests

DIRECTUS_URL = "http://localhost:8055"
EMAIL = "admin@yourparty.tech"
PASSWORD = "change_me_admin"

def main():
    # Login
    resp = requests.post(f"{DIRECTUS_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    token = resp.json()['data']['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    collections = ["ratings", "mood_votes", "song_metadata", "user_stats", "shoutouts", "debug_test"]
    
    for col in collections:
        print(f"Deleting '{col}'...")
        r = requests.delete(f"{DIRECTUS_URL}/collections/{col}", headers=headers)
        print(f"Status: {r.status_code}")

if __name__ == "__main__":
    main()
