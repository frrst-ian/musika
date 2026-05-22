import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()

genius = lyricsgenius.Genius(os.environ["GENIUS_TOKEN"])

genius.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_song(title: str, artist: str) -> dict | None:
    try:
        search_results = genius.search_songs(f"{title} {artist}")
    except Exception as e:
        print(f"[genius] search_song error: {e}", flush=True)
        return None

    if not search_results or not search_results.get('hits'):
        return None

    for hit in search_results['hits']:
        result = hit['result']
        if artist.lower() in result['primary_artist']['name'].lower():
            
            song_data = {
                "title": result.get("title"),
                "artist": result.get("primary_artist", {}).get("name"),
                "url": result.get("url"),
                "thumbnail": result.get("song_art_image_thumbnail_url"),
                "lyrics": None
            }
            
            try:
                song_data["lyrics"] = genius.lyrics(song_url=song_data["url"])
            except Exception as e:
                print(f"[genius] web scraping lyrics failed: {e}", flush=True)
            
            return song_data
            
    return None

def fetch_lyrics(title: str, artist: str) -> str | None:
    song = search_song(title, artist)
    if not song:
        return None
    return song["lyrics"]