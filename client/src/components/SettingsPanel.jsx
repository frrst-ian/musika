import { useEffect, useState } from "react"
import { User, Mail, Calendar, Music2, LogOut, Loader2 } from "lucide-react"
import styles from "./SettingsPanel.module.css"

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

function formatDate(iso) {
  if (!iso) return "—"
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
}

export default function SettingsPanel({ token, logout }) {
  const [me, setMe] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setMe)
      .catch(() => setMe(null))
      .finally(() => setLoading(false))
  }, [token])

  return (
    <div className={styles.panel}>
      <section className={styles.section}>
        <p className={styles.sectionLabel}>account</p>

        {loading ? (
          <div className={styles.center}>
            <Loader2 size={16} className={styles.spin} />
          </div>
        ) : me ? (
          <div className={styles.infoList}>
            <div className={styles.infoRow}>
              <User size={13} className={styles.icon} />
              <span className={styles.infoLabel}>username</span>
              <span className={styles.infoValue}>{me.username}</span>
            </div>
            <div className={styles.infoRow}>
              <Mail size={13} className={styles.icon} />
              <span className={styles.infoLabel}>email</span>
              <span className={styles.infoValue}>{me.email}</span>
            </div>
            <div className={styles.infoRow}>
              <Calendar size={13} className={styles.icon} />
              <span className={styles.infoLabel}>member since</span>
              <span className={styles.infoValue}>{formatDate(me.created_at)}</span>
            </div>
            <div className={styles.infoRow}>
              <Music2 size={13} className={styles.icon} />
              <span className={styles.infoLabel}>songs classified</span>
              <span className={styles.infoValue}>{me.total_classified}</span>
            </div>
          </div>
        ) : (
          <p className={styles.empty}>could not load user info.</p>
        )}
      </section>

      <section className={styles.section}>
        <p className={styles.sectionLabel}>session</p>
        <button className={styles.logoutBtn} onClick={logout}>
          <LogOut size={13} />
          <span>log out</span>
        </button>
      </section>
    </div>
  )
}