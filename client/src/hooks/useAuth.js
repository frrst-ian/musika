import { useState, useEffect } from "react"
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
} from "firebase/auth"
import { auth, googleProvider } from "../firebase"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function initUserDoc(token, email, username) {
  await fetch(`${BASE}/user/init`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ email, username }),
  })
}

export function useAuth() {
  const [user, setUser]   = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (u) => {
      if (u) {
        const t = await u.getIdToken()
        setUser(u)
        setToken(t)
      } else {
        setUser(null)
        setToken(null)
      }
      setLoading(false)
    })
    return unsub
  }, [])

  // token refreshes every hour — keep it fresh
  useEffect(() => {
    if (!user) return
    const interval = setInterval(async () => {
      const t = await user.getIdToken(true)
      setToken(t)
    }, 55 * 60 * 1000)
    return () => clearInterval(interval)
  }, [user])

  async function loginEmail(email, password) {
    setError(null)
    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch (e) {
      setError(e.message)
    }
  }

  async function signupEmail(email, password, username) {
    setError(null)
    try {
      const cred = await createUserWithEmailAndPassword(auth, email, password)
      const t = await cred.user.getIdToken()
      await initUserDoc(t, email, username)
    } catch (e) {
      setError(e.message)
    }
  }

  async function loginGoogle() {
    setError(null)
    try {
      const cred = await signInWithPopup(auth, googleProvider)
      const t = await cred.user.getIdToken()
      const username = cred.user.displayName || cred.user.email.split("@")[0]
      await initUserDoc(t, cred.user.email, username)
    } catch (e) {
      setError(e.message)
    }
  }

  async function logout() {
    await signOut(auth)
  }

  return { user, token, loading, error, loginEmail, signupEmail, loginGoogle, logout }
}