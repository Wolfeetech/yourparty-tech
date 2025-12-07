#!/usr/bin/env python3
"""
Script to discover MongoDB connection details from AzuraCast instance.
"""

import requests
import json
import sys

AZURACAST_URL = "http://192.168.178.210"
AZURACAST_API_KEY = "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c"
STATION_ID = 1

# Common MongoDB connection patterns for AzuraCast
POTENTIAL_CONNECTIONS = [
    # Local MongoDB on AzuraCast VM
    "mongodb://localhost:27017/",
    "mongodb://127.0.0.1:27017/",
    
    # Docker internal network
    "mongodb://mongo:27017/",
    "mongodb://azuracast-mongo:27017/",
    
    # With authentication (common AzuraCast defaults)
    "mongodb://azuracast:azuracast@localhost:27017/",
    "mongodb://azuracast:azuracast@mongo:27017/",
    
    # External access from Windows host
    f"mongodb://192.168.178.210:27017/",
    f"mongodb://azuracast:azuracast@192.168.178.210:27017/",
]

DATABASE_NAMES = [
    "azuracast",
    "radio_ratings", 
    "ratings",
    "azuracast_ratings"
]

def test_azuracast_api():
    """Test if AzuraCast API is reachable."""
    print(f"[*] Testing AzuraCast API at {AZURACAST_URL}...")
    
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    try:
        # Try to get station info
        response = requests.get(
            f"{AZURACAST_URL}/api/station/{STATION_ID}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"[+] AzuraCast API is reachable!")
            data = response.json()
            print(f"    Station: {data.get('name', 'Unknown')}")
            return True
        else:
            print(f"[-] API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[-] API request failed: {e}")
        return False

def test_mongodb_port():
    """Check if MongoDB port is accessible."""
    import socket
    
    print(f"\n[*] Testing MongoDB port accessibility...")
    
    # Test localhost (if script runs on VM)
    for host in ["localhost", "127.0.0.1", "192.168.178.210"]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        result = sock.connect_ex((host, 27017))
        if result == 0:
            print(f"[+] Port 27017 is OPEN on {host}")
        else:
            print(f"[-] Port 27017 is CLOSED on {host}")
        sock.close()

def test_mongodb_connections():
    """Test potential MongoDB connections."""
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
    
    print(f"\n[*] Testing MongoDB connections...")
    
    successful_connections = []
    
    for conn_str in POTENTIAL_CONNECTIONS:
        for db_name in DATABASE_NAMES:
            try:
                print(f"\n[*] Trying: {conn_str} / {db_name}")
                
                client = MongoClient(
                    conn_str,
                    serverSelectionTimeoutMS=3000,
                    connectTimeoutMS=3000
                )
                
                # Try to access the database
                db = client[db_name]
                
                # Try to list collections (this will fail if auth is wrong)
                collections = db.list_collection_names()
                
                print(f"[+] SUCCESS! Connected to {db_name}")
                print(f"    Collections: {collections}")
                
                successful_connections.append({
                    "connection_string": conn_str,
                    "database": db_name,
                    "collections": collections
                })
                
                client.close()
                
            except OperationFailure as e:
                print(f"[-] Authentication failed: {e}")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                print(f"[-] Connection failed: {type(e).__name__}")
            except Exception as e:
                print(f"[-] Error: {e}")
    
    return successful_connections

def main():
    print("="*60)
    print("AzuraCast MongoDB Discovery Tool")
    print("="*60)
    
    # Step 1: Test AzuraCast API
    api_ok = test_azuracast_api()
    
    if not api_ok:
        print("\n[!] Warning: AzuraCast API is not reachable!")
        print("    Make sure the VM is running and accessible.")
    
    # Step 2: Test MongoDB port
    test_mongodb_port()
    
    # Step 3: Try MongoDB connections
    successful = test_mongodb_connections()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if successful:
        print(f"\n[+] Found {len(successful)} working connection(s):\n")
        for i, conn in enumerate(successful, 1):
            print(f"{i}. Connection String: {conn['connection_string']}")
            print(f"   Database: {conn['database']}")
            print(f"   Collections: {', '.join(conn['collections'])}")
            print()
            
        # Write to file
        with open("mongodb_config.json", "w") as f:
            json.dump(successful[0], f, indent=2)
        print("[+] Config saved to: mongodb_config.json")
    else:
        print("\n[-] No working MongoDB connections found!")
        print("\nPossible reasons:")
        print("  1. MongoDB is not running on the AzuraCast VM")
        print("  2. MongoDB port (27017) is not exposed")
        print("  3. Firewall blocking the connection")
        print("  4. Different credentials needed")
        print("\nNext steps:")
        print("  - SSH into the AzuraCast VM")
        print("  - Run: docker ps | grep mongo")
        print("  - Check: docker-compose.yml for MongoDB config")

if __name__ == "__main__":
    main()
