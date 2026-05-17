import { useState, useEffect, useRef } from "react"
import { Send, Loader2, Bot } from "lucide-react"
import styles from "./ChatPanel.module.css"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function ChatPanel({ token, songContext }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  // clear chat when song changes
  useEffect(() => {
    setMessages([])
  }, [songContext?.title, songContext?.artist])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function send() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: "user", content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setInput("")
    setLoading(true)

    try {
      const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages: next,
          song_context: songContext || null,
        }),
      })
      const data = await res.json()
      setMessages([...next, { role: "assistant", content: data.reply }])
    } catch {
      setMessages([...next, { role: "assistant", content: "Something went wrong. Try again." }])
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className={styles.panel}>
      <div className={styles.context}>
        {songContext
          ? <><Bot size={12} /><span>asking about <strong>{songContext.title}</strong> by {songContext.artist}</span></>
          : <><Bot size={12} /><span>classify a song first to ask about it</span></>
        }
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <p className={styles.empty}>
            {songContext
              ? `Ask me anything about ${songContext.title} — its genre, sentiment, similar artists...`
              : "Classify a song, then come here to ask questions about it."
            }
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`${styles.msg} ${m.role === "user" ? styles.user : styles.assistant}`}>
            {m.content}
          </div>
        ))}
        {loading && (
          <div className={`${styles.msg} ${styles.assistant} ${styles.thinking}`}>
            <Loader2 size={12} className={styles.spin} />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <input
          className={styles.input}
          placeholder="ask about this song..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading || !songContext}
        />
        <button
          className={styles.sendBtn}
          onClick={send}
          disabled={loading || !input.trim() || !songContext}
        >
          <Send size={14} />
        </button>
      </div>
    </div>
  )
}