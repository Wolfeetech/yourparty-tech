import asyncio
import websockets
import json
import httpx
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/1"
TIMEOUT = 5

async def test_realtime_steer():
    logging.info(f"Connecting to {WS_URL}...")
    try:
        # 0. Get Token
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/token", data={"username": "admin", "password": "admin"})
            if resp.status_code != 200:
                logging.error(f"❌ Login Failed: {resp.text}")
                return
            token = resp.json()["access_token"]
            logging.info("✅ Login Successful, Token acquired.")

        async with websockets.connect(WS_URL) as websocket:
            # 1. Wait for initial 'song' message
            init_msg = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
            init_data = json.loads(init_msg)
            logging.info(f"Received Initial: {init_data.get('type')}")
            
            # 2. Trigger Steering Change (Manual)
            target = "energetic"
            logging.info("Triggering Steering Change -> MANUAL / ENERGETIC")
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_URL}/control/steer", 
                    json={
                        "station_id": 1,
                        "mode": "manual",
                        "target": target
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                logging.info(f"API Response: {resp.status_code}")
                if resp.status_code != 200:
                    logging.error(f"❌ API FAILED: {resp.text}")
                    return
                assert resp.status_code == 200

            # 3. Wait for 'steer' broadcast
            logging.info("Waiting for WebSocket Broadcast...")
            
            # Loop because we might get other messages (pulse, song)
            found = False
            start = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start < TIMEOUT:
                msg = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                data = json.loads(msg)
                logging.info(f"Received WS Message: {data.get('type')}")
                
                if data.get('type') == 'steer':
                    steer_data = data.get('data', {})
                    if steer_data.get('mode') == 'manual' and steer_data.get('target') == target:
                        logging.info("✅ SUCCESS: Received correct Steering Update via WS")
                        found = True
                        break
            
            if not found:
                logging.error("❌ FAILED: Did not receive steering update in time")
                
            # 4. Reset to Auto
            logging.info("Resetting to AUTO...")
            async with httpx.AsyncClient() as client:
                 await client.post(f"{API_URL}/control/steer", json={
                    "station_id": 1,
                    "mode": "auto",
                    "target": None
                })

    except Exception as e:
        logging.error(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_realtime_steer())
