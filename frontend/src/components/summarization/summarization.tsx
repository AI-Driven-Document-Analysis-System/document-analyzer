"use client"

import { useState } from "react"

const models = [
  {
    id: "pegasus",
    name: "Pegasus",
    description: "Best for news articles and general content",
    icon: "⚡",
    strengths: ["News articles", "General content", "Fast processing"],
  },
  {
    id: "bart",
    name: "BART",
    description: "Excellent for detailed summaries",
    icon: "🎯",
    strengths: ["Detailed summaries", "Technical content", "High accuracy"],
  },
  {
    id: "t5",
    name: "T5",
    description: "Great for academic and research papers",
    icon: "📚",
    strengths: ["Academic papers", "Research content", "Complex documents"],
  },
]

const documents = [
  { id: "1", name: "Financial Report Q4.pdf", type: "Financial Document", pages: 45 },
  { id: "2", name: "Research Paper.pdf", type: "Academic Paper", pages: 23 },
  { id: "3", name: "Legal Contract.pdf", type: "Legal Document", pages: 12 },
]

export function Summarization() {
  const [selectedDocument, setSelectedDocument] = useState("")
  const [selectedModel, setSelectedModel] = useState("pegasus")
  const [summaryType, setSummaryType] = useState("brief")
  const [summaryLength, setSummaryLength] = useState(150)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedSummary, setGeneratedSummary] = useState("")

  const handleGenerateSummary = async () => {
    if (!selectedDocument) return

    setIsGenerating(true)

    // Simulate API call
    setTimeout(() => {
      setGeneratedSummary(
        `This is a ${summaryType} summary generated using the ${models.find((m) => m.id === selectedModel)?.name} model. The document contains important information about financial performance, market trends, and strategic initiatives. Key findings include revenue growth of 15% year-over-year, expansion into new markets, and improved operational efficiency. The analysis reveals strong fundamentals and positive outlook for the coming quarters.`,
      )
      setIsGenerating(false)
    }, 3000)
  }

  const selectedModelData = models.find((m) => m.id === selectedModel)

  return (
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Summarization</h1>
        <p className="text-gray-600">Generate intelligent summaries using advanced AI models</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Document Selection */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">📄 Select Document</h2>
            </div>
            <div className="card-content">
              <select
                className="form-select"
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
              >
                <option value="">Choose a document</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name} ({doc.type} • {doc.pages} pages)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Model Selection */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">🧠 AI Model</h2>
              <p className="card-description">Choose the best model for your content type</p>
            </div>
            <div className="card-content">
              <div className="space-y-4">
                {models.map((model) => (
                  <div key={model.id} className="flex items-start gap-3">
                    <input
                      type="radio"
                      id={model.id}
                      name="model"
                      value={model.id}
                      checked={selectedModel === model.id}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <label htmlFor={model.id} className="cursor-pointer">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{model.icon}</span>
                          <span className="font-medium">{model.name}</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                        <div className="flex flex-wrap gap-1">
                          {model.strengths.map((strength) => (
                            <span key={strength} className="badge badge-secondary text-xs">
                              {strength}
                            </span>
                          ))}
                        </div>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Summary Options */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title flex items-center gap-2">⚙️ Summary Options</h2>
            </div>
            <div className="card-content space-y-4">
              <div>
                <label className="form-label">Summary Type</label>
                <div className="space-y-2">
                  {["brief", "detailed", "key-points"].map((type) => (
                    <div key={type} className="flex items-center gap-2">
                      <input
                        type="radio"
                        id={type}
                        name="summaryType"
                        value={type}
                        checked={summaryType === type}
                        onChange={(e) => setSummaryType(e.target.value)}
                      />
                      <label htmlFor={type} className="capitalize">
                        {type.replace("-", " ")}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="form-label">Summary Length: {summaryLength} words</label>
                <input
                  type="range"
                  min="50"
                  max="500"
                  step="25"
                  value={summaryLength}
                  onChange={(e) => setSummaryLength(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={handleGenerateSummary}
                disabled={!selectedDocument || isGenerating}
                className="btn btn-primary w-full"
              >
                {isGenerating ? <>✨ Generating...</> : <>✨ Generate Summary</>}
              </button>
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="card h-full">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="card-title flex items-center gap-2">✨ Generated Summary</h2>
                  {selectedModelData && (
                    <p className="card-description flex items-center gap-2 mt-1">
                      <span>{selectedModelData.icon}</span>
                      Generated using {selectedModelData.name} model
                    </p>
                  )}
                </div>
                {generatedSummary && (
                  <div className="flex gap-2">
                    <button className="btn btn-sm btn-outline">📋 Copy</button>
                    <button className="btn btn-sm btn-outline">💾 Export</button>
                  </div>
                )}
              </div>
            </div>
            <div className="card-content">
              {generatedSummary ? (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg border">
                    <textarea
                      value={generatedSummary}
                      readOnly
                      className="form-textarea border-0 bg-transparent resize-none"
                      style={{ minHeight: "300px" }}
                    />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>Word count: {generatedSummary.split(" ").length}</span>
                    <span>•</span>
                    <span>Model: {selectedModelData?.name}</span>
                    <span>•</span>
                    <span>Type: {summaryType}</span>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center" style={{ height: "400px" }}>
                  <div className="text-6xl mb-4">🧠</div>
                  <h3 className="text-lg font-medium text-gray-600 mb-2">No summary generated yet</h3>
                  <p className="text-sm text-gray-500 max-w-md">
                    Select a document and configure your preferences, then click "Generate Summary" to create an
                    AI-powered summary.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
