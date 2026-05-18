import requests
import json
import os

API_KEY = "b67d671461fd35d0:9ba6fc04467491f28c29caf8895a5ca7"
BASE_URL = "http://192.168.178.210/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_api():
    url = f"{BASE_URL}/stations"
    print(f"Testing API: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            stations = resp.json()
            print(f"STATIONS_FOUND:{len(stations)}")
            for s in stations:
                sid = s['id']
                print(f"SID:{sid}|NAME:{s['name']}")
                
                f_resp = requests.get(f"{BASE_URL}/station/{sid}/files", headers=headers, timeout=10, verify=False)
                print(f"  FILES_COUNT:{len(f_resp.json()) if f_resp.status_code == 200 else 'ERR'}")
                
                m_resp = requests.get(f"{BASE_URL}/station/{sid}/media", headers=headers, timeout=10, verify=False)
                print(f"  MEDIA_COUNT:{len(m_resp.json()) if m_resp.status_code == 200 else 'ERR'}")

                np_resp = requests.get(f"{BASE_URL}/nowplaying/{sid}", headers=headers, timeout=10, verify=False)
                if np_resp.status_code == 200:
                    cur = np_resp.json().get('now_playing', {}).get('song', {})
                    print(f"  NP:{cur.get('text', 'N/A')}|ID:{cur.get('id', 'N/A')}")
                else:
                    print(f"  NP_ERR:{np_resp.status_code}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()
