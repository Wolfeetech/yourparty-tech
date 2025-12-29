
import requests
import json

# Disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    resp = requests.get(
        'https://radio.yourparty.tech/api/stations', 
        headers={'Authorization': 'Bearer 19dc63da6223190:c9f8cc3a22e25932753dd3f4d57fa0d9'}, 
        verify=False
    )
    stations = resp.json()
    print("--- STATIONS ---")
    for s in stations:
        print(f"ID: {s.get('id')} | Name: {s.get('name')} | Short: {s.get('short_name')}")
    print("----------------")
except Exception as e:
    print(f"Error: {e}")
