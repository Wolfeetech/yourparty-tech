import requests
import time
import logging
import sys
import os

# Configure logging
# Force UTF-8 for file output
file_handler = logging.FileHandler("stream_health.log", encoding='utf-8')
console_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)

# Use the specific station endpoint that mimics the browser player
STREAM_URL = "https://radio.yourparty.tech/listen/yourparty/radio.mp3"
API_URL = "https://radio.yourparty.tech/api/nowplaying/yourparty"
CHECK_INTERVAL = 5  # Seconds

def safe_print(msg):
    try:
        logging.info(msg)
    except UnicodeEncodeError:
        # Fallback for Windows consoles that don't support emojis
        clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
        logging.info(clean_msg)

def check_stream():
    safe_print(f"Starting professional stream monitor for {STREAM_URL}")
    print(f"Monitoring {STREAM_URL} (Interval: {CHECK_INTERVAL}s)...")
    
    # First verify the URL from API
    try:
        r = requests.get(API_URL, timeout=5, verify=False)
        if r.status_code == 200:
            data = r.json()
            listen_url = data.get('station', {}).get('listen_url', STREAM_URL)
            safe_print(f"Verified Listen URL: {listen_url}")
            monitor_url = listen_url
        else:
            monitor_url = STREAM_URL
    except Exception as e:
        safe_print(f"Warning: Could not fetch API info: {e}")
        monitor_url = STREAM_URL

    while True:
        try:
            start_time = time.time()
            # Stream=True to avoid downloading the whole file
            with requests.get(monitor_url, stream=True, timeout=5, verify=False) as r:
                latency = (time.time() - start_time) * 1000
                
                if r.status_code == 200:
                    # Try to read a small chunk to ensure data is flowing
                    chunk = next(r.iter_content(chunk_size=1024), None)
                    if chunk:
                        safe_print(f"✅ UP | Latency: {latency:.2f}ms | Status: {r.status_code}")
                    else:
                        safe_print(f"⚠️ EMPTY | Latency: {latency:.2f}ms | Stream connected but no data")
                else:
                    safe_print(f"❌ DOWN | Status: {r.status_code} | Latency: {latency:.2f}ms")
                    
        except requests.exceptions.Timeout:
            safe_print("❌ TIMEOUT | Connection timed out (>5s)")
        except requests.exceptions.ConnectionError as e:
            safe_print(f"❌ CONNECTION ERROR | {e}")
        except Exception as e:
            safe_print(f"❌ ERROR | {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_stream()
