const stats = [
  {
    title: "Total Documents",
    value: "1,234",
    change: "+12%",
    icon: "📄",
  },
  {
    title: "Processed Today",
    value: "89",
    change: "+23%",
    icon: "✅",
  },
  {
    title: "Processing Queue",
    value: "12",
    change: "-5%",
    icon: "⏰",
  },
  {
    title: "Success Rate",
    value: "98.5%",
    change: "+0.5%",
    icon: "📈",
  },
]

const recentDocuments = [
  {
    id: "1",
    name: "Financial Report Q4.pdf",
    type: "Financial Document",
    status: "Completed",
    uploadedAt: "2 hours ago",
    confidence: 95,
  },
  {
    id: "2",
    name: "Legal Contract.pdf",
    type: "Legal Document",
    status: "Processing",
    uploadedAt: "5 hours ago",
    confidence: null,
  },
  {
    id: "3",
    name: "Research Paper.pdf",
    type: "Academic Paper",
    status: "Completed",
    uploadedAt: "1 day ago",
    confidence: 88,
  },
]

export function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's what's happening with your documents.</p>
        </div>
        <button className="btn btn-primary">📤 Upload Document</button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        {stats.map((stat) => (
          <div key={stat.title} className="card">
            <div className="card-content">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">{stat.title}</h3>
                <span className="text-2xl">{stat.icon}</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
                <span className={`badge ${stat.change.startsWith("+") ? "badge-success" : "badge-warning"}`}>
                  {stat.change}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent Documents */}
        <div className="card" style={{ gridColumn: "span 2" }}>
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">📄 Recent Documents</h2>
            <p className="card-description">Your latest document processing activities</p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {recentDocuments.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{doc.name}</h4>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="badge badge-secondary text-xs">{doc.type}</span>
                      <span className="text-xs text-gray-500">{doc.uploadedAt}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {doc.confidence && (
                      <div className="text-right">
                        <div className="text-sm font-medium">{doc.confidence}%</div>
                        <div className="progress" style={{ width: "64px" }}>
                          <div className="progress-bar" style={{ width: `${doc.confidence}%` }}></div>
                        </div>
                      </div>
                    )}
                    <span className={`badge ${doc.status === "Completed" ? "badge-success" : "badge-warning"}`}>
                      {doc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Quick Actions</h2>
            <p className="card-description">Common tasks and shortcuts</p>
          </div>
          <div className="card-content space-y-3">
            <button className="btn btn-outline w-full text-left">📤 Upload New Document</button>
            <button className="btn btn-outline w-full text-left">🧠 Generate Summary</button>
            <button className="btn btn-outline w-full text-left">🔍 Search Documents</button>
          </div>
        </div>
      </div>
    </div>
  )
}
