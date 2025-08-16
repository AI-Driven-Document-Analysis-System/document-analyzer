
//Fetched user relevent documents

"use client"

import { useState, useEffect, useMemo } from "react"

export function Dashboard() {
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch user documents
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const token = localStorage.getItem("token")
        if (!token) {
          setError("No authentication token found. Please log in again.")
          return
        }

        const response = await fetch("http://localhost:8000/api/documents/", {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        })

        if (response.status === 401) {
          localStorage.removeItem("token")
          localStorage.removeItem("user")
          setError("Session expired. Please log in again.")
          return
        }

        if (!response.ok) {
          throw new Error("Failed to fetch documents")
        }

        const data = await response.json()
        setDocuments(data.documents || [])
      } catch (err) {
        console.error("Error fetching documents:", err)
        setError(err instanceof Error ? err.message : "Failed to load documents")
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  // Format date to relative time
  const formatRelativeTime = (isoString: string): string => {
    const past = new Date(isoString)
    const now = new Date()
    const diffInMs = now.getTime() - past.getTime()
    const diffInHours = diffInMs / (1000 * 60 * 60)
    const diffInDays = diffInHours / 24

    if (diffInHours < 1) return "Less than an hour ago"
    if (diffInHours < 24) return `${Math.floor(diffInHours)} hours ago`
    if (diffInDays < 7) return `${Math.floor(diffInDays)} days ago`
    return past.toLocaleDateString()
  }

  // Compute stats from real documents
  const stats = useMemo(() => {
    const total = documents.length
    const today = new Date().setHours(0, 0, 0, 0)
    const processedToday = documents.filter(
      (doc) =>
        doc.processing_status === "completed" &&
        new Date(doc.upload_date).getTime() >= today
    ).length
    const inQueue = documents.filter(doc => doc.processing_status === "processing").length
    const successRate = total > 0 ? ((processedToday / total) * 100).toFixed(1) : 0

    return [
      {
        title: "Total Documents",
        value: total.toLocaleString(),
        change: "+12%",
        icon: "📄",
      },
      {
        title: "Processed Today",
        value: processedToday.toString(),
        change: "+23%",
        icon: "✅",
      },
      {
        title: "Processing Queue",
        value: inQueue.toString(),
        change: inQueue > 0 ? "-5%" : "0%",
        icon: "⏰",
      },
      {
        title: "Success Rate",
        value: `${successRate}%`,
        change: "+0.5%",
        icon: "📈",
      },
    ]
  }, [documents])

  // Format recent documents
  const recentDocuments = useMemo(() => {
    return documents
      .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
      .slice(0, 3)
      .map((doc) => ({
        id: doc.id,
        name: doc.original_filename,
        type: doc.content_type?.split("/")[1]?.toUpperCase() || "FILE",
        status: doc.processing_status === "completed" ? "Completed" : 
                doc.processing_status === "processing" ? "Processing" : "Failed",
        uploadedAt: formatRelativeTime(doc.upload_date),
        confidence: doc.processing_status === "completed" ? 95 : null,
      }))
  }, [documents])

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        <p className="mt-4 text-gray-600">Loading your dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-300 rounded-lg p-4 text-red-700">
          {error}
        </div>
      </div>
    )
  }

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
            {recentDocuments.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No documents uploaded yet.</p>
            ) : (
              <div className="space-y-4">
                {recentDocuments.map((doc) => (
                  <div key={doc.id} className="p-4 bg-gray-50 rounded-lg border hover:bg-gray-100 hover:shadow-md transition-all duration-200 cursor-pointer">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{doc.name}</h4>
                        <div className="flex items-center gap-4 mt-1">
                          <span className="badge badge-secondary text-xs">{doc.type}</span>
                          <span className="text-xs text-gray-500">{doc.uploadedAt}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {doc.confidence !== null && (
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
                    <div className="flex gap-3">
                      <button className="btn btn-primary flex-1 text-sm">
                        💬 Summarize
                      </button>
                      <button className="btn btn-primary flex-1 text-sm">
                        💬 Chat with Doc
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
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


