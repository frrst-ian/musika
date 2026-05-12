import os
import tempfile
import edge_tts
import asyncio

_VOICE = "en-US-JennyNeural"
_TMP = tempfile.gettempdir()


def build_result_speech(result: dict) -> str:
    title = result.get("title", "Unknown")
    artist = result.get("artist", "Unknown")
    return f"{title} by {artist}"


def speak_sync(text: str):
    path = os.path.join(_TMP, "musika_cmd.mp3")

    os.system(
        f'edge-tts --text "{text}" --voice {_VOICE} --write-media "{path}"'
    )

    os.system(
        f'PULSE_SERVER=unix:/run/user/1000/pulse/native '
        f'/usr/bin/mpg123 "{path}"'
    )


async def _speak_async(text: str):
    path = os.path.join(_TMP, "musika_tts.mp3")

    tts = edge_tts.Communicate(text, _VOICE)
    await tts.save(path)

    os.system(
        f'PULSE_SERVER=unix:/run/user/1000/pulse/native '
        f'/usr/bin/mpg123 "{path}"'
    )


def speak(text: str):
    asyncio.create_task(_speak_async(text))