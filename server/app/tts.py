import os
import tempfile
import edge_tts
import asyncio

_VOICE = "en-US-JennyNeural"
_TMP = tempfile.gettempdir()
_IS_LINUX = os.sys.platform == "linux"


def _play(path_mp3: str):
    if _IS_LINUX:
        wav = path_mp3.replace(".mp3", ".wav")
        os.system(f'ffmpeg -i "{path_mp3}" "{wav}" -y -loglevel quiet')
        os.system(f'aplay -D plughw:0,0 "{wav}"') 
    else:
        os.system(f'mpg123 "{path_mp3}"')


def build_result_speech(result: dict) -> str:
    return f"{result.get('title', 'Unknown')} by {result.get('artist', 'Unknown')}"


def speak_sync(text: str):
    path = os.path.join(_TMP, "musika_cmd.mp3")
    os.system(f'edge-tts --text "{text}" --voice {_VOICE} --write-media "{path}"')
    _play(path)


async def _speak_async(text: str):
    path = os.path.join(_TMP, "musika_tts.mp3")
    tts = edge_tts.Communicate(text, _VOICE)
    await tts.save(path)
    _play(path)


def speak(text: str):
    asyncio.create_task(_speak_async(text))