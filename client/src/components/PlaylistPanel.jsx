import { useState, useEffect } from "react"
import { ListMusic, TrendingUp, Trash2, ExternalLink } from "lucide-react"
import styles from "./PlaylistPanel.module.css"

const BASE = "http://localhost:8000"

function SongRow({ song, onRemove }) {
  return (
    <div className={styles.row}>
      <div className={styles.rowInfo}>
        <span className={styles.rowTitle}>{song.title}</span>
        <span className={styles.rowArtist}>{song.artist}</span>
      </div>
      <div className={styles.rowMeta}>
        <span className={styles.rowGenre}>{song.genre}</span>
        <span className={styles.rowCount}>×{song.search_count}</span>
        {song.youtube_url && (
          <a href={song.youtube_url} target="_blank" rel="noreferrer" className={styles.rowLink}>
            <ExternalLink size={12} />
          </a>
        )}
        <button className={styles.removeBtn} onClick={() => onRemove(song)}>
          <Trash2 size={12} />
        </button>
      </div>
    </div>
  )
}

export default function PlaylistPanel() {
  const [tab, setTab] = useState("top")
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)

  async function fetchSongs() {
    setLoading(true)
    try {
      const endpoint = tab === "top" ? "/playlist/top" : "/playlist"
      const res = await fetch(`${BASE}${endpoint}`)
      const data = await res.json()
      setSongs(data.songs)
    } catch {
      setSongs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSongs() }, [tab])

  async function handleRemove(song) {
    await fetch(`${BASE}/playlist?title=${encodeURIComponent(song.title)}&artist=${encodeURIComponent(song.artist)}`, {
      method: "DELETE",
    })
    fetchSongs()
  }

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${tab === "top" ? styles.activeTab : ""}`}
            onClick={() => setTab("top")}
          >
            <TrendingUp size={12} /> top
          </button>
          <button
            className={`${styles.tab} ${tab === "all" ? styles.activeTab : ""}`}
            onClick={() => setTab("all")}
          >
            <ListMusic size={12} /> all
          </button>
        </div>
        <button className={styles.refreshBtn} onClick={fetchSongs}>refresh</button>
      </div>

      <div className={styles.list}>
        {loading && <p className={styles.empty}>loading...</p>}
        {!loading && songs.length === 0 && (
          <p className={styles.empty}>no songs yet — classify something first.</p>
        )}
        {!loading && songs.map((s, i) => (
          <SongRow key={`${s.title}-${s.artist}-${i}`} song={s} onRemove={handleRemove} />
        ))}
      </div>
    </div>
  )
}