import sys
import os
import time
import speech_recognition as sr
from app.tts import speak_sync
from ytmusicapi import YTMusic
from ctypes import cdll, CFUNCTYPE, c_char_p, c_int
import contextlib

os.environ["JACK_NO_START_SERVER"] = "1"
os.environ["JACK_DEFAULT_SERVER"] = ""
os.environ["LIBASOUND_THREAD_SAFE"] = "0"
os.environ["ALSA_QUIET"] = "1"

_IS_WINDOWS = sys.platform == "win32"
_IS_LINUX = sys.platform == "linux"

def _noop(*args): pass

ERROR_HANDLER = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)(_noop)

if _IS_LINUX:
    try:
        asound = cdll.LoadLibrary("libasound.so")
        asound.snd_lib_error_set_handler(ERROR_HANDLER)
    except:
        pass

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as f:
        with contextlib.redirect_stderr(f):
            yield

IDLE_TIMEOUT = 3 * 60
_recognizer = sr.Recognizer()
_ytm = YTMusic()

SESSION_ACTIVE = False

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

def _get_mic():
    if _IS_LINUX:
        return sr.Microphone(device_index=4, sample_rate=48000)
    return sr.Microphone()

def _get_ytmusic_url(title: str, artist: str) -> str:
    try:
        results = _ytm.search(f"{title} {artist}", filter="songs", limit=1)
        if results:
            return f"https://music.youtube.com/watch?v={results[0]['videoId']}"
    except:
        pass
    return f"https://music.youtube.com/search?q={title}+{artist}".replace(" ", "+")

def _transcribe(source) -> str:
    try:
        audio = _recognizer.listen(source, timeout=6, phrase_time_limit=6)
        text = _recognizer.recognize_google(audio).lower()
        print(f"[CMD] heard: {text}")
        return text
    except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
        return ""

def _match_command(text: str):
    for k, v in _COMMANDS.items():
        if k in text:
            return v
    return None

def _handle(action: str, last_result: dict | None):
    if not last_result:
        return

    if action == "open_youtube":
        import webbrowser
        url = _get_ytmusic_url(
            last_result.get("title", ""),
            last_result.get("artist", "")
        )
        webbrowser.open(url)
        speak_sync("Opening YouTube")
        print({"action": "open_youtube", "url": url})

    elif action == "read_sentiment":
        msg = f"The song feels {last_result.get('emotion','unknown')} with a {last_result.get('sentiment','unknown')} sentiment."
        speak_sync(msg)
        print({"action": "read_sentiment", "text": msg})

    elif action == "read_genre":
        msg = f"The genre is {last_result.get('genre','unknown')} with {last_result.get('confidence',0):.0f}% confidence."
        speak_sync(msg)
        print({"action": "read_genre", "text": msg})

def listen_for_command(last_result: dict | None) -> dict:
    global SESSION_ACTIVE

    try:
        with suppress_stderr():
            with _get_mic() as source:
                _recognizer.adjust_for_ambient_noise(source, duration=1)

                print("[CMD] waiting for wake word...")
                last_activity = time.time()

                while True:
                    if time.time() - last_activity > IDLE_TIMEOUT:
                        SESSION_ACTIVE = False
                        return {"action": "stop", "reason": "timeout"}

                    text = _transcribe(source)
                    if not text:
                        continue

                    last_activity = time.time()

                    if "end" in text:
                        SESSION_ACTIVE = False
                        speak_sync("Goodbye")
                        return {"action": "stop"}

                    # wake word
                    if not SESSION_ACTIVE:
                        if "musika" in text:
                            SESSION_ACTIVE = True
                            speak_sync("Yes?")
                        continue

                    # active session mode (NO RESET AFTER COMMAND)
                    action = _match_command(text)
                    if action:
                        _handle(action, last_result)
                        continue

    except Exception as e:
        SESSION_ACTIVE = False
        return {"action": "error", "reason": str(e)}