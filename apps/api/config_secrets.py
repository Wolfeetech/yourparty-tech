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
# Credentials to mount \\192.168.178.25\music (or correct share)
SMB_SERVER = os.getenv("SMB_SERVER", "192.168.178.25")
SMB_SHARE = os.getenv("SMB_SHARE", "music") # Change if 'public', 'share' etc.
SMB_USERNAME = os.getenv("SMB_USERNAME", "wolf")
SMB_PASSWORD = os.getenv("SMB_PASSWORD", "YpWolf2024!")

# Library Root (Single Source of Truth)
LIBRARY_SUBDIR = os.getenv("LIBRARY_SUBDIR", "yourparty_Libary")
LIBRARY_UNC = os.getenv(
    "LIBRARY_UNC",
    rf"\\{SMB_SERVER}\{SMB_SHARE}\{LIBRARY_SUBDIR}"
)
LIBRARY_ROOT_WIN = os.getenv("LIBRARY_ROOT_WIN", rf"Z:\{LIBRARY_SUBDIR}")
LIBRARY_ROOT_LINUX = os.getenv(
    "LIBRARY_ROOT_LINUX",
    f"/var/radio/music/{LIBRARY_SUBDIR}"
)

# 3. MongoDB (Found in config, but good to keep here)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin")

# 4. AzuraCast (Radio)
AZURACAST_API_URL = os.getenv("AZURACAST_API_URL", "https://radio.yourparty.tech/api")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "b67d671461fd35d0:9ba6fc04467491f28c29caf8895a5ca7")
AZURACAST_STATION_ID = int(os.getenv("AZURACAST_STATION_ID", 1))

# 5. Smart Tagging Rules (Dynamic Genre Mapping)
# Maps partial genre/folder names to Vibes
MOOD_RULES = {
    "Energy": [
        "Tech House", "Techno", "Drum & Bass", "Dubstep", "Peak Time", 
        "Driving", "Hard Techno", "Bass House", "Electro", "Big Room"
    ],
    "Euphoric": [
        "Melodic House & Techno", "Trance", "Progressive House", "Indie Dance", 
        "Disco", "Nu Disco", "Future House", "Mainstage", "Anthem"
    ],
    "Chill": [
        "Deep House", "Afro House", "Organic House", "Minimal", "Deep Tech", 
        "Downtempo", "Lounge", "Electronica", "Ambient", "R&B", "Soul"
    ]
}
AZURACAST_VERIFY_SSL = os.getenv("AZURACAST_VERIFY_SSL", "true").lower() == "true"
