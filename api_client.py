import time
import requests
from typing import Optional, Dict, Any, List

MUSIC_BRAINZ_URL = "https://musicbrainz.org/ws/2/release/"
COVER_ART_ARCHIVE_URL = "https://coverartarchive.org/release/{release_id}/front"
USER_AGENT = "MusicCat/1.0 (https://github.com/agardnerIT/musiccat)"
RATE_LIMIT_DELAY = 1.1

_last_request_time = 0


def _rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def _get_cover_url(release_id: str) -> Optional[str]:
    try:
        url = COVER_ART_ARCHIVE_URL.format(release_id=release_id)
        response = requests.get(url, allow_redirects=True, timeout=10, stream=True)
        if response.status_code == 200:
            return response.url
        return None
    except requests.RequestException:
        return None


def _get_tracks(release_id: str) -> List[Dict[str, Any]]:
    try:
        url = f"{MUSIC_BRAINZ_URL}{release_id}"
        params = {"inc": "recordings", "fmt": "json"}
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        tracks = []
        for media in data.get("media", []):
            recordings = media.get("recordings", [])
            for i, recording in enumerate(recordings):
                track_position = (
                    media.get("track", [])[i].get("position")
                    if i < len(media.get("track", []))
                    else None
                )
                duration_ms = recording.get("length")
                duration_sec = duration_ms // 1000 if duration_ms else None
                tracks.append(
                    {
                        "track_number": track_position,
                        "title": recording.get("title"),
                        "duration": duration_sec,
                    }
                )
        return tracks
    except requests.RequestException:
        return []


def lookup_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    _rate_limit()

    params = {"query": f"barcode:{barcode}", "fmt": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(
            MUSIC_BRAINZ_URL, params=params, headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("releases"):
            return None

        release = data["releases"][0]
        release_id = release.get("id")

        artist_name = "Unknown Artist"
        if release.get("artist-credit"):
            artist_name = release["artist-credit"][0]["artist"]["name"]

        year = None
        if release.get("date"):
            try:
                year = int(release["date"][:4])
            except (ValueError, IndexError):
                pass

        genre = None
        if release.get("genres"):
            genre = release["genres"][0]["name"]

        cover_url = None
        if release_id:
            cover_url = _get_cover_url(release_id)
            tracks = _get_tracks(release_id)
        else:
            tracks = []

        return {
            "barcode": barcode,
            "title": release.get("title", "Unknown Title"),
            "artist": artist_name,
            "year": year,
            "genre": genre,
            "cover_url": cover_url,
            "tracks": tracks,
        }

    except requests.RequestException:
        return None
