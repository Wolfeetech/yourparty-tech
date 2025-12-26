import requests

# 2. Simulate Frontend User Vote (via Proxy)
print("Simulating Frontend Vote (via WP Proxy)...")
proxy_url = "https://yourparty.tech/wp-json/yourparty/v1/vote-next-mood"
payload = {
    "song_id": "proxy_verify_id",
    "mood_next": "energy"
}

# Note: In this environment, we might need to resolve 'yourparty.tech' manually 
# if external DNS isn't perfect, but let's try standard first.
try:
    # 1. Try Public URL
    print(f"POST {proxy_url}")
    response = requests.post(proxy_url, json=payload, verify=False, timeout=10)
    print(f"Proxy Response: {response.status_code}")
    print(f"Proxy Body: {response.text}")
    
    if response.status_code == 200:
         data = response.json()
         print("✅ SUCCESS: Proxy vote accepted!")
         print(f"🗳️ Dominant Next Mood: {data.get('dominant_next', 'None')} (Should be 'energy' or similar)")
    else:
         print("❌ FAILURE: Proxy vote rejected.")

except Exception as e:
    print(f"Proxy Request Failed: {e}")
