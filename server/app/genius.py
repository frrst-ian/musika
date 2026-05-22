import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()

genius = lyricsgenius.Genius(os.environ["GENIUS_TOKEN"], skip_non_songs=True)

genius.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://genius.com/'
}

def search_song(title: str, artist: str) -> dict | None:
    try:
        song = genius.search_song(title, artist)
    except Exception as e:
        print(f"[genius] search_song error: {e}", flush=True)
        return None
    
    if not song:
        return None
        
    return {
        "title": song.title,
        "artist": song.artist,
        "url": song.url,
        "thumbnail": song.song_art_image_thumbnail_url,
        "lyrics": song.lyrics,
    }

def fetch_lyrics(title: str, artist: str) -> str | None:
    song = search_song(title, artist)
    if not song:
        return None
    return song["lyrics"]