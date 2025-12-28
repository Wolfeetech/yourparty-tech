import requests
import time

BASE_URL = "https://api.yourparty.tech"

def test_rate_limit():
    print(f"Testing Rate Limits against {BASE_URL}...\n")
    
    # 1. Test /token limit (5/minute)
    print("1. Spamming /token endpoint (Limit: 5/min)...")
    url = f"{BASE_URL}/token"
    # Invalid credentials are fine, we just want to hit the limiter
    data = {"username": "spam", "password": "spam"} 
    
    for i in range(1, 8):
        resp = requests.post(url, data=data)
        print(f"   Request {i}: Status {resp.status_code}")
        
        if resp.status_code == 429:
            print("✅ Rate limit hit (429 Too Many Requests)!")
            break
        elif i > 5:
             print("❌ Rate limit NOT hit after 5 requests.")
             
    # 2. Test /vote-next-track limit (5/minute)
    print("\n2. Spamming /vote-next-track endpoint (Limit: 5/min)...")
    url = f"{BASE_URL}/vote-next-track"
    # Need valid payload structure, mock data fine
    json_data = {"track_id": "spam_id", "user_id": "spammer"}
    
    for i in range(1, 8):
        resp = requests.post(url, json=json_data)
        print(f"   Request {i}: Status {resp.status_code}")
        
        if resp.status_code == 429:
            print("✅ Rate limit hit (429 Too Many Requests)!")
            return

    print("❌ Failed to trigger rate limit on voting endpoint.")

if __name__ == "__main__":
    test_rate_limit()
