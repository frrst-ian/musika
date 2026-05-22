from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.genius import search_song
from app.classifier import classify_genre
from app.sentiment import analyze as analyze_sentiment
from app.stt import parse_transcript
from app.acr import identify as acr_identify
from app.tts import speak, build_result_speech
from app.commands import listen_for_command
from app.firebase import verify_token, create_user_doc
from app.db import init_db
import app.playlist as playlist
from ytmusicapi import YTMusic
from groq import Groq
import os

_ytm = YTMusic()
_groq = Groq(api_key=os.environ["GROQ_TOKEN"])

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://awesome-musika.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

_last_result: dict | None = None


class SearchRequest(BaseModel):
    title: str
    artist: str


class TranscriptRequest(BaseModel):
    transcript: str


class CommandRequest(BaseModel):
    last_result: dict | None = None


class TTSRequest(BaseModel):
    text: str


class UserDocRequest(BaseModel):
    email: str
    username: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    song_context: dict | None = None


@app.post("/user/init")
def init_user(req: UserDocRequest, uid: str = Depends(verify_token)):
    create_user_doc(uid, req.email, req.username)
    return {"status": "ok"}


@app.post("/classify")
async def classify(req: SearchRequest, uid: str = Depends(verify_token)):
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
    playlist.upsert(uid, result)
    return result


@app.post("/chat")
def chat(req: ChatRequest, uid: str = Depends(verify_token)):
    system = "You are Musika, a music assistant. Answer concisely and only about music."

    if req.song_context:
        ctx = req.song_context
        system = (
            f"You are Musika, a music assistant. The user just classified this song:\n"
            f"Title: {ctx.get('title')}\n"
            f"Artist: {ctx.get('artist')}\n"
            f"Genre: {ctx.get('genre')} ({ctx.get('confidence', 0):.0f}% confidence)\n"
            f"Sentiment: {ctx.get('sentiment')} / Emotion: {ctx.get('emotion')} / Compound: {ctx.get('compound')}\n"
            f"Answer questions about this song, its genre, sentiment, or related music. Be concise."
        )

    response = _groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}]
        + [{"role": m.role, "content": m.content} for m in req.messages],
        max_tokens=400,
    )
    return {"reply": response.choices[0].message.content.strip()}


@app.post("/stt/parse")
def stt_parse(req: TranscriptRequest, uid: str = Depends(verify_token)):
    return parse_transcript(req.transcript)


@app.post("/acr/identify")
async def acr_identify_route(file: UploadFile = File(...), uid: str = Depends(verify_token)):
    audio_bytes = await file.read()
    result = await acr_identify(audio_bytes)
    if not result:
        raise HTTPException(status_code=404, detail="Song not recognized")
    return result


@app.post("/tts/speak")
async def tts_speak(req: TTSRequest, background_tasks: BackgroundTasks, uid: str = Depends(verify_token)):
    background_tasks.add_task(_speak_bg, req.text)
    return {"status": "speaking"}

async def _speak_bg(text: str):
    from app.tts import _speak_async
    await _speak_async(text)


@app.post("/command/listen")
def command_listen(req: CommandRequest, uid: str = Depends(verify_token)):
    context = req.last_result or _last_result
    return listen_for_command(context)


@app.get("/playlist")
def get_playlist(uid: str = Depends(verify_token)):
    return {"songs": playlist.get_all(uid)}


@app.get("/playlist/top")
def get_top(uid: str = Depends(verify_token)):
    return {"songs": playlist.get_top(uid)}


@app.delete("/playlist")
def remove_from_playlist(title: str, artist: str, uid: str = Depends(verify_token)):
    playlist.remove(uid, title, artist)
    return {"status": "removed"}


@app.get("/stats")
def get_stats(uid: str = Depends(verify_token)):
    return playlist.get_stats(uid)


@app.get("/me")
def get_me(uid: str = Depends(verify_token)):
    from app.db import get_conn
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT username, email, created_at FROM users WHERE uid = %s", (uid,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM playlist WHERE uid = %s", (uid,))
        count_row = cur.fetchone()
    return {
        "username": row["username"],
        "email": row["email"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "total_classified": count_row["total"] if count_row else 0,
    }

@app.get("/")
def root():
    return {"status": "ok"}