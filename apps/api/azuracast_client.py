import httpx
import logging
import os
import urllib3
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")

class AzuraCastClient:
    def __init__(self, base_url: str, api_key: str, station_id: int, verify_ssl: Optional[bool] = None):
        self.base_url = base_url.rstrip('/').rstrip('/api')
        self.api_key = api_key
        self.station_id = station_id
        self.verify_ssl = _env_bool("AZURACAST_VERIFY_SSL", False) if verify_ssl is None else bool(verify_ssl)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = 10.0
        if not self.verify_ssl:
            # Suppress InsecureRequestWarning when SSL verification is intentionally disabled.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    async def _get(self, url: str) -> Any:
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f"GET {url} failed: {e}")
                return {}

    async def _post(self, url: str, json: Optional[Dict] = None) -> Any:
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.post(url, headers=self.headers, json=json)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f"POST {url} failed: {e}")
                return None

    async def _put(self, url: str, json: Optional[Dict] = None) -> Any:
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.put(url, headers=self.headers, json=json)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f"PUT {url} failed: {e}")
                return None

    async def sync_media(self, station_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Triggers a media scan/check.
        """
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/status"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                return {
                    "success": True,
                    "message": "AzuraCast station reachable.",
                    "data": resp.json()
                }
            except Exception as e:
                logger.error(f"AzuraCast sync failed: {e}")
                return {"success": False, "error": str(e)}

    async def get_playlists(self, station_id: Optional[int] = None) -> List[Dict]:
        """Fetch all playlists for the station."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlists"
        res = await self._get(url)
        return res if isinstance(res, list) else []

    async def create_playlist(self, name: str, weight: int = 3, station_id: Optional[int] = None):
        """Create a new playlist."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlists"
        payload = {
            "name": name,
            "weight": weight,
            "is_enabled": True,
            "type": "default",
            "include_in_requests": True
        }
        res = await self._post(url, json=payload)
        if res:
             logger.info(f"Created playlist: {name}")
        return res

    async def get_station_media(self, station_id: Optional[int] = None) -> List[Dict]:
        """Get all media files for the station."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/files"
        logger.info(f"Fetching media from {url} (using requests)")
        try:
            # Fallback to sync requests because httpx is acting up on this env
            import requests
            resp = requests.get(url, headers=self.headers, verify=self.verify_ssl, timeout=30)
            resp.raise_for_status()
            res = resp.json()
        except Exception as e:
            logger.error(f"Requests GET failed: {e}")
            res = []
            
        logger.info(f"Media Response Type: {type(res)}")
        if isinstance(res, list):
             logger.info(f"Media Count: {len(res)}")
        else:
             logger.info(f"Media Response Content (First 100): {str(res)[:100]}")
        return res if isinstance(res, list) else []

    async def get_now_playing(self, station_id: Optional[int] = None):
        """Get current playback information including history."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/nowplaying/{sid}"
        return await self._get(url)

    async def replace_playlist_content(self, playlist_id: int, media_ids: list, station_id: Optional[int] = None) -> bool:
        """Replace entire content of a playlist with new media IDs."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/files/batch"
        payload = {
            "do": "playlist",
            "playlists": [playlist_id], 
            "files": [str(mid) for mid in media_ids]
        }
        res = await self._put(url, json=payload)
        return bool(res)

    async def queue_track(self, media_id, station_id: Optional[int] = None) -> bool:
        """Queue a specific track by numeric ID or unique_id (hash) to play next."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/request/{media_id}"
        # Requests don't return JSON body always, just 204 or 200
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.post(url, headers=self.headers)
                resp.raise_for_status()
                logger.info(f"Queued media ID {media_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to queue media {media_id}: {e}")
                return False

    async def skip_current_song(self, station_id: Optional[int] = None) -> bool:
        """Skip the currently playing song."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/backend/skip"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.post(url, headers=self.headers)
                resp.raise_for_status()
                logger.info("Skipped current song successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to skip song: {e}")
                return False

    async def get_upcoming_queue(self, station_id: Optional[int] = None) -> List[Dict]:
        """
        Get the list of tracks currently in the queue (playing_next).
        """
        data = await self.get_now_playing(station_id)
        if not data:
            return []
        
        playing_next = data.get('playing_next')
        if not playing_next:
            return []

        return playing_next.get('song_history', [])

    async def add_to_playlist(self, media_id: int, playlist_name: str, station_id: Optional[int] = None) -> bool:
        """Add a media item to a specific playlist (by name)."""
        playlists = await self.get_playlists(station_id)
        
        target_playlist = next((p for p in playlists if p['name'].lower() == playlist_name.lower()), None)
        
        if not target_playlist:
            logger.info(f"Playlist '{playlist_name}' not found. Creating it...")
            target_playlist = await self.create_playlist(playlist_name, station_id=station_id)
            if not target_playlist:
                return False
        
        playlist_id = target_playlist['id']
        
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/files/batch"
        payload = {
            "do": "playlist",
            "playlists": [playlist_id],
            "files": [str(media_id)]
        }
        res = await self._put(url, json=payload)
        if res:
            logger.info(f"Added media {media_id} to playlist {playlist_name}")
        if res:
            logger.info(f"Added media {media_id} to playlist {playlist_name}")
        return bool(res)

    async def get_station_queue(self, station_id: Optional[int] = None) -> List[Dict]:
        """Fetch the current upcoming queue for the station."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/queue"
        res = await self._get(url)
        return res if isinstance(res, list) else []

    async def delete_queue_item(self, item_id: int, station_id: Optional[int] = None) -> bool:
        """Remove an item from the queue."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/queue/{item_id}"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.delete(url, headers=self.headers)
                resp.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to delete queue item {item_id}: {e}")
                return False

    async def search_requests(self, query: str, station_id: Optional[int] = None) -> List[Dict]:
        """Search for requestable songs."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/requests"
        params = {"searchPhrase": query, "rowCount": 20}
        
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                # AzuraCast usually returns {"rows": [...], "total": ...} or just [...]
                if isinstance(data, dict) and "rows" in data:
                    return data["rows"]
                elif isinstance(data, list):
                    return data
                return []
            except Exception as e:
                logger.error(f"Search requests failed: {e}")
                return []

    # ============================================
    # PLAYLIST MANAGEMENT (NTS-Lite Curator Features)
    # ============================================

    async def get_playlist(self, playlist_id: int, station_id: Optional[int] = None) -> Dict:
        """Get single playlist details."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}"
        res = await self._get(url)
        return res if isinstance(res, dict) else {}

    async def update_playlist(self, playlist_id: int, data: Dict, station_id: Optional[int] = None) -> Dict:
        """Update playlist settings."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}"
        return await self._put(url, json=data) or {}

    async def delete_playlist(self, playlist_id: int, station_id: Optional[int] = None) -> bool:
        """Delete a playlist."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.delete(url, headers=self.headers)
                resp.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to delete playlist {playlist_id}: {e}")
                return False

    async def get_playlist_schedule(self, playlist_id: int, station_id: Optional[int] = None) -> List[Dict]:
        """Get schedule items for a playlist."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}/schedule"
        res = await self._get(url)
        return res if isinstance(res, list) else []

    async def add_playlist_schedule(
        self, 
        playlist_id: int, 
        start_time: str,  # "HH:MM" format
        end_time: str,    # "HH:MM" format
        days: List[int],  # 0=Mon, 6=Sun
        station_id: Optional[int] = None
    ) -> Dict:
        """Add a schedule item to a playlist.
        
        Args:
            playlist_id: Playlist ID
            start_time: Start time in HH:MM format (e.g., "20:00")
            end_time: End time in HH:MM format (e.g., "22:00")
            days: List of days (0=Monday, 6=Sunday)
        """
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}/schedule"
        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "days": days
        }
        return await self._post(url, json=payload) or {}

    async def delete_playlist_schedule(self, playlist_id: int, schedule_id: int, station_id: Optional[int] = None) -> bool:
        """Remove a schedule item from a playlist."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}/schedule/{schedule_id}"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.delete(url, headers=self.headers)
                resp.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Failed to delete schedule {schedule_id}: {e}")
                return False

    async def get_playlist_media(self, playlist_id: int, station_id: Optional[int] = None) -> List[Dict]:
        """Get all media files in a playlist."""
        sid = station_id if station_id is not None else self.station_id
        # First get playlist to find its source type
        playlist = await self.get_playlist(playlist_id, sid)
        if not playlist:
            return []
        
        # For song-based playlists, fetch files with playlist filter
        url = f"{self.base_url}/api/station/{sid}/files"
        params = {"searchPhrase": f"playlist:{playlist.get('name', '')}"}
        
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=30, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "rows" in data:
                    return data["rows"]
                return []
            except Exception as e:
                logger.error(f"Get playlist media failed: {e}")
                return []

    async def reorder_playlist(self, playlist_id: int, media_ids: List[str], station_id: Optional[int] = None) -> bool:
        """Reorder tracks in a playlist."""
        sid = station_id if station_id is not None else self.station_id
        url = f"{self.base_url}/api/station/{sid}/playlist/{playlist_id}/order"
        payload = {"order": media_ids}
        result = await self._put(url, json=payload)
        return result is not None

if __name__ == "__main__":
    pass

