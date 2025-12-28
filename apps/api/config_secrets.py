"""
SECRETS FILE
------------
Please fill in the values below to enable the automation scripts.
This file is ignored by git (or should be).
"""
import os

# 1. Music Assistant (Home Assistant)
# Generate this in HA Profile -> Security -> Create Long-Lived Access Token
# 1. Music Assistant (Home Assistant)
# Generate this in HA Profile -> Security -> Create Long-Lived Access Token
MASS_TOKEN = os.getenv("MASS_TOKEN", "RXq_nQKdsyk1Z0DIj0_MXUs_OEp_cN7Wjt2kPX_e8mREXPawY0ZITBuY0BBvNVKg")
MASS_URL = os.getenv("MASS_URL", "http://192.168.178.179:8123") # Updated to correct HA IP

# 2. NAS / File Server (SMB)
# Credentials to mount \\192.168.178.120\music (or correct share)
SMB_SERVER = os.getenv("SMB_SERVER", "192.168.178.120")
SMB_SHARE = os.getenv("SMB_SHARE", "music") # Change if 'public', 'share' etc.
SMB_USERNAME = os.getenv("SMB_USERNAME", "wolf")
SMB_PASSWORD = os.getenv("SMB_PASSWORD", "YpWolf2024!")

# 3. MongoDB (Found in config, but good to keep here)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin")

# 4. AzuraCast (Radio)
AZURACAST_API_URL = os.getenv("AZURACAST_API_URL", "http://192.168.178.210/api") # Updated to match .env
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
AZURACAST_STATION_ID = int(os.getenv("AZURACAST_STATION_ID", 1))
