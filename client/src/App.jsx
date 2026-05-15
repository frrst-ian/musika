import { useState } from "react";
import { Mic, MicOff, Radio } from "lucide-react";
import SearchBar from "./components/SearchBar";
import ResultCard from "./components/ResultCard";
import ErrorBoundary from "./components/ErrorBoundary";
import ModeToggle from "./components/ModeToggle";
import TTSToggle from "./components/TTSToggle";
import CommandButton from "./components/CommandButton";
import PlaylistPanel from "./components/PlaylistPanel";
import AuthGate from "./components/AuthGate";
import { useSpeech } from "./hooks/useSpeech";
import styles from "./styles/app.module.css";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function MusikApp({ token, user, logout }) {
  const [mode, setMode] = useState("search");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [commandFeedback, setCommandFeedback] = useState(null);

  const {
    listening,
    identifying,
    listenForSearch,
    stopListening,
    identifySong,
    stopIdentifying,
  } = useSpeech();

  function authHeaders() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  async function classify(title, artist) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${BASE}/classify`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ title, artist }),
      });

      if (res.status === 404) {
        setError("Song not found. Try a different title or artist.");
        return;
      }
      if (!res.ok) throw new Error();

      const data = await res.json();
      setResult(data);

      if (ttsEnabled) {
        await fetch(`${BASE}/tts/speak`, {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({
            text: `${data.title} by ${data.artist}. Genre: ${data.genre}, ${data.confidence.toFixed(0)} percent confidence. The song feels ${data.emotion} with a ${data.sentiment} sentiment.`,
          }),
        });
      }
    } catch {
      setError("Something went wrong. Is the server running?");
    } finally {
      setLoading(false);
    }
  }

  function handleSearch({ title, artist }) {
    classify(title, artist);
  }

  function handleVoiceSearch() {
    if (listening) {
      stopListening();
      return;
    }
    listenForSearch(
      token,
      ({ title, artist }) => classify(title, artist),
      (msg) => setError(msg),
    );
  }

  function handleIdentify() {
    if (identifying) {
      stopIdentifying();
      return;
    }
    setError(null);
    identifySong(
      token,
      ({ title, artist }) => classify(title, artist),
      (msg) => setError(msg),
    );
  }

  function handleCommandAction(action) {
    if (action.action === "open_youtube" && action.url) {
      const a = document.createElement("a");
      a.href = action.url;
      a.target = "_blank";
      a.rel = "noreferrer";
      a.click();
      setCommandFeedback(`Opening: ${action.url}`);
    } else if (action.action === "read_sentiment") {
      setCommandFeedback(action.text);
    } else if (action.action === "read_genre") {
      setCommandFeedback(action.text);
    } else if (action.action === "stop") {
      setCommandFeedback("Musika session ended.");
    } else if (action.action === "error") {
      setCommandFeedback(`Error: ${action.reason}`);
    }
    setTimeout(() => setCommandFeedback(null), 4000);
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.logo}>musika</h1>
        <p className={styles.tagline}>music genre classifier</p>
      </header>

      <main className={styles.main}>
        <div className={styles.controls}>
          <ModeToggle mode={mode} onChange={setMode} />
          <div className={styles.controlsRight}>
            <TTSToggle enabled={ttsEnabled} onChange={setTtsEnabled} />
            <CommandButton
              lastResult={result}
              token={token}
              onAction={handleCommandAction}
            />
            <button className={styles.logoutBtn} onClick={logout}>
              logout
            </button>
          </div>
        </div>

        {mode === "search" && (
          <SearchBar onSearch={handleSearch} loading={loading} />
        )}

        {mode === "stt" && (
          <button
            className={`${styles.bigMicBtn} ${listening ? styles.micActive : ""}`}
            onClick={handleVoiceSearch}
            disabled={loading}
          >
            {listening ? <MicOff size={22} /> : <Mic size={22} />}
            <span>
              {listening ? "tap to stop" : "tap and speak the song name"}
            </span>
          </button>
        )}

        {mode === "identify" && (
          <button
            className={`${styles.bigMicBtn} ${identifying ? styles.micActive : ""}`}
            onClick={handleIdentify}
            disabled={loading}
          >
            {identifying ? <MicOff size={22} /> : <Radio size={22} />}
            <span>
              {identifying
                ? "listening 10s... tap to stop"
                : "tap to identify song from mic"}
            </span>
          </button>
        )}

        {commandFeedback && (
          <p className={styles.feedback}>{commandFeedback}</p>
        )}
        {error && <p className={styles.error}>{error}</p>}

        {result && (
          <ErrorBoundary key={result.title + result.artist}>
            <ResultCard result={result} />
          </ErrorBoundary>
        )}

        <PlaylistPanel token={token} />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthGate>
      {({ token, user, logout }) => (
        <MusikApp token={token} user={user} logout={logout} />
      )}
    </AuthGate>
  );
}
