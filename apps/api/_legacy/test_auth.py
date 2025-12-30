
import requests
import sys

BASE_URL = "https://api.yourparty.tech"
# BASE_URL = "http://192.168.178.211:8000" # Fallback if domain fails

def test_auth():
    print(f"Testing Auth against {BASE_URL}...")
    
    # 1. Test Public Endpoint (should work)
    print("\n1. Testing Public Endpoint (GET /status)...")
    try:
        resp = requests.get(f"{BASE_URL}/status")
        if resp.status_code == 200:
            print("✅ Public endpoint accessible.")
        else:
            print(f"❌ Public endpoint failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Test Protected Endpoint without Token (should fail 401)
    print("\n2. Testing Protected Endpoint (POST /control/steer) - No Token...")
    try:
        resp = requests.post(f"{BASE_URL}/control/steer", json={"mode": "auto", "target": "energy"})
        if resp.status_code == 401:
            print("✅ Protected endpoint correctly rejected request (401).")
        else:
            print(f"❌ Protected endpoint failed validation: {resp.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    # 3. Login (Get Token)
    print("\n3. Testing Login (POST /token)...")
    token = None
    try:
        # Default hardcoded admin/admin
        resp = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin"})
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            print(f"✅ Login successful. Token: {token[:10]}...")
        else:
             print(f"❌ Login failed: {resp.status_code} - {resp.text}")
             return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 4. Test Protected Endpoint with Token
    print("\n4. Testing Protected Endpoint with Token (GET /users/me)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if resp.status_code == 200:
             print(f"✅ Protected endpoint accessible. User: {resp.json().get('username')}")
        else:
             print(f"❌ Protected endpoint failed with token: {resp.status_code} - {resp.text}")

    except Exception as e:
         print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_auth()
