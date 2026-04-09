import asyncio
import logging
import time
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager import LibraryManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LibraryService")

async def run_loop():
    logger.info("📡 Starting Library Manager Service Loop...")
    manager = LibraryManager()
    
    while True:
        try:
            logger.info("👀 Checking Inbox...")
            await manager.process_inbox()
        except Exception as e:
            logger.error(f"Error in process loop: {e}")
        
        # Wait 60 seconds before next scan
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(run_loop())
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user.")
