"use client"

interface SidebarProps {
  isOpen: boolean
  onNavigate: (path: string) => void
  currentRoute: string
  onToggle: () => void
  user: any
  onLogout: () => void
}

const navigationItems = [
  {
    title: "Overview",
    items: [
      { title: "Dashboard", url: "/dashboard", icon: "fas fa-home" },
      { title: "Upload Documents", url: "/upload", icon: "fas fa-cloud-upload-alt" },
      { title: "My Documents", url: "/documents", icon: "fas fa-file-alt" },
    ],
  },
  {
    title: "Analysis",
    items: [
      { title: "Document Viewer", url: "/viewer", icon: "fas fa-eye" },
      { title: "Classification", url: "/classification", icon: "fas fa-tags" },
      { title: "Summarization", url: "/summarization", icon: "fas fa-brain" },
      { title: "Search", url: "/search", icon: "fas fa-search" },
      { title: "AI Chat", url: "/chat", icon: "fas fa-robot" },
    ],
  },
  {
    title: "Insights",
    items: [{ title: "Analytics", url: "/analytics", icon: "fas fa-chart-bar" }],
  },
  {
    title: "Account",
    items: [
      { title: "Profile", url: "/profile", icon: "fas fa-user" },
      { title: "Subscription", url: "/subscription", icon: "fas fa-credit-card" },
      { title: "Settings", url: "/settings", icon: "fas fa-cog" },
    ],
  },
]

export function Sidebar({ isOpen, onNavigate, currentRoute, onToggle, user, onLogout }: SidebarProps) {
  return (
    <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <i className="fas fa-brain"></i>
          </div>
          <span className="sidebar-logo-text">DocuMind AI</span>
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
                  <i className={`nav-icon ${item.icon}`}></i>
                  <span>{item.title}</span>
                </button>
              </div>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">{user?.firstName?.[0]?.toUpperCase() || "U"}</div>
          <div className="user-details">
            <div className="user-name">
              {user?.firstName} {user?.lastName}
            </div>
            <div className="user-email">{user?.email}</div>
          </div>
          <button className="logout-button" onClick={onLogout} title="Logout">
            <i className="fas fa-sign-out-alt"></i>
          </button>
        </div>
      </div>
    </div>
  )
}
