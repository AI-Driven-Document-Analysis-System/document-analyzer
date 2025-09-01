"use client"

interface LandingPageProps {
  onShowAuth: () => void
}

export function LandingPage({ onShowAuth }: LandingPageProps) {
  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <div className="nav-logo-icon">📄</div>
            <span className="nav-logo-text">DocAnalyzer</span>
          </div>
          <div className="nav-actions">
            <button className="btn btn-primary" onClick={onShowAuth}>
              Sign In
            </button>
            <button className="btn btn-primary" onClick={onShowAuth}>
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Transform Your Documents with
              <span className="hero-gradient-text"> AI-Powered Analysis</span>
            </h1>
            <p className="hero-description">
              Upload, analyze, and extract insights from your documents using advanced AI models. Get intelligent
              summaries, semantic search, and interactive chat with your content.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary btn-lg" onClick={onShowAuth}>
                🚀 Start Analyzing Documents
              </button>
              <button className="btn btn-outline btn-lg">📹 Watch Demo</button>
            </div>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">10K+</span>
                <span className="stat-label">Documents Processed</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">98%</span>
                <span className="stat-label">Accuracy Rate</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">5min</span>
                <span className="stat-label">Average Processing</span>
              </div>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-card">
              <div className="hero-card-header">
                <div className="hero-card-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="hero-card-title">Document Analysis</span>
              </div>
              <div className="hero-card-content">
                <div className="analysis-item">
                  <span className="analysis-icon">📄</span>
                  <div className="analysis-details">
                    <span className="analysis-name">Financial Report Q4.pdf</span>
                    <div className="analysis-progress">
                      <div className="progress-bar" style={{ width: "85%" }}></div>
                    </div>
                  </div>
                  <span className="analysis-status">✅</span>
                </div>
                <div className="analysis-item">
                  <span className="analysis-icon">📊</span>
                  <div className="analysis-details">
                    <span className="analysis-name">Market Research.pdf</span>
                    <div className="analysis-progress">
                      <div className="progress-bar" style={{ width: "92%" }}></div>
                    </div>
                  </div>
                  <span className="analysis-status">🔄</span>
                </div>
                <div className="analysis-item">
                  <span className="analysis-icon">📋</span>
                  <div className="analysis-details">
                    <span className="analysis-name">Legal Contract.pdf</span>
                    <div className="analysis-progress">
                      <div className="progress-bar" style={{ width: "100%" }}></div>
                    </div>
                  </div>
                  <span className="analysis-status">✅</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <div className="section-header">
            <h2 className="section-title">Powerful AI Features</h2>
            <p className="section-description">
              Everything you need to analyze, understand, and extract value from your documents
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3 className="feature-title">AI Summarization</h3>
              <p className="feature-description">Generate intelligent summaries using Pegasus, BART, and T5 models</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3 className="feature-title">Semantic Search</h3>
              <p className="feature-description">
                Find information using natural language queries and AI-powered search
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💬</div>
              <h3 className="feature-title">RAG Chatbot</h3>
              <p className="feature-description">Chat with your documents and get instant answers to your questions</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏷️</div>
              <h3 className="feature-title">Auto Classification</h3>
              <p className="feature-description">Automatically categorize documents by type and content</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👁️</div>
              <h3 className="feature-title">OCR Processing</h3>
              <p className="feature-description">Extract text from images and scanned documents with high accuracy</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Analytics Dashboard</h3>
              <p className="feature-description">Track processing metrics and document insights over time</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <h2 className="cta-title">Ready to Transform Your Document Workflow?</h2>
          <p className="cta-description">
            Join thousands of users who are already using AI to analyze their documents more efficiently
          </p>
          <button className="btn btn-primary btn-lg" onClick={onShowAuth}>
            🚀 Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <div className="footer-logo-icon">📄</div>
                <span className="footer-logo-text">DocAnalyzer</span>
              </div>
              <p className="footer-description">AI-powered document analysis platform for modern businesses</p>
            </div>
            <div className="footer-links">
              <div className="footer-column">
                <h4 className="footer-column-title">Product</h4>
                <a href="#" className="footer-link">
                  Features
                </a>
                <a href="#" className="footer-link">
                  Pricing
                </a>
                <a href="#" className="footer-link">
                  API
                </a>
              </div>
              <div className="footer-column">
                <h4 className="footer-column-title">Company</h4>
                <a href="#" className="footer-link">
                  About
                </a>
                <a href="#" className="footer-link">
                  Blog
                </a>
                <a href="#" className="footer-link">
                  Careers
                </a>
              </div>
              <div className="footer-column">
                <h4 className="footer-column-title">Support</h4>
                <a href="#" className="footer-link">
                  Help Center
                </a>
                <a href="#" className="footer-link">
                  Contact
                </a>
                <a href="#" className="footer-link">
                  Status
                </a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 DocAnalyzer. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
