import os, requests
from dotenv import load_dotenv
load_dotenv()

GENIUS_TOKEN = os.environ["GENIUS_TOKEN"]
HEADERS = {"Authorization": f"Bearer {GENIUS_TOKEN}"}

def search_song(title: str, artist: str) -> dict | None:
    try:
        r = requests.get(
            "https://api.genius.com/search",
            headers=HEADERS,
            params={"q": f"{title} {artist}"},
            timeout=10,
        )
        r.raise_for_status()
        hits = r.json()["response"]["hits"]
        if not hits:
            return None
        s = hits[0]["result"]
        return {
            "title": s["title"],
            "artist": s["primary_artist"]["name"],
            "url": s["url"],
            "thumbnail": s["song_art_image_thumbnail_url"],
            "lyrics": None,  
        }
    except Exception as e:
        print(f"[genius] search_song error: {e}", flush=True)
        return None