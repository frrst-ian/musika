import { useEffect, useState } from "react"
import { ExternalLink, Loader2 } from "lucide-react"
import styles from "./StatsPanel.module.css"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

const EMOTION_COLORS = {
  joyful: "var(--primary)",
  energetic: "var(--secondary)",
  positive: "var(--primary)",
  melancholic: "var(--accent)",
  angry: "#f87171",
  negative: "#f87171",
  neutral: "rgba(236,249,236,.35)",
}

export default function StatsPanel({ token }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [token])

  if (loading) {
    return (
      <div className={styles.center}>
        <Loader2 size={16} className={styles.spin} />
      </div>
    )
  }

  if (!data || data.top_songs.length === 0) {
    return <p className={styles.empty}>no data yet — classify some songs first.</p>
  }

  const totalGenre = data.genre_distribution.reduce((s, r) => s + r.count, 0)
  const totalSentiment = data.sentiment_breakdown.reduce((s, r) => s + r.count, 0)

  return (
    <div className={styles.panel}>
      <section className={styles.section}>
        <p className={styles.label}>genre distribution</p>
        <div className={styles.bars}>
          {data.genre_distribution.map(({ genre, count }) => (
            <div key={genre} className={styles.barRow}>
              <span className={styles.barLabel}>{genre}</span>
              <div className={styles.barTrack}>
                <div
                  className={styles.barFill}
                  style={{ width: `${(count / totalGenre) * 100}%`, background: "var(--primary)" }}
                />
              </div>
              <span className={styles.barNum}>{count}</span>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <p className={styles.label}>sentiment breakdown</p>
        <div className={styles.bars}>
          {data.sentiment_breakdown.map(({ emotion, sentiment, count }) => {
            const color = EMOTION_COLORS[emotion] ?? "rgba(236,249,236,.35)"
            return (
              <div key={`${emotion}-${sentiment}`} className={styles.barRow}>
                <span className={styles.barLabel} style={{ color }}>{emotion}</span>
                <div className={styles.barTrack}>
                  <div
                    className={styles.barFill}
                    style={{ width: `${(count / totalSentiment) * 100}%`, background: color }}
                  />
                </div>
                <span className={styles.barNum}>{count}</span>
              </div>
            )
          })}
        </div>
      </section>

      <section className={styles.section}>
        <p className={styles.label}>top searched songs</p>
        <div className={styles.topList}>
          {data.top_songs.map((s, i) => (
            <div key={`${s.title}-${s.artist}`} className={styles.topRow}>
              <span className={styles.rank}>{i + 1}</span>
              <div className={styles.topInfo}>
                <span className={styles.topTitle}>{s.title}</span>
                <span className={styles.topArtist}>{s.artist}</span>
              </div>
              <div className={styles.topMeta}>
                <span className={styles.topGenre}>{s.genre}</span>
                <span className={styles.topCount}>×{s.search_count}</span>
                {s.youtube_url && (
                  <a href={s.youtube_url} target="_blank" rel="noreferrer" className={styles.topLink}>
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}