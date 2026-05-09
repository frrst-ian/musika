import { Music2, ExternalLink, AlertTriangle, HelpCircle } from "lucide-react"
import styles from "./ResultCard.module.css"

function confidenceColor(val) {
  if (val >= 70) return "var(--primary)"
  if (val >= 40) return "var(--secondary)"
  return "var(--accent)"
}

function getWarning(confidence, sorted) {
  const [first, second] = sorted
  const isLowConfidence = confidence < 40
  const isAmbiguous = second && (first[1] - second[1]) < 10

  if (isLowConfidence) return {
    icon: AlertTriangle,
    text: "Low confidence — lyrics may be too short, mixed-language, or genre-blending.",
  }
  if (isAmbiguous) return {
    icon: HelpCircle,
    text: `Close call between ${first[0]} and ${second[0]} — result may vary.`,
  }
  return null
}

export default function ResultCard({ result }) {
  const { title, artist, url, thumbnail, genre, confidence, all_scores } = result

  const sorted = Object.entries(all_scores).sort((a, b) => b[1] - a[1])
  const warning = getWarning(confidence, sorted)

  return (
    <div className={styles.card}>
      <div className={styles.meta}>
        {thumbnail
          ? <img className={styles.thumb} src={thumbnail} alt={title} />
          : <div className={styles.thumbPlaceholder}><Music2 size={20} /></div>
        }
        <div className={styles.info}>
          <p className={styles.title}>{title}</p>
          <p className={styles.artist}>{artist}</p>
          {url && (
            <a className={styles.link} href={url} target="_blank" rel="noreferrer">
              genius <ExternalLink size={10} />
            </a>
          )}
        </div>
        <span className={styles.badge}>{genre}</span>
      </div>

      <div className={styles.section}>
        <div className={styles.confRow}>
          <span className={styles.label}>confidence</span>
          <span className={styles.confVal} style={{ color: confidenceColor(confidence) }}>
            {confidence.toFixed(1)}%
          </span>
        </div>
        <div className={styles.meter}>
          <div
            className={styles.meterFill}
            style={{ width: `${confidence}%`, background: confidenceColor(confidence) }}
          />
        </div>
      </div>

      {warning && (
        <div className={styles.warning}>
          <warning.icon size={13} />
          <span>{warning.text}</span>
        </div>
      )}

      <div className={styles.section}>
        <p className={styles.label}>all scores</p>
        <div className={styles.scores}>
          {sorted.map(([g, score]) => (
            <div key={g} className={styles.scoreRow}>
              <span className={styles.scoreGenre}>{g}</span>
              <div className={styles.scoreBar}>
                <div
                  className={styles.scoreBarFill}
                  style={{
                    width: `${score}%`,
                    background: g === genre ? "var(--primary)" : "rgba(154, 223, 158, 0.2)",
                  }}
                />
              </div>
              <span className={styles.scoreNum}>{score.toFixed(0)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}