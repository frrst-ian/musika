import asyncio
import tempfile
import os
import edge_tts

# Jenny Neural — natural, non-robotic, neutral accent
_VOICE = "en-US-JennyNeural"
_TMP = tempfile.gettempdir()

def build_result_speech(result: dict) -> str:
    title = result.get("title", "Unknown")
    artist = result.get("artist", "Unknown")
    genre = result.get("genre", "unknown")
    confidence = result.get("confidence", 0)
    sentiment = result.get("sentiment", "")
    emotion = result.get("emotion", "")

    lines = [
        f"{title} by {artist}.",
        f"Genre: {genre}, with {confidence:.0f} percent confidence.",
    ]
    if sentiment and emotion:
        lines.append(f"The song has a {sentiment} sentiment and feels {emotion}.")

    return " ".join(lines)

async def _speak_async(text: str):
    path = os.path.join(_TMP, "musika_tts.mp3")
    tts = edge_tts.Communicate(text, _VOICE)
    await tts.save(path)
    # Non-blocking shell call — UI stays responsive
    os.system(f"mpg123 -q {path} &")

def speak(text: str):
    """Fire and forget, returns immediately, audio plays in background."""
    asyncio.create_task(_speak_async(text))

def speak_sync(text: str):
    """For use outside async context"""
    asyncio.run(_speak_async(text))