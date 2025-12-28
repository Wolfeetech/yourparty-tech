import requests
import time
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stream_health.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

STREAM_URL = "https://radio.yourparty.tech/listen/yourparty/radio.mp3"
CHECK_INTERVAL = 5  # Seconds

def check_stream():
    logging.info(f"Starting professional stream monitor for {STREAM_URL}")
    print(f"Monitoring {STREAM_URL} (Interval: {CHECK_INTERVAL}s)...")
    
    while True:
        try:
            start_time = time.time()
            # Stream=True to avoid downloading the whole file, just headers and first chunk
            with requests.get(STREAM_URL, stream=True, timeout=5, verify=False) as r:
                latency = (time.time() - start_time) * 1000
                
                if r.status_code == 200:
                    # Try to read a small chunk to ensure data is flowing
                    chunk = next(r.iter_content(chunk_size=1024), None)
                    if chunk:
                        logging.info(f"✅ UP | Latency: {latency:.2f}ms | Status: {r.status_code}")
                    else:
                        logging.warning(f"⚠️ EMPTY | Latency: {latency:.2f}ms | Stream connected but no data")
                else:
                    logging.error(f"❌ DOWN | Status: {r.status_code} | Latency: {latency:.2f}ms")
                    
        except requests.exceptions.Timeout:
            logging.error("❌ TIMEOUT | Connection timed out (>5s)")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"❌ CONNECTION ERROR | {e}")
        except Exception as e:
            logging.error(f"❌ ERROR | {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_stream()
