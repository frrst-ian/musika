import { Volume2, VolumeX } from "lucide-react"
import styles from "./TTSToggle.module.css"

export default function TTSToggle({ enabled, onChange }) {
  return (
    <button className={`${styles.btn} ${enabled ? styles.on : ""}`} onClick={() => onChange(!enabled)}>
      {enabled ? <Volume2 size={13} /> : <VolumeX size={13} />}
      <span>{enabled ? "tts on" : "tts off"}</span>
    </button>
  )
}