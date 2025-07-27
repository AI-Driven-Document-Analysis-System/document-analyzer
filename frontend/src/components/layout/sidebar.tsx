"use client"

interface SidebarProps {
  isOpen: boolean
  onNavigate: (path: string) => void
  currentRoute: string
  onToggle: () => void
}

const navigationItems = [
  {
    title: "Overview",
    items: [
      { title: "Dashboard", url: "/dashboard", icon: "🏠" },
      { title: "Upload Documents", url: "/upload", icon: "📤" },
      { title: "My Documents", url: "/documents", icon: "📄" },
    ],
  },
  {
    title: "Analysis",
    items: [
      { title: "Document Viewer", url: "/viewer", icon: "👁️" },
      { title: "Classification", url: "/classification", icon: "🏷️" },
      { title: "Summarization", url: "/summarization", icon: "🧠" },
      { title: "Search", url: "/search", icon: "🔍" },
      { title: "AI Chat", url: "/chat", icon: "💬" },
    ],
  },
  {
    title: "Insights",
    items: [{ title: "Analytics", url: "/analytics", icon: "📊" }],
  },
  {
    title: "Account",
    items: [
      { title: "Profile", url: "/profile", icon: "👤" },
      { title: "Subscription", url: "/subscription", icon: "💳" },
      { title: "Settings", url: "/settings", icon: "⚙️" },
    ],
  },
]

export function Sidebar({ isOpen, onNavigate, currentRoute, onToggle }: SidebarProps) {
  return (
    <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">📄</div>
          <span className="sidebar-logo-text">DocAnalyzer</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((group) => (
          <div key={group.title} className="nav-group">
            <div className="nav-group-label">{group.title}</div>
            {group.items.map((item) => (
              <div key={item.title} className="nav-item">
                <button
                  className={`nav-link ${currentRoute === item.url ? "active" : ""}`}
                  onClick={() => onNavigate(item.url)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span>{item.title}</span>
                </button>
              </div>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">JD</div>
          <div className="user-details">
            <div className="user-name">John Doe</div>
            <div className="user-email">john@example.com</div>
          </div>
        </div>
      </div>
    </div>
  )
}
