# musika
A music genre classifier with sentiment analysis, voice input, and text-to-speech.

---

## What it does
- Classifies a song's genre from its lyrics using an LLM
- Analyzes the emotional sentiment of the lyrics using NLTK and VADER
- Supports three input modes: typed search, voice search, and audio identification
- Reads results aloud using text-to-speech
- Accepts voice commands via a wake word
- Tracks search history and builds a playlist per user

---

## Tech stack
**Frontend** — ReactJS, Vite, CSS Modules  
**Backend** — FastAPI  
**NLP** — NLTK, spaCy, VADER Sentiment  
**APIs** — Genius (lyrics), Groq (genre classification), ACRCloud (audio fingerprinting)  
**Speech** — Web Speech API (browser STT), edge-tts (TTS via JennyNeural voice)  
**Auth** — Firebase Authentication  
**Database** — PostgreSQL

---

## Setup

**Requirements**
- Python 3.11
- Node.js 20+
- PostgreSQL 14+
- Linux only: `sudo apt install mpg123`

**Environment variables**

Create `server/.env`:
```bash
GENIUS_TOKEN=
GROQ_TOKEN=
ACR_HOST=
ACR_ACCESS_KEY=
ACR_ACCESS_SECRET=
FIREBASE_SERVICE_ACCOUNT_JSON=
DATABASE_URL=postgresql://user:password@localhost:5432/musika
```

Create `client/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
```

---

## Database setup

**1. Create the database and user**
```sql
CREATE USER musika WITH PASSWORD 'yourpassword';
CREATE DATABASE musika OWNER musika;
```

**2. Run the schema**
```bash
psql -U musika -d musika -f server/schema.sql
```

The schema creates four tables: `users`, `songs`, `song_analysis`, and `playlist`. The app calls `init_db()` on startup which also runs the schema with `CREATE TABLE IF NOT EXISTS`, so this step is only strictly necessary if you want the tables created before the first server start.

**3. Set `DATABASE_URL` in `server/.env`**
```bash
DATABASE_URL=postgresql://musika:yourpassword@localhost:5432/musika
```

For a remote database (e.g. Render, Supabase, Railway), paste the connection string they provide directly.

---

## Backend
```bash
cd server
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

## Frontend
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
Every classified song is saved automatically per user account. The playlist panel shows:
- **Top** — songs sorted by how often they have been searched
- **All** — full list with genre, search count, and a YouTube link