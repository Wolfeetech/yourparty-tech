import asyncio
import json
import logging
import aiohttp
from music_assistant_client import MusicAssistantClient
from music_assistant_models.config_entries import ConfigEntry

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MassSetup")

from secrets import MASS_TOKEN, MASS_URL

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MassSetup")

async def main():
    async with aiohttp.ClientSession() as session:
        # MusicAssistantClient expects (url, session, token)
        async with MusicAssistantClient(MASS_URL, session, MASS_TOKEN) as client:
            logger.info("Connected to Music Assistant!")
            
            try:
                # 1. List Providers
                logger.info("\n--- PROVIDERS ---")
                providers = await client.providers.get_providers() # Adjusted accessor if needed
                for p in providers:
                    logger.info(f"[{p.domain}] {p.name} (Instance ID: {p.instance_id})")
            except Exception as e:
                logger.error(f"Error listing providers: {e}")

        # 2. List Config Entries (Actual configurations)
        logger.info("\n--- CONFIG ENTRIES ---")
        # Note: Client library usage might differ slightly, trying best guess or standard method
        # If get_config_entries doesn't exist, we might need to use raw commands
        try:
             # Depending on client version, this might be under client.config
             # Using lower level access if needed
             pass
        except Exception:
             pass

        # 3. Check for SMB Provider specifically
        has_smb = False
        for p in providers:
            if p.domain == 'smb' or 'smb' in p.name.lower():
                has_smb = True
                logger.info(f"✅ SMB Provider Found: {p.name}")
        
        if not has_smb:
            logger.warning("❌ No SMB Provider found! We need to add one.")
            # Note: Adding provider requires interactive config usually.
            # We can try to dry-run the add command structure.

        # 4. List Players
        logger.info("\n--- PLAYERS ---")
        players = await client.players.get_players()
        for player in players:
             logger.info(f"[{player.player_id}] {player.name} ({player.state})")
        
        # 5. Get Library Stats
        logger.info("\n--- LIBRARY ---")
        tracks = await client.music.get_library_tracks()
        logger.info(f"Tracks in Library: {len(tracks)}")
        if tracks:
            sample = tracks[0]
            logger.info(f"Sample Track: {sample.name} - {sample.artist.name if sample.artist else 'Unknown'}")

            # Check metadata
            logger.info(f"Metadata: {sample.metadata}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed: {e}")
