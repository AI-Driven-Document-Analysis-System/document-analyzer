// "use client"

// interface LandingPageProps {
//   onShowAuth: () => void
// }

// export function LandingPage({ onShowAuth }: LandingPageProps) {
//   return (
//     <div className="landing-page">
//       {/* Navigation */}
//       <nav className="landing-nav" style={{ background: 'rgba(15, 23, 42, 0.95)', backdropFilter: 'blur(10px)' }}>
//         <div className="nav-container">
//           <div className="nav-logo">
//             <div className="nav-logo-icon">📄</div>
//             <span className="nav-logo-text">DocAnalyzer</span>
//           </div>
//           <div className="nav-actions">
//             <button className="btn btn-outline" onClick={onShowAuth} style={{width: '120px' , backgroundColor: '#007bff', color: 'white', borderColor: '#007bff'}}>
//               Sign In
//             </button>
//             <button className="btn btn-primary" onClick={onShowAuth} style={{width: '120px'}}>
//               Get Started
//             </button>
//           </div>
//         </div>
//       </nav>

//       {/* Hero Section */}
//       <section className="hero-section" style={{ background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)' }}>
//         <div className="hero-container">
//           <div className="hero-content">
//             <h1 className="hero-title">
//               Transform Your Documents with
//               <span className="hero-gradient-text"> AI-Powered Analysis</span>
//             </h1>
//             <p className="hero-description" style={{ color: '#e2e8f0' }}>
//               Upload, analyze, and extract insights from your documents using advanced AI models. Get intelligent
//               summaries, semantic search, and interactive chat with your content.
//             </p>
//             <div className="hero-actions">
//               <button className="btn btn-primary btn-lg" onClick={onShowAuth}>
//                 🚀 Start Analyzing Documents
//               </button>
//               {/* <button className="btn btn-outline btn-lg">📹 Watch Demo</button> */}
//             </div>
//             <div className="hero-stats">
//               <div className="stat-item">
//                 <span className="stat-number">10K+</span>
//                 <span className="stat-label">Documents Processed</span>
//               </div>
//               <div className="stat-item">
//                 <span className="stat-number">98%</span>
//                 <span className="stat-label">Accuracy Rate</span>
//               </div>
//               <div className="stat-item">
//                 <span className="stat-number">5min</span>
//                 <span className="stat-label">Average Processing</span>
//               </div>
//             </div>
//           </div>
//           <div className="hero-visual">
//             <div className="hero-card">
//               <div className="hero-card-header">
//                 <div className="hero-card-dots">
//                   <span></span>
//                   <span></span>
//                   <span></span>
//                 </div>
//                 <span className="hero-card-title">Document Analysis</span>
//               </div>
//               <div className="hero-card-content">
//                 <div className="analysis-item">
//                   <span className="analysis-icon">📄</span>
//                   <div className="analysis-details">
//                     <span className="analysis-name">Financial Report Q4.pdf</span>
//                     <div className="analysis-progress">
//                       <div className="progress-bar" style={{ width: "85%" }}></div>
//                     </div>
//                   </div>
//                   <span className="analysis-status">✅</span>
//                 </div>
//                 <div className="analysis-item">
//                   <span className="analysis-icon">📊</span>
//                   <div className="analysis-details">
//                     <span className="analysis-name">Market Research.pdf</span>
//                     <div className="analysis-progress">
//                       <div className="progress-bar" style={{ width: "92%" }}></div>
//                     </div>
//                   </div>
//                   <span className="analysis-status">🔄</span>
//                 </div>
//                 <div className="analysis-item">
//                   <span className="analysis-icon">📋</span>
//                   <div className="analysis-details">
//                     <span className="analysis-name">Legal Contract.pdf</span>
//                     <div className="analysis-progress">
//                       <div className="progress-bar" style={{ width: "100%" }}></div>
//                     </div>
//                   </div>
//                   <span className="analysis-status">✅</span>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* Features Section */}
//       <section className="features-section" style={{ background: '#0f172a' }}>
//         <div className="features-container">
//           <div className="section-header">
//             <h2 className="section-title">Powerful AI Features</h2>
//             <p className="section-description" style={{ color: '#cbd5e1' }}>
//               Everything you need to analyze, understand, and extract value from your documents
//             </p>
//           </div>
//           <div className="features-grid">
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">🧠</div>
//               <h3 className="feature-title">AI Summarization</h3>
//               <p className="feature-description">Generate intelligent summaries using Pegasus, BART, and T5 models</p>
//             </div>
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">🔍</div>
//               <h3 className="feature-title">Semantic Search</h3>
//               <p className="feature-description">
//                 Find information using natural language queries and AI-powered search
//               </p>
//             </div>
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">💬</div>
//               <h3 className="feature-title">RAG Chatbot</h3>
//               <p className="feature-description">Chat with your documents and get instant answers to your questions</p>
//             </div>
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">🏷️</div>
//               <h3 className="feature-title">Auto Classification</h3>
//               <p className="feature-description">Automatically categorize documents by type and content</p>
//             </div>
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">👁️</div>
//               <h3 className="feature-title">OCR Processing</h3>
//               <p className="feature-description">Extract text from images and scanned documents with high accuracy</p>
//             </div>
//             <div className="feature-card" style={{ color: '#f1f5f9' }}>
//               <div className="feature-icon">📊</div>
//               <h3 className="feature-title">Analytics Dashboard</h3>
//               <p className="feature-description">Track processing metrics and document insights over time</p>
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* CTA Section */}
//       <section className="cta-section" style={{ background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)' }}>
//         <div className="cta-container">
//           <h2 className="cta-title">Ready to Transform Your Document Workflow?</h2>
//           <p className="cta-description" style={{ color: '#e2e8f0' }}>
//             Join thousands of users who are already using AI to analyze their documents more efficiently
//           </p>
//           <button className="btn btn-primary btn-lg" onClick={onShowAuth}>
//             🚀 Get Started Free
//           </button>
//         </div>
//       </section>

