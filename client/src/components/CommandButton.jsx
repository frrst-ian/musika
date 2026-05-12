import { useState } from "react"
import { Zap, Loader2 } from "lucide-react"
import styles from "./CommandButton.module.css"

const BASE = "http://localhost:8000"

export default function CommandButton({ lastResult, onAction }) {
  const [active, setActive] = useState(false)

  async function startSession() {
    setActive(true)
    await runLoop()
    setActive(false)
  }

  async function runLoop() {
    while (true) {
      try {
        const res = await fetch(`${BASE}/command/listen`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ last_result: lastResult }),
        })
        const data = await res.json()
        onAction(data)

        if (data.action === "stop" || data.action === "error") break
        if (data.session !== "active") break

      } catch {
        onAction({ action: "error", reason: "Could not reach server." })
        break
      }
    }
  }

  function handleClick() {
    if (active) return
    startSession()
  }

  return (
    <button
      className={`${styles.btn} ${active ? styles.active : ""}`}
      onClick={handleClick}
      disabled={active}
      title='Say "Musika" to start, "end Musika" to stop'
    >
      {active ? <Loader2 size={13} className={styles.spin} /> : <Zap size={13} />}
      <span>{active ? "session active..." : "musika"}</span>
    </button>
  )
}