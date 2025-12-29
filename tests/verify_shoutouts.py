import requests
import json
import time

BASE_URL = "https://yourparty.tech/wp-json/yourparty/v1"

def test_shoutouts():
    print("--- Testing Shoutout System ---")
    
    # 1. Send Shoutout
    payload = {
        "message": "Hello from Auto-Test " + str(time.time()),
        "sender": "Antigravity",
        "user_id": "test_user"
    }
    
    print(f"Sending: {payload['message']}")
    try:
        resp = requests.post(f"{BASE_URL}/shoutout", json=payload, verify=False)
        print(f"POST Status: {resp.status_code}")
        print(f"POST Response: {resp.text}")
        
        if resp.status_code != 200:
            print("FAILED: POST returned non-200")
            return
            
    except Exception as e:
        print(f"POST Error: {e}")
        return

    # 2. Get Shoutouts
    print("\nfetching history...")
    try:
        resp = requests.get(f"{BASE_URL}/shoutouts", verify=False)
        print(f"GET Status: {resp.status_code}")
        data = resp.json()
        
        found = False
        for s in data:
            print(f"- {s.get('sender')}: {s.get('message')}")
            if s.get('message') == payload['message']:
                found = True
        
        if found:
            print("\nSUCCESS: Sent message found in history!")
        else:
            print("\nFAILED: Message not found in history.")
            
    except Exception as e:
        print(f"GET Error: {e}")

if __name__ == "__main__":
    test_shoutouts()
