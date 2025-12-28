"""
SECRETS FILE
------------
Please fill in the values below to enable the automation scripts.
This file is ignored by git (or should be).
"""

# 1. Music Assistant (Home Assistant)
# Generate this in HA Profile -> Security -> Create Long-Lived Access Token
MASS_TOKEN = "RXq_nQKdsyk1Z0DIj0_MXUs_OEp_cN7Wjt2kPX_e8mREXPawY0ZITBuY0BBvNVKg"
MASS_URL = "http://192.168.178.67:8095"

# 2. NAS / File Server (SMB)
# Credentials to mount \\192.168.178.120\music (or correct share)
SMB_SERVER = "192.168.178.120"
SMB_SHARE = "music" # Change if 'public', 'share' etc.
SMB_USERNAME = "wolf"
SMB_PASSWORD = "YpWolf2024!"

# 3. MongoDB (Found in config, but good to keep here)
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"

# 4. AzuraCast (Radio)
AZURACAST_API_URL = "https://192.168.178.210/api" # Internal Network Speed
AZURACAST_API_KEY = "8aa6ccfc64d9d32e:dcf81da2e093ef61a332025c2e7c09fb"
AZURACAST_STATION_ID = 1
