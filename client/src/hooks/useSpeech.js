import { useState, useRef, useCallback } from "react"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export function useSpeech() {
  const [listening, setListening] = useState(false)
  const [identifying, setIdentifying] = useState(false)
  const mediaRef = useRef(null)
  const recognitionRef = useRef(null)

  const listenForSearch = useCallback((token, onResult, onError) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) { onError("Speech recognition not supported. Use Chrome."); return }

    const rec = new SpeechRecognition()
    rec.lang = "en-US"
    rec.interimResults = false
    rec.maxAlternatives = 1
    recognitionRef.current = rec

    rec.onstart = () => setListening(true)
    rec.onend = () => setListening(false)
    rec.onresult = async (e) => {
      const transcript = e.results[0][0].transcript
      try {
        const res = await fetch(`${BASE}/stt/parse`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ transcript }),
        })
        const parsed = await res.json()
        onResult(parsed)
      } catch { onError("Failed to parse transcript.") }
    }
    rec.onerror = (e) => { setListening(false); onError(`Mic error: ${e.error}`) }
    rec.start()
  }, [])

  const stopListening = useCallback(() => { recognitionRef.current?.stop(); setListening(false) }, [])

  const identifySong = useCallback(async (token, onResult, onError) => {
    try {
      setIdentifying(true)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      mediaRef.current = recorder
      const chunks = []
      recorder.ondataavailable = (e) => chunks.push(e.data)
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunks, { type: "audio/wav" })
        const form = new FormData()
        form.append("file", blob, "sample.wav")
        try {
          const res = await fetch(`${BASE}/acr/identify`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: form,
          })
          if (res.status === 404) { onError("Song not recognized."); return }
          const data = await res.json()
          onResult(data)
        } catch { onError("ACR identification failed.") }
        finally { setIdentifying(false) }
      }
      recorder.start()
      setTimeout(() => recorder.stop(), 10000)
    } catch { setIdentifying(false); onError("Microphone access denied.") }
  }, [])

  const stopIdentifying = useCallback(() => { mediaRef.current?.stop(); setIdentifying(false) }, [])

  return { listening, identifying, listenForSearch, stopListening, identifySong, stopIdentifying }
}