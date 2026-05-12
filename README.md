# musika
A music genre classifier with sentiment analysis, voice input, and text-to-speech.

---

## What it does
- Classifies a song's genre from its lyrics using an LLM
- Analyzes the emotional sentiment of the lyrics using NLTK and VADER
- Supports three input modes: typed search, voice search, and audio identification
- Reads results aloud using text-to-speech
- Accepts voice commands via a wake word
- Tracks search history and builds a playlist

---

## Tech stack
**Frontend** — ReactJS, Vite, CSS Modules  
**Backend** — FastAPI  
**NLP** — NLTK, spaCy, VADER Sentiment  
**APIs** — Genius (lyrics), Groq (genre classification), ACRCloud (audio fingerprinting)  
**Speech** — Web Speech API (browser STT), edge-tts (TTS via JennyNeural voice)

---

## Setup

**Requirements**
- Python 3.11
- Node.js 20+
- Linux only: `sudo apt install mpg123`

**Environment variables**

Create `server/.env`:

GENIUS_TOKEN=
GROQ_TOKEN=
ACR_HOST=
ACR_ACCESS_KEY=
ACR_ACCESS_SECRET=

**Backend**
```bash
cd server
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd client
npm install
npm run dev
```

Open http://localhost:5173 in Chrome.

---

## Windows notes

PyAudio requires a manual install on Windows — do this before `pip install -r requirements.txt`:
```bash
pip install pipwin
pipwin install pyaudio
```
If that fails, download the `.whl` for your Python version from
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio then:
```bash
pip install PyAudio-0.2.14-cp311-win_amd64.whl
```

---

## Input modes
**Search** — type the song title and artist, press classify.  
**Voice** — click the mic button and speak the song name. Example: "Blinding Lights by The Weeknd". The transcript is parsed by spaCy to extract the title and artist.  
**Identify** — click the identify button while a song is playing near your microphone. Records 10 seconds of audio and sends it to ACRCloud for fingerprint matching.

---

## Voice commands
Click the "musika" button to activate the command listener.  
Say "Musika" as the wake word, then follow with a command:
- "open the song" or "open YouTube" — opens a YouTube search for the last classified song
- "what is the sentiment" or "what is the emotion" — reads the sentiment analysis result aloud
- "what genre" — reads the genre and confidence aloud

Say "end Musika" to close the command session.

---

## TTS
Toggle "tts on" in the UI to have results read aloud automatically after each classification. Uses Microsoft's JennyNeural voice via edge-tts. Audio plays in the background so the UI stays responsive.

---

## Playlist
Every classified song is saved automatically. The playlist panel at the bottom shows:
- **Top** — songs sorted by how often they have been searched
- **All** — full list with genre, search count, and a YouTube link