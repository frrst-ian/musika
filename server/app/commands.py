# app/commands.py

import os
os.environ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"

import ctypes
from ctypes import *

# Suppress ALSA warnings
ERROR_HANDLER_FUNC = CFUNCTYPE(
    None, c_char_p, c_int, c_char_p, c_int, c_char_p
)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

try:
    asound = cdll.LoadLibrary("libasound.so")
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass


import speech_recognition as sr
from app.tts import speak_sync
import webbrowser
from ytmusicapi import YTMusic

CHROMEBOOK_MIC_INDEX = 4
CHROMEBOOK_RATE = 48000

_recognizer = sr.Recognizer()
_ytm = YTMusic()

_COMMANDS = {
    "open": "open_youtube",
    "youtube": "open_youtube",
    "play": "open_youtube",
    "sentiment": "read_sentiment",
    "emotion": "read_sentiment",
    "feeling": "read_sentiment",
    "genre": "read_genre",
    "what genre": "read_genre",
}


def _get_ytmusic_url(title: str, artist: str) -> str:
    try:
        results = _ytm.search(f"{title} {artist}", filter="songs", limit=1)
        if results:
            video_id = results[0]["videoId"]
            return f"https://music.youtube.com/watch?v={video_id}"
    except:
        pass

    return f"https://music.youtube.com/search?q={title}+{artist}".replace(" ", "+")


def _transcribe(source) -> str:
    try:
        audio = _recognizer.listen(source, timeout=6, phrase_time_limit=6)
        text = _recognizer.recognize_google(audio).lower()
        print(f"[CMD] heard: {text}")
        return text

    except (sr.WaitTimeoutError, sr.UnknownValueError):
        print("[CMD] nothing heard")
        return ""

    except sr.RequestError:
        print("[CMD] API error")
        return ""


def _match_command(text: str):
    for keyword, action in _COMMANDS.items():
        if keyword in text:
            return action
    return None


def _handle(action: str, last_result: dict | None):
    if not last_result:
        return {"action": "none", "reason": "no song yet"}

    if action == "open_youtube":
        title = last_result.get("title", "")
        artist = last_result.get("artist", "")
        url = _get_ytmusic_url(title, artist)
        webbrowser.open(url)
        speak_sync("Opening YouTube")
        return {"action": "open_youtube", "url": url}

    if action == "read_sentiment":
        sentiment = last_result.get("sentiment", "unknown")
        emotion = last_result.get("emotion", "unknown")

        msg = f"The song feels {emotion} with a {sentiment} sentiment."
        speak_sync(msg)

        return {"action": "read_sentiment", "text": msg}

    if action == "read_genre":
        genre = last_result.get("genre", "unknown")
        confidence = last_result.get("confidence", 0)

        msg = f"The genre is {genre} with {confidence:.0f} percent confidence."
        speak_sync(msg)

        return {"action": "read_genre", "text": msg}

    return {"action": "none"}


def listen_for_command(last_result: dict | None):
    try:
        with sr.Microphone(
            device_index=CHROMEBOOK_MIC_INDEX,
            sample_rate=CHROMEBOOK_RATE
        ) as source:

            _recognizer.adjust_for_ambient_noise(source, duration=1)

            print("[CMD] waiting for wake word...")

            while True:
                text = _transcribe(source)

                if not text:
                    continue

                if "end" in text:
                    return {"action": "stop"}

                if "musika" in text:
                    speak_sync("Yes?")
                    print("[CMD] wake word detected")
                    break

            while True:
                print("[CMD] ready for command...")
                text = _transcribe(source)

                if not text:
                    continue

                if "end" in text:
                    speak_sync("Goodbye")
                    return {"action": "stop"}

                action = _match_command(text)

                if action:
                    _handle(action, last_result)
                    continue

    except Exception as e:
        return {"action": "error", "reason": str(e)}