from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.genius import search_song
from app.classifier import classify_genre
from app.sentiment import analyze as analyze_sentiment
from app.stt import parse_transcript
from app.acr import identify as acr_identify
from app.tts import speak, build_result_speech
from app.commands import listen_for_command
import app.playlist as playlist
from ytmusicapi import YTMusic

_ytm = YTMusic()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Holds the last classified result for command mode context
_last_result: dict | None = None


class SearchRequest(BaseModel):
    title: str
    artist: str


class TranscriptRequest(BaseModel):
    transcript: str


class CommandRequest(BaseModel):
    # Frontend passes last result so command mode has context
    last_result: dict | None = None


class TTSRequest(BaseModel):
    text: str

# Classify

@app.post("/classify")
async def classify(req: SearchRequest):
    global _last_result

    song = search_song(req.title, req.artist)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    genre_result = classify_genre(song["lyrics"])
    sentiment_result = analyze_sentiment(song["lyrics"])

    try:
        yt_results = _ytm.search(f"{song['title']} {song['artist']}", filter="songs", limit=1)
        youtube_url = f"https://music.youtube.com/watch?v={yt_results[0]['videoId']}" if yt_results else ""
    except Exception:
        youtube_url = ""

    result = {
        "title": song["title"],
        "artist": song["artist"],
        "url": song["url"],
        "thumbnail": song["thumbnail"],
        "youtube_url": youtube_url,
        **genre_result,
        **sentiment_result,
    }

    _last_result = result
    playlist.upsert(result)
    return result

#  STT parse based on title / artist name


@app.post("/stt/parse")
def stt_parse(req: TranscriptRequest):
    """Receives Web Speech API transcript, returns parsed title + artist."""
    return parse_transcript(req.transcript)

# ACRCloud identify (lyrics based)


@app.post("/acr/identify")
async def acr_identify_route(file: UploadFile = File(...)):
    """Receives audio blob from browser, identifies song via ACRCloud."""
    audio_bytes = await file.read()
    result = await acr_identify(audio_bytes)
    if not result:
        raise HTTPException(status_code=404, detail="Song not recognized")
    return result

# TTS
@app.post("/tts/speak")
async def tts_speak(req: TTSRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(_speak_bg, req.text)
    return {"status": "speaking"}

async def _speak_bg(text: str):
    from app.tts import _speak_async
    await _speak_async(text)

#  Command mode
@app.post("/command/listen")
def command_listen(req: CommandRequest):
    context = req.last_result or _last_result
    return listen_for_command(context)

#  Playlist


@app.get("/playlist")
def get_playlist():
    return {"songs": playlist.get_all()}


@app.get("/playlist/top")
def get_top():
    return {"songs": playlist.get_top()}


@app.delete("/playlist")
def remove_from_playlist(title: str, artist: str):
    playlist.remove(title, artist)
    return {"status": "removed"}
