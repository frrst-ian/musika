import { Music2, ExternalLink, AlertTriangle, HelpCircle } from "lucide-react";
import SentimentBadge from "./SentimentBadge";
import styles from "./ResultCard.module.css";

function confidenceColor(val) {
  if (val >= 70) return "var(--primary)";
  if (val >= 40) return "var(--secondary)";
  return "var(--accent)";
}

function getWarning(confidence, sorted) {
  const [first, second] = sorted;
  if (confidence < 40)
    return {
      icon: AlertTriangle,
      text: "Low confidence — lyrics may be too short, mixed-language, or genre-blending.",
    };
  if (second && first[1] - second[1] < 10)
    return {
      icon: HelpCircle,
      text: `Close call between ${first[0]} and ${second[0]} — result may vary.`,
    };
  return null;
}

export default function ResultCard({ result }) {
  const {
    title,
    artist,
    url,
    thumbnail,
    youtube_url,
    genre,
    confidence,
    all_scores,
    sentiment,
    emotion,
    compound,
    scores,
  } = result;
  const sorted = Object.entries(all_scores).sort((a, b) => b[1] - a[1]);
  const warning = getWarning(confidence, sorted);

  return (
    <div className={styles.card}>
      <div className={styles.meta}>
        {thumbnail ? (
          <img className={styles.thumb} src={thumbnail} alt={title} />
        ) : (
          <div className={styles.thumbPlaceholder}>
            <Music2 size={20} />
          </div>
        )}
        <div className={styles.info}>
          <p className={styles.title}>{title}</p>
          <p className={styles.artist}>{artist}</p>
          <div className={styles.links}>
            {url && (
              <a
                className={styles.link}
                href={url}
                target="_blank"
                rel="noreferrer"
              >
                genius <ExternalLink size={10} />
              </a>
            )}
            {youtube_url && (
              <a
                className={styles.link}
                href={youtube_url}
                target="_blank"
                rel="noreferrer"
              >
                youtube <ExternalLink size={10} />
              </a>
            )}
          </div>
        </div>
        <span className={styles.badge}>{genre}</span>
      </div>

      {warning && (
        <div className={styles.warning}>
          <warning.icon size={13} />
          <span>{warning.text}</span>
        </div>
      )}

      <div className={styles.section}>
        <div className={styles.confRow}>
          <span className={styles.label}>confidence</span>
          <span
            className={styles.confVal}
            style={{ color: confidenceColor(confidence) }}
          >
            {confidence.toFixed(1)}%
          </span>
        </div>
        <div className={styles.meter}>
          <div
            className={styles.meterFill}
            style={{
              width: `${confidence}%`,
              background: confidenceColor(confidence),
            }}
          />
        </div>
      </div>

      {sentiment && (
        <div className={styles.section}>
          <SentimentBadge
            sentiment={sentiment}
            emotion={emotion}
            compound={compound}
            scores={scores}
          />
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
                    background:
                      g === genre ? "var(--primary)" : "rgba(154,223,158,.2)",
                  }}
                />
              </div>
              <span className={styles.scoreNum}>{score.toFixed(0)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
