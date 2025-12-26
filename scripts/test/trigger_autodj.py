import asyncio
import os
import sys

# Add app directory to path
sys.path.insert(0, "/opt/radio-api")

from mood_scheduler import mood_queue_worker_iteration
from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient

async def run_manual_autodj():
    print("Initializing clients...")
    mongo = MongoDatabaseClient(os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/yourparty"))
    azura = AzuraCastClient(
        os.getenv("AZURACAST_URL"), 
        os.getenv("AZURACAST_API_KEY"), 
        1
    )
    
    print("Running Auto-DJ Iteration...")
    result = await mood_queue_worker_iteration(mongo, azura)
    
    print(f"\n✅ Auto-DJ Result: {result}")
    
    # Check what passed through
    # Note: mood_scheduler logs to logger, so we might not see stdout unless configured, 
    # but the True/False result tells us if it worked.

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("/opt/radio-api/.env")
    asyncio.run(run_manual_autodj())
