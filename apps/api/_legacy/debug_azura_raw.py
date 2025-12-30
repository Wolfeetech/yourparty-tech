import requests
import json
from apps.api.secrets import AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

url = f"{AZURACAST_API_URL}/api/station/{AZURACAST_STATION_ID}/files"
headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

print(f"Fetch: {url}")
try:
    resp = requests.get(url, headers=headers, verify=False)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Keys:", data.keys() if isinstance(data, dict) else "List")
        print("Raw:", json.dumps(data, indent=2)[:500]) # First 500 chars
    else:
        print("Error:", resp.text)
except Exception as e:
    print(f"Exception: {e}")
