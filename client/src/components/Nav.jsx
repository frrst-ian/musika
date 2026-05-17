import { Search, ListMusic, MessageSquare, BarChart2, Settings } from "lucide-react"
import styles from "./Nav.module.css"

const LEFT_TABS = [
  { id: "classify", label: "classify", Icon: Search },
  { id: "playlist", label: "playlist", Icon: ListMusic },
  { id: "chat",     label: "chat",     Icon: MessageSquare },
  { id: "stats",    label: "stats",    Icon: BarChart2 },
]

export default function Nav({ active, onChange }) {
  return (
    <nav className={styles.nav}>
      <div className={styles.left}>
        {LEFT_TABS.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`${styles.tab} ${active === id ? styles.active : ""}`}
            onClick={() => onChange(id)}
          >
            <Icon size={13} />
            <span>{label}</span>
          </button>
        ))}
      </div>
      <button
        className={`${styles.tab} ${styles.settingsTab} ${active === "settings" ? styles.active : ""}`}
        onClick={() => onChange("settings")}
      >
        <Settings size={13} />
        <span>settings</span>
      </button>
    </nav>
  )
}