#!/usr/bin/env python3
import click
import asyncio
import os
import uvicorn
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enrich_ratings import enrich_metadata

@click.group()
def cli():
    """YourParty Radio Manager"""
    pass

@cli.command()
def enrich():
    """Enrich ratings with metadata from AzuraCast"""
    print("Starting enrichment...")
    asyncio.run(enrich_metadata())

@cli.command()
def sync_library():
    """Sync AzuraCast Media IDs to MongoDB"""
    
    async def _sync():
        try:
            from mongo_client import MongoDatabaseClient
            from azuracast_client import AzuraCastClient
            from library_service import get_library_service
            from config_secrets import MONGO_URI, AZURACAST_URL, AZURACAST_API_KEY
            
            print("Connecting to MongoDB...")
            mongo = MongoDatabaseClient(MONGO_URI)
            
            print("Connecting to AzuraCast...")
            azura = AzuraCastClient(AZURACAST_URL, AZURACAST_API_KEY or "", 1)
            
            service = get_library_service(mongo)
            
            print("Starting Library Sync...")
            result = await service.sync_azuracast_ids(azura)
            print(f"Sync Result: {result}")
            
        except Exception as e:
            print(f"Error during sync: {e}")

    asyncio.run(_sync())

@cli.command()
def run_api():
    """Run the API server"""
    print("Starting API...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == '__main__':
    cli()
