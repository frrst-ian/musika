import styles from "./SentimentBadge.module.css"

const EMOTION_COLORS = {
  joyful:"var(--primary)", energetic:"var(--secondary)", positive:"var(--primary)",
  melancholic:"var(--accent)", angry:"#f87171", negative:"#f87171", neutral:"rgba(236,249,236,.4)",
}

export default function SentimentBadge({ sentiment, emotion, compound, scores }) {
  const color = EMOTION_COLORS[emotion] ?? "rgba(236,249,236,.4)"
  return (
    <div className={styles.wrap}>
      <div className={styles.row}>
        <span className={styles.label}>sentiment</span>
        <div className={styles.badges}>
          <span className={styles.badge} style={{ borderColor: color, color }}>{emotion}</span>
          <span className={styles.sub}>{sentiment}</span>
          <span className={styles.compound}>{compound >= 0 ? "+" : ""}{compound.toFixed(2)}</span>
        </div>
      </div>
      <div className={styles.bars}>
        {[{key:"pos",label:"pos",color:"var(--primary)"},{key:"neu",label:"neu",color:"rgba(236,249,236,.3)"},{key:"neg",label:"neg",color:"#f87171"}].map(({key,label,color:c})=>(
          <div key={key} className={styles.barRow}>
            <span className={styles.barLabel}>{label}</span>
            <div className={styles.barTrack}><div className={styles.barFill} style={{width:`${(scores[key]??0)*100}%`,background:c}}/></div>
            <span className={styles.barNum}>{((scores[key]??0)*100).toFixed(0)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}