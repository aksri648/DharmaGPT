import type { Tab } from "../types"

interface SidebarProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "upload", label: "Upload PDF", icon: "📄" },
  { id: "settings", label: "Settings", icon: "⚙️" },
]

export default function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-logo">DharmaGPT</h1>
        <p className="sidebar-subtitle">Wisdom of the Gita & Ramayana</p>
      </div>
      <nav className="sidebar-nav">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`sidebar-btn ${activeTab === t.id ? "active" : ""}`}
            onClick={() => onTabChange(t.id)}
          >
            <span className="sidebar-btn-icon">{t.icon}</span>
            <span className="sidebar-btn-label">{t.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
