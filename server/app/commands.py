import sys
import os
import time
import speech_recognition as sr
from app.tts import speak_sync
from ytmusicapi import YTMusic

_IS_WINDOWS = sys.platform == "win32"
_IS_LINUX = sys.platform == "linux"

if _IS_LINUX:
    from ctypes import cdll, CFUNCTYPE, c_char_p, c_int, c_void_p
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def _py_error_handler(filename, line, function, err, fmt): pass
    try:
        asound = cdll.LoadLibrary("libasound.so")
        asound.snd_lib_error_set_handler(ERROR_HANDLER_FUNC(_py_error_handler))
    except Exception:
        pass
    os.environ.setdefault("PULSE_SERVER", "unix:/run/user/1000/pulse/native")

IDLE_TIMEOUT = 3 * 60

_recognizer = sr.Recognizer()
_ytm = YTMusic()

_COMMANDS = {
    "open":      "open_youtube",
    "youtube":   "open_youtube",
    "play":      "open_youtube",
    "sentiment": "read_sentiment",
    "emotion":   "read_sentiment",
    "feeling":   "read_sentiment",
    "genre":     "read_genre",
    "what genre":"read_genre",
}


def _get_mic() -> sr.Microphone:
    if _IS_LINUX:
        return sr.Microphone(device_index=4, sample_rate=48000)
    return sr.Microphone()


def _get_ytmusic_url(title: str, artist: str) -> str:
    try:
        results = _ytm.search(f"{title} {artist}", filter="songs", limit=1)
        if results:
            return f"https://music.youtube.com/watch?v={results[0]['videoId']}"
    except Exception:
        pass
    return f"https://music.youtube.com/search?q={title}+{artist}".replace(" ", "+")


def _transcribe(source) -> str:
    try:
        audio = _recognizer.listen(source, timeout=6, phrase_time_limit=6)
        text = _recognizer.recognize_google(audio).lower()
        print(f"[CMD] heard: {text}")
        return text
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except sr.RequestError:
        return ""


def _match_command(text: str):
    for keyword, action in _COMMANDS.items():
        if keyword in text:
            return action
    return None


def _handle(action: str, last_result: dict | None) -> dict:
    if not last_result:
        return {"action": "none", "reason": "no song yet"}

    if action == "open_youtube":
        import webbrowser
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


def listen_for_command(last_result: dict | None) -> dict:
    try:
        with _get_mic() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[CMD] waiting for wake word...")
            last_activity = time.time()

            while True:
                if time.time() - last_activity > IDLE_TIMEOUT:
                    return {"action": "stop", "reason": "timeout"}
                text = _transcribe(source)
                if not text:
                    continue
                last_activity = time.time()
                if "end" in text:
                    return {"action": "stop"}
                if "musika" in text:
                    speak_sync("Yes?")
                    break

            last_activity = time.time()

            while True:
                if time.time() - last_activity > IDLE_TIMEOUT:
                    speak_sync("Goodbye")
                    return {"action": "stop", "reason": "timeout"}
                text = _transcribe(source)
                if not text:
                    continue
                last_activity = time.time()
                if "end" in text:
                    speak_sync("Goodbye")
                    return {"action": "stop"}
                action = _match_command(text)
                if action:
                    result = _handle(action, last_result)
                    result["session"] = "active"
                    return result

    except Exception as e:
        return {"action": "error", "reason": str(e)}