import logging
import asyncio
from state import state

logger = logging.getLogger(__name__)

class BackgroundSyncer:
    """
    Decoupled Syncer: Fetches data from slow upstream APIs (AzuraCast)
    and caches it in high-speed MongoDB for instant read access.
    """
    
    def __init__(self):
        self.is_running = False

    async def start(self):
        """Start the background sync loop."""
        self.is_running = True
        logger.info("Background Syncer Started")
        
        while self.is_running:
            try:
                await self.sync_playlists()
            except Exception as e:
                logger.error(f"Syncer Error: {e}")
            
            # Sync every 5 minutes (300s)
            await asyncio.sleep(300)

    async def sync_playlists(self):
        """Fetch playlists from AzuraCast and save to MongoDB."""
        if not state.azura_client or not state.mongo_client:
            logger.warning("Syncer: Clients not ready yet")
            return

        logger.info("Syncer: Fetching playlists from AzuraCast...")
        try:
            # 1. Slow Read
            playlists = await state.azura_client.get_playlists()
            
            # 2. Fast Write
            if playlists:
                success = state.mongo_client.save_playlists(playlists)
                if success:
                    logger.info(f"Syncer: Successfully cached {len(playlists)} playlists")
            else:
                logger.warning("Syncer: No playlists returned from AzuraCast")
                
        except Exception as e:
            logger.error(f"Syncer: Failed to sync playlists: {e}")

syncer = BackgroundSyncer()
