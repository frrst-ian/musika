import { Search, Mic, Music } from "lucide-react"
import styles from "./ModeToggle.module.css"

const MODES = [
  { id: "search",     label: "search",     Icon: Search },
  { id: "stt",      label: "voice",    Icon: Mic },
  { id: "identify", label: "identify", Icon: Music },
]

export default function ModeToggle({ mode, onChange }) {
  return (
    <div className={styles.group}>
      {MODES.map(({ id, label, Icon }) => (
        <button key={id} className={`${styles.btn} ${mode === id ? styles.active : ""}`} onClick={() => onChange(id)}>
          <Icon size={13} />{label}
        </button>
      ))}
    </div>
  )
}