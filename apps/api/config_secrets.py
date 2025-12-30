"""
SECRETS FILE
------------
All secrets MUST be provided via environment variables.
See .env.example for required variables.
This file only reads from environment - no hardcoded secrets!
"""
import os

def _require_env(name: str) -> str:
    """Get required environment variable or raise error."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Required environment variable '{name}' is not set. Check .env file.")
    return value

def _env(name: str, default: str = "") -> str:
    """Get optional environment variable with default."""
    return os.getenv(name, default)

# 1. Music Assistant (Home Assistant)
MASS_TOKEN = _env("MASS_TOKEN")
MASS_URL = _env("MASS_URL", "http://192.168.178.179:8123")

# 2. NAS / File Server (SMB)
SMB_SERVER = _env("SMB_SERVER", "192.168.178.25")
SMB_SHARE = _env("SMB_SHARE", "music")
SMB_USERNAME = _env("SMB_USERNAME")
SMB_PASSWORD = _env("SMB_PASSWORD")

# Library Root (Single Source of Truth)
LIBRARY_SUBDIR = _env("LIBRARY_SUBDIR", "yourparty_Libary")
LIBRARY_UNC = _env(
    "LIBRARY_UNC",
    rf"\\{SMB_SERVER}\{SMB_SHARE}\{LIBRARY_SUBDIR}" if SMB_SERVER else ""
)
LIBRARY_ROOT_WIN = _env("LIBRARY_ROOT_WIN", rf"Z:\{LIBRARY_SUBDIR}")
LIBRARY_ROOT_LINUX = _env(
    "LIBRARY_ROOT_LINUX",
    f"/var/radio/music/{LIBRARY_SUBDIR}"
)

# 3. MongoDB - REQUIRED
MONGO_URI = _require_env("MONGO_URI")

# 4. AzuraCast (Radio) - REQUIRED
AZURACAST_API_URL = _require_env("AZURACAST_API_URL")
AZURACAST_API_KEY = _require_env("AZURACAST_API_KEY")
AZURACAST_STATION_ID = int(_env("AZURACAST_STATION_ID", "1"))
AZURACAST_VERIFY_SSL = _env("AZURACAST_VERIFY_SSL", "true").lower() == "true"

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
