import { useState, useRef } from "react"
import { Zap, Loader2 } from "lucide-react"
import styles from "./CommandButton.module.css"

const BASE = "http://localhost:8000"
const TIMEOUT_MS = 3 * 60 * 1000

export default function CommandButton({ lastResult, onAction }) {
  const [active, setActive] = useState(false)
  const timerRef = useRef(null)

  function resetTimer(stopFn) {
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      stopFn()
      onAction({ action: "stop", reason: "timeout" })
    }, TIMEOUT_MS)
  }

  function clearTimer() {
    clearTimeout(timerRef.current)
    timerRef.current = null
  }

  async function startSession() {
    setActive(true)

    let running = true
    function stop() { running = false }

    resetTimer(stop)

    while (running) {
      try {
        const res = await fetch(`${BASE}/command/listen`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ last_result: lastResult }),
        })
        const data = await res.json()

        if (!running) break

        if (data.action !== "none") resetTimer(stop)

        onAction(data)

        if (data.action === "stop" || data.action === "error") break
        if (data.session !== "active") break

      } catch {
        onAction({ action: "error", reason: "Could not reach server." })
        break
      }
    }

    clearTimer()
    setActive(false)
  }

  return (
    <button
      className={`${styles.btn} ${active ? styles.active : ""}`}
      onClick={() => { if (!active) startSession() }}
      disabled={active}
      title='Say "musika" to start, "end" to stop'
    >
      {active ? <Loader2 size={13} className={styles.spin} /> : <Zap size={13} />}
      <span>{active ? "session active..." : "musika"}</span>
    </button>
  )
}