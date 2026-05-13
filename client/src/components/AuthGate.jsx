import { useState } from "react"
import { Loader2 } from "lucide-react"
import { useAuth } from "../hooks/useAuth"
import styles from "./AuthGate.module.css"

export default function AuthGate({ children }) {
  const { user, token, loading, error, loginEmail, signupEmail, loginGoogle, logout } = useAuth()
  const [mode, setMode] = useState("login")
  const [email, setEmail]       = useState("")
  const [password, setPassword] = useState("")
  const [username, setUsername] = useState("")
  const [busy, setBusy]         = useState(false)

  if (loading) return (
    <div className={styles.center}>
      <Loader2 size={20} className={styles.spin} />
    </div>
  )

  if (user && token) return children({ token, user, logout })

  async function handleSubmit() {
    setBusy(true)
    if (mode === "login") await loginEmail(email, password)
    else await signupEmail(email, password, username)
    setBusy(false)
  }

  async function handleGoogle() {
    setBusy(true)
    await loginGoogle()
    setBusy(false)
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.logo}>musika</h1>
        <p className={styles.tagline}>music genre classifier</p>

        <div className={styles.tabs}>
          <button className={`${styles.tab} ${mode === "login" ? styles.activeTab : ""}`} onClick={() => setMode("login")}>login</button>
          <button className={`${styles.tab} ${mode === "signup" ? styles.activeTab : ""}`} onClick={() => setMode("signup")}>sign up</button>
        </div>

        <div className={styles.fields}>
          {mode === "signup" && (
            <input
              className={styles.input}
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={busy}
            />
          )}
          <input
            className={styles.input}
            placeholder="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={busy}
          />
          <input
            className={styles.input}
            placeholder="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={busy}
          />
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button className={styles.submitBtn} onClick={handleSubmit} disabled={busy}>
          {busy ? <Loader2 size={14} className={styles.spin} /> : null}
          {mode === "login" ? "login" : "create account"}
        </button>

        <div className={styles.divider}><span>or</span></div>

        <button className={styles.googleBtn} onClick={handleGoogle} disabled={busy}>
          continue with google
        </button>
      </div>
    </div>
  )
}