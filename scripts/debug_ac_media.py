
import os
import requests
import json
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings()
load_dotenv('/opt/radio-api/.env')
load_dotenv()

API_URL = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech/api").rstrip('/')
if not API_URL.endswith('/api'):
     API_URL += '/api'
     
API_KEY = os.getenv("AZURACAST_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def debug():
    url = f"{API_URL}/station/1/files"
    print(f"Debug URL: {url}")
    print(f"API Key: {API_KEY[:4]}...{API_KEY[-4:] if API_KEY else 'NONE'}")
    
    try:
        r = requests.get(url, headers=HEADERS, verify=False)
        print(f"Status: {r.status_code}")
        
        try:
            data = r.json()
            if isinstance(data, list):
                print(f"Got LIST of {len(data)} items.")
                if len(data) > 0:
                    print(f"Sample: {json.dumps(data[0], indent=2)}")
            elif isinstance(data, dict):
                print(f"Got DICT with keys: {data.keys()}")
                if 'rows' in data:
                     print(f"Rows count: {len(data['rows'])}")
            else:
                print(f"Got unexpected type: {type(data)}")
                print(r.text[:500])
        except Exception as e:
             print(f"JSON Decode Error: {e}")
             print("Response Text:", r.text[:500])
             
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    debug()
