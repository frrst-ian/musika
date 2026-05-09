import { useState } from "react"
import { Search, Loader2 } from "lucide-react"
import styles from "./SearchBar.module.css"

export default function SearchBar({ onSearch, loading }) {
  const [title, setTitle] = useState("")
  const [artist, setArtist] = useState("")

  function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim() || !artist.trim()) return
    onSearch({ title: title.trim(), artist: artist.trim() })
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.inputs}>
        <input
          className={styles.input}
          type="text"
          placeholder="song title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
        />
        <input
          className={styles.input}
          type="text"
          placeholder="artist"
          value={artist}
          onChange={(e) => setArtist(e.target.value)}
          disabled={loading}
        />
      </div>
      <button className={styles.button} type="submit" disabled={loading || !title.trim() || !artist.trim()}>
        {loading
          ? <Loader2 size={16} className={styles.spin} />
          : <Search size={16} />
        }
        {loading ? "classifying" : "classify"}
      </button>
    </form>
  )
}