//       {/* Footer */}
//       <footer className="landing-footer" style={{ background: '#0c0e27' }}>
//         <div className="footer-container">
//           <div className="footer-content">
//             <div className="footer-brand">
//               <div className="footer-logo">
//                 <div className="footer-logo-icon">📄</div>
//                 <span className="footer-logo-text">DocAnalyzer</span>
//               </div>
//               <p className="footer-description">AI-powered document analysis platform for modern businesses</p>
//             </div>
//             <div className="footer-links">
//               <div className="footer-column">
//                 <h4 className="footer-column-title">Product</h4>
//                 <a href="#" className="footer-link">
//                   Features
//                 </a>
//                 <a href="#" className="footer-link">
//                   Pricing
//                 </a>
//                 <a href="#" className="footer-link">
//                   API
//                 </a>
//               </div>
//               <div className="footer-column">
//                 <h4 className="footer-column-title">Company</h4>
//                 <a href="#" className="footer-link">
//                   About
//                 </a>
//                 <a href="#" className="footer-link">
//                   Blog
//                 </a>
//                 <a href="#" className="footer-link">
//                   Careers
//                 </a>
//               </div>
//               <div className="footer-column">
//                 <h4 className="footer-column-title">Support</h4>
//                 <a href="#" className="footer-link">
//                   Help Center
//                 </a>
//                 <a href="#" className="footer-link">
//                   Contact
//                 </a>
//                 <a href="#" className="footer-link">
//                   Status
//                 </a>
//               </div>
//             </div>
//           </div>
//           <div className="footer-bottom">
//             <p>&copy; 2024 DocAnalyzer. All rights reserved.</p>
//           </div>
//         </div>
//       </footer>
//     </div>
//   )
// }


"use client"

interface LandingPageProps {
  onShowAuth: () => void
}

