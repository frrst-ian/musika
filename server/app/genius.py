import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()

genius = lyricsgenius.Genius(os.environ["GENIUS_TOKEN"], skip_non_songs=True)

def search_song(title: str, artist: str) -> dict | None:
    song = genius.search_song(title, artist)
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