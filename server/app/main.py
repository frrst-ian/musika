from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.genius import search_song, fetch_lyrics
from app.classifier import classify_genre

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    title: str
    artist: str

@app.post("/classify")
def classify(req: SearchRequest):
    song = search_song(req.title, req.artist)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    result = classify_genre(song["lyrics"])
    return {
        "title": song["title"],
        "artist": song["artist"],
        "url": song["url"],
        "thumbnail": song["thumbnail"],
        **result
    }