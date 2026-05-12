import os
import sys
import tempfile
import edge_tts
import asyncio
import subprocess

_VOICE = "en-US-JennyNeural"
_TMP = tempfile.gettempdir()
_IS_WINDOWS = sys.platform == "win32"


def build_result_speech(result: dict) -> str:
    title = result.get("title", "Unknown")
    artist = result.get("artist", "Unknown")
    return f"{title} by {artist}"


def _play(path: str):
    if _IS_WINDOWS:
        subprocess.run(
            ["powershell", "-c", f'(New-Object Media.SoundPlayer).PlaySync()' ],
            capture_output=True
        )
        subprocess.run(
            ["powershell", "-c",
             f'$p = New-Object System.Windows.Media.MediaPlayer; '
             f'$p.Open([uri]"{path}"); $p.Play(); Start-Sleep 5'],
            capture_output=True
        )
    else:
        pulse_env = {"PULSE_SERVER": "unix:/run/user/1000/pulse/native", **os.environ}
        subprocess.run(["/usr/bin/mpg123", path], env=pulse_env)


def speak_sync(text: str):
    path = os.path.join(_TMP, "musika_cmd.mp3")
    asyncio.run(_save_tts(text, path))
    _play(path)


async def _save_tts(text: str, path: str):
    tts = edge_tts.Communicate(text, _VOICE)
    await tts.save(path)


async def _speak_async(text: str):
    path = os.path.join(_TMP, "musika_tts.mp3")
    await _save_tts(text, path)
    _play(path)


def speak(text: str):
    asyncio.create_task(_speak_async(text))