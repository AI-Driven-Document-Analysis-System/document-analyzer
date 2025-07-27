"use client"

import { useState } from "react"

const searchResults = [
  {
    id: "1",
    title: "Financial Report Q4 2023.pdf",
    type: "Financial Document",
    excerpt: "Revenue increased by 15% year-over-year, driven by strong performance in the technology sector...",
    uploadDate: "2024-01-15",
    confidence: 95,
    tags: ["financial", "quarterly", "revenue"],
    pages: 45,
  },
  {
    id: "2",
    title: "Market Analysis Research.pdf",
    type: "Research Paper",
    excerpt: "The market analysis reveals significant trends in consumer behavior and emerging technologies...",
    uploadDate: "2024-01-10",
    confidence: 88,
    tags: ["market", "research", "analysis"],
    pages: 32,
  },
  {
    id: "3",
    title: "Legal Contract Agreement.pdf",
    type: "Legal Document",
    excerpt: "This agreement outlines the terms and conditions for the partnership between the parties...",
    uploadDate: "2024-01-08",
    confidence: 92,
    tags: ["legal", "contract", "agreement"],
    pages: 18,
  },
]

const documentTypes = [
  "All Types",
  "Financial Document",
  "Legal Document",
  "Research Paper",
  "Academic Paper",
  "Technical Manual",
  "Report",
]

export function SearchInterface() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedType, setSelectedType] = useState("All Types")
  const [dateRange, setDateRange] = useState("all")
  const [showFilters, setShowFilters] = useState(false)
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async () => {
    setIsSearching(true)
    // Simulate search API call
    setTimeout(() => {
      setIsSearching(false)
    }, 1500)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Search</h1>
        <p className="text-gray-600">Search through your documents using AI-powered semantic search</p>
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="card-content">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search documents, content, or ask questions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input text-lg"
                style={{ paddingLeft: "2.5rem", height: "48px" }}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="btn btn-primary"
              style={{ height: "48px", padding: "0 2rem" }}
            >
              {isSearching ? "Searching..." : "Search"}
            </button>
            <button
              className="btn btn-outline"
              onClick={() => setShowFilters(!showFilters)}
              style={{ height: "48px", padding: "0 1rem" }}
            >
              🔧
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Search Filters</h2>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="form-label">Document Type</label>
                <select className="form-select" value={selectedType} onChange={(e) => setSelectedType(e.target.value)}>
                  {documentTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label">Date Range</label>
                <select className="form-select" value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="year">This Year</option>
                </select>
              </div>

              <div>
                <label className="form-label">Options</label>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <input type="checkbox" id="semantic" />
                    <label htmlFor="semantic" className="text-sm">
                      Semantic Search
                    </label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" id="exact" />
                    <label htmlFor="exact" className="text-sm">
                      Exact Match
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      <div className="space-y-4">
        {searchResults.map((result) => (
          <div key={result.id} className="card">
            <div className="card-content">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xl">📄</span>
                    <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
                      {result.title}
                    </h3>
                    <span className="badge badge-secondary">{result.type}</span>
                  </div>

                  <p className="text-gray-600 mb-3">{result.excerpt}</p>

                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center gap-1">📅 {new Date(result.uploadDate).toLocaleDateString()}</div>
                    <div className="flex items-center gap-1">📄 {result.pages} pages</div>
                    <div className="flex items-center gap-1">⭐ {result.confidence}% match</div>
                  </div>

                  <div className="flex items-center gap-2">
                    {result.tags.map((tag) => (
                      <span key={tag} className="badge badge-primary text-xs">
                        🏷️ {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  <button className="btn btn-sm btn-outline">👁️ View</button>
                  <button className="btn btn-sm btn-outline">💾 Download</button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Search Stats */}
      <div className="card">
        <div className="card-content">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Found {searchResults.length} documents in 0.23 seconds</span>
            <div className="flex items-center gap-4">
              <span>Sort by:</span>
              <select className="form-select" style={{ width: "128px" }}>
                <option value="relevance">Relevance</option>
                <option value="date">Date</option>
                <option value="name">Name</option>
                <option value="type">Type</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
