import { Component } from "react"

export default class ErrorBoundary extends Component {
  state = { crashed: false }

  static getDerivedStateFromError() {
    return { crashed: true }
  }

  render() {
    if (this.state.crashed) return (
      <div style={{
        border: "1px solid rgba(248,113,113,0.3)",
        background: "rgba(248,113,113,0.06)",
        color: "#f87171",
        padding: "0.75rem 1rem",
        borderRadius: "6px",
        fontSize: "0.875rem",
      }}>
        Something broke rendering this result. Try another search.
      </div>
    )
    return this.props.children
  }
}