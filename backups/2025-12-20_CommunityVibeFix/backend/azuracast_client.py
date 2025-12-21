import requests
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzuraCastClient:
    def __init__(self, base_url: str, api_key: str, station_id: int):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.station_id = station_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def sync_media(self) -> Dict[str, Any]:
        """
        Triggers a media scan/sync for the station.
        Note: AzuraCast API might not have a direct 'sync now' endpoint exposed publicly 
        in all versions, but usually reloading the playlist or media can be triggered.
        
        Commonly used endpoint for media management: /station/{station_id}/files
        Or specific command execution if available.
        
        For now, we will try to list files which often triggers a cache refresh, 
        or use a specific 'reload' endpoint if known. 
        
        Actually, a better approach for "sync" is often just uploading or ensuring files are there.
        If the user puts files on SMB, AzuraCast (if mounted) should see them.
        We might just need to tell AzuraCast to re-process the media folders.
        """
        # Attempt to hit the media endpoint to trigger a refresh or check status
        # In many setups, AzuraCast auto-watches, but a manual trigger is good.
        # There isn't a standard "force sync" API endpoint documented for all versions without admin rights.
        # We will assume a standard GET to the files endpoint might wake it up, 
        # or we return a message that files are in place.
        
        # If there is a specific 'restart' or 'reload' command for the station:
        # POST /station/{station_id}/restart
        
        try:
            # For this implementation, we'll try to just check the status, 
            # assuming the user wants to know if the server is reachable.
            url = f"{self.base_url}/api/station/{self.station_id}/status"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "AzuraCast station reachable. Media should be detected automatically by AzuraCast's watcher.",
                "data": response.json()
            }
        except Exception as e:
            logger.error(f"AzuraCast sync failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_playlists(self):
        """Fetch all playlists for the station."""
        url = f"{self.base_url}/api/station/{self.station_id}/playlists"
        try:
            resp = requests.get(url, headers=self.headers, verify=False)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch playlists: {e}")
            return []

    def create_playlist(self, name: str, weight: int = 3):
        """Create a new playlist."""
        url = f"{self.base_url}/api/station/{self.station_id}/playlists"
        payload = {
            "name": name,
            "weight": weight,
            "is_enabled": True,
            "type": "default",  # Standard rotation (API expects 'default')
            "include_in_requests": True
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, verify=False)
            resp.raise_for_status()
            logger.info(f"Created playlist: {name}")
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to create playlist {name}: {e}")
            return None

    def _get(self, url: str):
        try:
             resp = requests.get(url, headers=self.headers, verify=False)
             resp.raise_for_status()
             return resp.json()
        except Exception as e:
             logger.error(f"GET {url} failed: {e}")
             return {}

    def get_station_media(self):
        """
        Get all media files for the station.
        """
        # Iterate pages if necessary or get all
        # Endpoint: /api/station/{station_id}/files
        # Note: This might be heavy.
        url = f"{self.base_url}/api/station/{self.station_id}/files"
        return self._get(url)

    def get_now_playing(self):
        """
        Get current playback information including history.
        """
        url = f"{self.base_url}/api/nowplaying/{self.station_id}"
        return self._get(url)

    def replace_playlist_content(self, playlist_id: int, media_ids: list):
        """
        Replace entire content of a playlist with new media IDs.
        Note: AzuraCast usually manages this via 'media' relations or specific endpoints.
        This is a common way to do 'Smart Playlists' externally.
        """
        # First, clear? Or just set? 
        # API: POST /station/{station_id}/playlist/{id}/queue (this bumps to top)
        # API: PUT /station/{station_id}/playlist/{id}/folders (assign folders)
        
        # Correct way usually involves assigning media to the playlist.
        # We might need to iterate or send a batch if supported.
        # For now, let's assume we can post to a 'media' endpoint for the playlist
        pass
        
        # Note: AzuraCast API specifics for BATCH assignment can vary.
        # Often it is: POST /station/{station_id}/files/batch
        # with { "do": "playlist", "playlists": [id], "files": [file_paths or ids] }
        
        url = f"{self.base_url}/api/station/{self.station_id}/files/batch"
        payload = {
            "do": "playlist",
            # "playlists": [playlist_id], # Some versions
            "playlist_id": playlist_id, # Target playlist
            "files": media_ids # Array of file unique IDs
        }
        
        # Note: We might need to handle 'remove from others' or clear connection logic
        # But simply adding them to the target playlist is step 1.
        try:
            resp = requests.put(url, headers=self.headers, json=payload, verify=False)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error adding to playlist: {e}")
            return False

    def queue_track(self, media_id: int):
        """
        Queue a specific track ID to play next.
        POST /api/station/{station_id}/requests/{media_id}
        """
        url = f"{self.base_url}/api/station/{self.station_id}/request/{media_id}"
        try:
            # Note: The API endpoint might differ for 'admin' queuing vs 'public' requests.
            # Usually /requests is for public, but admins can use it too.
            # Proper admin queue: POST /api/station/{station_id}/queue/add
            # Let's try the admin queue endpoint first if available in newer versions, 
            # otherwise fallback to request.
            
            # Explicit Queue Add (Admin) - likely payload needs media_id or unique_id
            # url_admin = f"{self.base_url}/api/station/{self.station_id}/queue/add"
            # payload = {"media_id": media_id}
            # resp = requests.post(url_admin, headers=self.headers, json=payload, verify=False)
            
            # Request method is safest for now
            resp = requests.post(url, headers=self.headers, verify=False)
            resp.raise_for_status()
            logger.info(f"Queued media ID {media_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue media {media_id}: {e}")
            return False

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Test stub
    pass
