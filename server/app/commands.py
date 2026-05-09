import speech_recognition as sr
from app.tts import speak_sync

CHROMEBOOK_MIC_INDEX = 4
CHROMEBOOK_RATE = 48000

_recognizer = sr.Recognizer()

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

def _transcribe(source) -> str:
    try:
        audio = _recognizer.listen(source, timeout=6, phrase_time_limit=6)
        return _recognizer.recognize_google(audio).lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except sr.RequestError:
        return ""

def _match_command(text: str) -> str | None:
    for keyword, action in _COMMANDS.items():
        if keyword in text:
            return action
    return None

def listen_for_command(last_result: dict | None) -> dict:
    """
    Opens mic and waits for 'Musika' wake word.
    Then listens for a command phrase.
    'end Musika' closes session.
    Returns {action, payload} for the frontend to execute.
    """
    try:
        with sr.Microphone(device_index=CHROMEBOOK_MIC_INDEX,
                           sample_rate=CHROMEBOOK_RATE) as source:
            _recognizer.adjust_for_ambient_noise(source, duration=1)
            speak_sync("Musika is listening.")

            # Wait for wake word
            while True:
                text = _transcribe(source)
                if not text:
                    continue
                if "end musika" in text:
                    speak_sync("Musika closed.")
                    return {"action": "stop"}
                if "musika" in text:
                    speak_sync("Yes?")
                    break

            # Listen for the actual command
            command_text = _transcribe(source)
            if not command_text:
                return {"action": "none", "reason": "no command heard"}

            if "end musika" in command_text:
                speak_sync("Musika closed.")
                return {"action": "stop"}

            action = _match_command(command_text)

            if action == "open_youtube" and last_result:
                title = last_result.get("title", "")
                artist = last_result.get("artist", "")
                query = f"{title} {artist}".replace(" ", "+")
                url = f"https://www.youtube.com/results?search_query={query}"
                speak_sync(f"Opening {title} by {artist} on YouTube.")
                return {"action": "open_youtube", "url": url}

            if action == "read_sentiment" and last_result:
                sentiment = last_result.get("sentiment", "unknown")
                emotion = last_result.get("emotion", "unknown")
                msg = f"The song feels {emotion} with a {sentiment} sentiment."
                speak_sync(msg)
                return {"action": "read_sentiment", "text": msg}

            if action == "read_genre" and last_result:
                genre = last_result.get("genre", "unknown")
                confidence = last_result.get("confidence", 0)
                msg = f"The genre is {genre} with {confidence:.0f} percent confidence."
                speak_sync(msg)
                return {"action": "read_genre", "text": msg}

            speak_sync("Sorry, I didn't catch that command.")
            return {"action": "none", "reason": "unrecognized command"}

    except Exception as e:
        return {"action": "error", "reason": str(e)}