export function LandingPage({ onShowAuth }: LandingPageProps) {
  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav" style={{ 
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(59, 130, 246, 0.2)'
      }}>
        <div className="nav-container">
          <div className="nav-logo">
            <div className="nav-logo-icon">📄</div>
            <span className="nav-logo-text">DocAnalyzer</span>
          </div>
          <div className="nav-actions">
            <button className="btn btn-outline" onClick={onShowAuth} style={{
              width: '120px',
              backgroundColor: '#3b82f6',
              color: 'white',
              borderColor: '#3b82f6',
              fontWeight: '600'
            }}>
              Sign In
            </button>
            <button className="btn btn-primary" onClick={onShowAuth} style={{
              width: '120px',
              fontWeight: '600'
            }}>
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section" style={{ 
        background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.95) 0%, rgba(30, 64, 175, 0.95) 100%)',
        backdropFilter: 'blur(8px)',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        <div className="hero-container" style={{ position: 'relative', zIndex: 1 }}>
          <div className="hero-content">
            <h1 className="hero-title" style={{ color: '#f1f5f9' }}>
              Transform Your Documents with
              <span className="hero-gradient-text"> AI-Powered Analysis</span>
            </h1>
            <p className="hero-description" style={{ 
              color: '#e2e8f0',
              fontSize: '1.125rem',
              lineHeight: '1.7',
              fontWeight: '400'
            }}>
              Upload, analyze, and extract insights from your documents using advanced AI models. Get intelligent
              summaries, semantic search, and interactive chat with your content.
            </p>
            <div className="hero-actions">
              <button className="btn btn-primary btn-lg" onClick={onShowAuth} style={{
                fontWeight: '600',
                boxShadow: '0 8px 20px rgba(59, 130, 246, 0.4)'
              }}>
                🚀 Start Analyzing Documents
              </button>
            </div>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number" style={{ color: '#fbbf24' }}>10K+</span>
                <span className="stat-label" style={{ color: '#cbd5e1' }}>Documents Processed</span>
              </div>
              <div className="stat-item">
                <span className="stat-number" style={{ color: '#fbbf24' }}>98%</span>
                <span className="stat-label" style={{ color: '#cbd5e1' }}>Accuracy Rate</span>
              </div>
              <div className="stat-item">
                <span className="stat-number" style={{ color: '#fbbf24' }}>5min</span>
                <span className="stat-label" style={{ color: '#cbd5e1' }}>Average Processing</span>
              </div>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-card" style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
            }}>
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
      <section className="features-section" style={{ 
        background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
        backdropFilter: 'blur(8px)',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 40%)',
          pointerEvents: 'none'
        }}></div>
        <div className="features-container" style={{ position: 'relative', zIndex: 1 }}>
          <div className="section-header">
            <h2 className="section-title" style={{ color: '#f1f5f9' }}>Powerful AI Features</h2>
            <p className="section-description" style={{ 
              color: '#cbd5e1',
              fontSize: '1.0625rem'
            }}>
              Everything you need to analyze, understand, and extract value from your documents
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">🧠</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>AI Summarization</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>Generate intelligent summaries using Pegasus, BART, and T5 models</p>
            </div>
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">🔍</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>Semantic Search</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>
                Find information using natural language queries and AI-powered search
              </p>
            </div>
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">💬</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>RAG Chatbot</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>Chat with your documents and get instant answers to your questions</p>
            </div>
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">🏷️</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>Auto Classification</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>Automatically categorize documents by type and content</p>
            </div>
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">👁️</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>OCR Processing</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>Extract text from images and scanned documents with high accuracy</p>
            </div>
            <div className="feature-card" style={{ 
              color: '#f1f5f9',
              background: 'rgba(30, 58, 138, 0.4)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              transition: 'all 0.3s ease'
            }}>
              <div className="feature-icon">📊</div>
              <h3 className="feature-title" style={{ color: '#e2e8f0' }}>Analytics Dashboard</h3>
              <p className="feature-description" style={{ color: '#cbd5e1' }}>Track processing metrics and document insights over time</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section" style={{ 
        background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.95) 0%, rgba(30, 64, 175, 0.95) 100%)',
        backdropFilter: 'blur(8px)',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        <div className="cta-container" style={{ position: 'relative', zIndex: 1 }}>
          <h2 className="cta-title" style={{ color: '#f1f5f9' }}>Ready to Transform Your Document Workflow?</h2>
          <p className="cta-description" style={{ 
            color: '#e2e8f0',
            fontSize: '1.0625rem'
          }}>
            Join thousands of users who are already using AI to analyze their documents more efficiently
          </p>
          <button className="btn btn-primary btn-lg" onClick={onShowAuth} style={{
            fontWeight: '600',
            boxShadow: '0 8px 20px rgba(59, 130, 246, 0.4)'
          }}>
            🚀 Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer" style={{ 
        background: 'linear-gradient(180deg, rgba(12, 14, 39, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)',
        backdropFilter: 'blur(8px)',
        borderTop: '1px solid rgba(59, 130, 246, 0.1)'
      }}>
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <div className="footer-logo-icon">📄</div>
                <span className="footer-logo-text">DocAnalyzer</span>
              </div>
              <p className="footer-description" style={{ color: '#cbd5e1' }}>AI-powered document analysis platform for modern businesses</p>
            </div>
            <div className="footer-links">
              <div className="footer-column">
                <h4 className="footer-column-title" style={{ color: '#f1f5f9' }}>Product</h4>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Features
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Pricing
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  API
                </a>
              </div>
              <div className="footer-column">
                <h4 className="footer-column-title" style={{ color: '#f1f5f9' }}>Company</h4>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  About
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Blog
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Careers
                </a>
              </div>
              <div className="footer-column">
                <h4 className="footer-column-title" style={{ color: '#f1f5f9' }}>Support</h4>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Help Center
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Contact
                </a>
                <a href="#" className="footer-link" style={{ color: '#cbd5e1' }}>
                  Status
                </a>
              </div>
            </div>
          </div>
          <div className="footer-bottom" style={{ borderTopColor: 'rgba(59, 130, 246, 0.1)' }}>
            <p style={{ color: '#9ca3af' }}>&copy; 2024 DocAnalyzer. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}