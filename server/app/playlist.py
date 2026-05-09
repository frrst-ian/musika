import json
import os
from datetime import datetime

_PATH = os.path.join(os.path.dirname(__file__), "..", "playlist.json")

def _load() -> dict:
    if not os.path.exists(_PATH):
        return {"songs": []}
    with open(_PATH, "r") as f:
        return json.load(f)

def _save(data: dict):
    with open(_PATH, "w") as f:
        json.dump(data, f, indent=2)

def _key(title: str, artist: str) -> str:
    return f"{title.lower().strip()}::{artist.lower().strip()}"

def upsert(song: dict):
    """Add song or increment search_count if it already exists."""
    data = _load()
    k = _key(song["title"], song["artist"])

    for existing in data["songs"]:
        if _key(existing["title"], existing["artist"]) == k:
            existing["search_count"] += 1
            existing["last_searched"] = datetime.now().isoformat()
            _save(data)
            return

    data["songs"].append({
        **song,
        "search_count": 1,
        "last_searched": datetime.now().isoformat(),
    })
    _save(data)

def get_all() -> list:
    return _load()["songs"]

def get_top(limit: int = 10) -> list:
    songs = _load()["songs"]
    return sorted(songs, key=lambda s: s["search_count"], reverse=True)[:limit]

def remove(title: str, artist: str):
    data = _load()
    k = _key(title, artist)
    data["songs"] = [s for s in data["songs"]
                     if _key(s["title"], s["artist"]) != k]
    _save(data)