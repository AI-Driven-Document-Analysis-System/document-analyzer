


"use client";

import { useState, useEffect } from "react";
import "./summarization.css"; // Adjust path if needed

type GeneratedSummary = {
  summary_text: string;
  document_name?: string;
  model_used?: string;
  created_at?: string;
  word_count?: number;
  summary_type?: string;
};

export default function Summarization() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocument, setSelectedDocument] = useState("");
  const [summaryType, setSummaryType] = useState("brief");
  const [summaryLength, setSummaryLength] = useState(150);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState("");

  const summaryOptions = [
    { id: "brief", name: "Brief Summary", desc: "Quick overview using BART model", model: "BART" },
    { id: "detailed", name: "Detailed Summary", desc: "Comprehensive analysis using Pegasus model", model: "Pegasus" },
    { id: "domain_specific", name: "Domain Specific", desc: "Specialized summary using T5 model", model: "Domain Specific Model" },
  ];

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authentication token found. Please log in again.");
        return;
      }

      const response = await fetch("http://localhost:8000/api/documents/", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setError("Session expired. Please log in again.");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
        setError("");
      } else {
        const errorData = await response.json();
        const msg = typeof errorData.detail === "string" ? errorData.detail : errorData.message || "Failed to fetch documents";
        setError(msg);
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError("Network error while fetching documents");
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedDocument) {
      setError("Please select a document first");
      return;
    }

    setIsGenerating(true);
    setError("");
    setProgress("AI is generating summary...");
    setGeneratedSummary(null);

    try {
      const token = localStorage.getItem("token");
      const requestBody = {
        document_id: selectedDocument,
        summary_type: summaryType,
        summary_length: summaryLength,
      };

      const response = await fetch("http://localhost:8000/api/summarize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setProgress("Summary generated successfully!");
        setGeneratedSummary({
          ...data,
          document_name: data.document_name || "Unknown Document",
          model_used: data.model_used || "AI Selected",
          created_at: data.created_at || new Date().toISOString(),
          word_count: data.word_count || 0,
          summary_type: data.summary_type || getSummaryTypeName(summaryType),
        });
      } else {
        let errorMessage = `Request failed (${response.status})`;
        if (response.status === 422 && data.detail) {
          errorMessage = Array.isArray(data.detail)
            ? data.detail.map((e: any) => `${e.loc?.join(".")}: ${e.msg}`).join(", ")
            : data.detail;
        } else if (data.detail) {
          errorMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        }
        setError(errorMessage);
      }
    } catch (err) {
      setError(`Network error: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setIsGenerating(false);
      setProgress("");
    }
  };

  const getSummaryTypeName = (typeId: string) => {
    const option = summaryOptions.find((opt) => opt.id === typeId);
    return option ? option.name : "Unknown";
  };

  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    if (generatedSummary?.summary_text) {
      try {
        await navigator.clipboard.writeText(generatedSummary.summary_text);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch {
        const textArea = document.createElement("textarea");
        textArea.value = generatedSummary.summary_text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      }
    }
  };

  const handleExport = () => {
    if (generatedSummary) {
      const content = `Document: ${generatedSummary.document_name}
Model: ${generatedSummary.model_used}
Type: ${generatedSummary.summary_type}
Generated: ${new Date(generatedSummary.created_at ?? "").toLocaleString()}

Summary:
${generatedSummary.summary_text}`;

      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `summary-${generatedSummary.document_name}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const selectedDocumentData = documents.find((d) => d.id === selectedDocument);

  return (
    <div className="summarization-container">
      {/* Header */}
      <div className="summarization-header">
        <h1>AI-Powered Document Summarization</h1>
        <p>Select your document and summary type to generate intelligent summaries</p>
      </div>

      {/* Success Message */}
      {progress && !isGenerating && (
        <div className="message-success">{progress}</div>
      )}

      {/* Error Message */}
      {error && (
        <div className="message-error">{error}</div>
      )}

      {/* Main Layout */}
      <div className="layout-grid">
        {/* Left Panel */}
        <div className="left-panel">
          {/* Document Selection */}
          <div className="card">
            <div className="card-header">
              <h2>Select Document</h2>
            </div>
            <div className="card-body document-select">
              <select value={selectedDocument} onChange={(e) => setSelectedDocument(e.target.value)}>
                <option value="">Select a document from the list</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.original_filename || doc.name}
                    {doc.document_type && ` (${doc.document_type})`}
                    {doc.page_count && ` • ${doc.page_count} pages`}
                  </option>
                ))}
              </select>

              {selectedDocumentData && (
                <div className="document-info">
                  <div><span className="label">Document:</span> <span className="value">{selectedDocumentData.original_filename}</span></div>
                  {selectedDocumentData.document_type && (
                    <div><span className="label">Type:</span> <span className="value">{selectedDocumentData.document_type}</span></div>
                  )}
                  {selectedDocumentData.page_count && (
                    <div><span className="label">Pages:</span> <span className="value">{selectedDocumentData.page_count}</span></div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* AI Summary Options */}
          <div className="card">
            <div className="card-header">
              <h2>Summary Options</h2>
            </div>
            <div className="card-body">
              <div className="model-options">
                {summaryOptions.map((option) => (
                  <div
                    key={option.id}
                    className={`model-option ${summaryType === option.id ? "selected" : ""}`}
                    onClick={() => setSummaryType(option.id)}
                  >
                    <div className="model-option-content">
                      <div className="model-option-radio"></div>
                      <div>
                        <div className="model-option-title">{option.name}</div>
                        <p className="model-option-desc">{option.desc}</p>
                        <p className="model-option-model">Model: {option.model}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={handleGenerateSummary}
                disabled={!selectedDocument || isGenerating}
                className="generate-button"
              >
                {isGenerating ? (
                  <>
                    <span className="spinner"></span>
                    AI Processing...
                  </>
                ) : (
                  "Generate Summary"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <div className="results-card">
            <div className="results-header">
              <div>
                <h2>AI Generated Summary</h2>
                {generatedSummary && (
                  <p>Generated using {generatedSummary.model_used} • {generatedSummary.summary_type}</p>
                )}
              </div>
              {generatedSummary && (
                <div className="action-buttons">
                  <button onClick={handleCopy} className="action-button">Copy Text</button>
                  <button onClick={handleExport} className="action-button">Export</button>
                </div>
              )}
            </div>
            <div className="results-content">
              {isGenerating ? (
                <div className="loading-state">
                  <div className="ripple-spinner"></div>
                  <h3 className="processing-text">AI is Processing Your Document</h3>
                  <p>This may take a few minutes. Please wait while our AI analyzes your document and generates a comprehensive summary.</p>
                  <div className="dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              ) : generatedSummary ? (
                <div>
                  <div className="summary-box">
                    {generatedSummary.summary_text.split("\n").map((paragraph, index) => (
                      <p key={index}>{paragraph}</p>
                    ))}
                  </div>
                  <div className="summary-meta">
                    <div><span>Word count: {generatedSummary.word_count || "N/A"}</span></div>
                    <div><span>Model: {generatedSummary.model_used}</span></div>
                    <div><span>Type: {generatedSummary.summary_type}</span></div>
                    <div><span>Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}</span></div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div style={{ fontSize: "3rem" }}>📝</div>
                  <h3>Ready to Generate</h3>
                  <p>Select a document from the dropdown menu on the left and choose a summary type. Click the "Generate Summary" button to create an AI-powered summary of your document.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}