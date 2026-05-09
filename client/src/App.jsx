import { useState } from "react"
import SearchBar from "./components/SearchBar"
import ResultCard from "./components/ResultCard"
import styles from "./styles/app.module.css"

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSearch({ title, artist }) {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch("http://localhost:8000/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, artist }),
      })

      if (res.status === 404) {
        setError("Song not found. Try a different title or artist.")
        return
      }

      if (!res.ok) throw new Error("Server error")

      const data = await res.json()
      setResult(data)
    } catch {
      setError("Something went wrong. Is the server running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.logo}>musika</h1>
        <p className={styles.tagline}>genre classifier</p>
      </header>

      <main className={styles.main}>
        <SearchBar onSearch={handleSearch} loading={loading} />

        {error && <p className={styles.error}>{error}</p>}

        {result && <ResultCard result={result} />}
      </main>
    </div>
  )
}