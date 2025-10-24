"use client"

import { useState, useEffect } from "react"
import { LandingPage } from "../components/landing/landing-page"
import { AuthModal } from "../components/auth/auth-modal"
import Dashboard from "../components/dashboard/dashboard"
import { DocumentUpload } from "../components/upload/document-upload"
import Summarization from "../components/summarization/summarization";
import { SearchInterface } from "../components/search/search-interface"
import { RAGChatbot } from "../components/chat/rag-chatbot"
import { Sidebar } from "../components/layout/sidebar"
import Analytics from "../components/analytics/analytics"
import { DocumentView } from '../components/view/document_view'
// import "../styles/globals.css"
import './globals.css' 
import { authService } from "../services/authService"
import UserProfilePage  from "../profile/profile"
import Settings from "../components/settings/settings"
import { Subscription } from "../components/subscription/subscription"
import { ThemeProvider } from "../contexts/ThemeContext" 
import ReturnPage from "../components/payment_portal/return-page"

const routes = {
  "/dashboard": { component: Dashboard, title: "Dashboard", breadcrumb: ["Dashboard"] },
  "/upload": { component: DocumentUpload, title: "Upload Documents", breadcrumb: ["Upload Documents"] },
  "/summarization": { component: Summarization, title: "Summarization", breadcrumb: ["Analysis", "Summarization"] },
  "/search": { component: SearchInterface, title: "Search", breadcrumb: ["Analysis", "Search"] },
  "/chat": { component: RAGChatbot, title: "AI Agent", breadcrumb: ["Analysis", "AI Agent"] },
  "/analytics": { component: Analytics, title: "Analytics", breadcrumb: ["Insights", "Analytics"] },
  "/documents": { component: DocumentView, title: "My Documents", breadcrumb: ["Documents"] },
  "/profile": { component: UserProfilePage, title: "Profile",  breadcrumb: ["Account", "Profile"] },
  "/subscription": { component: Subscription, title: "Subscription", breadcrumb: ["Account", "Subscription"] },
  "/settings": { component: Settings, title: "Settings", breadcrumb: ["Account", "Settings"] },
  "/return": { component: ReturnPage, title: "Payment Return", breadcrumb: ["Payments", "Return"] },
}

/**
 * Main page component that handles authentication, routing, and layout
 * Implements proper SSR hydration handling and localStorage state persistence
 */
export default function Page() {
  // FIXED: Initialize all state with safe defaults for SSR
  // Don't access localStorage during initial render to avoid hydration mismatch
  const [isAuthenticated, setIsAuthenticated] = useState(false) // Always start false for SSR
  const [isVerifyingAuth, setIsVerifyingAuth] = useState(true) // Always start verifying
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [currentRoute, setCurrentRoute] = useState("/dashboard") // Safe default
  const [sidebarOpen, setSidebarOpen] = useState(true) // Safe default
  const [user, setUser] = useState<{username?: string} | null>(null)
  const [isClientReady, setIsClientReady] = useState(false) // Track when client is ready


  // FIXED: Handle client-side hydration and state restoration
  useEffect(() => {
    // Mark client as ready and restore state from localStorage
    setIsClientReady(true);
    
    // Restore persisted state after hydration
    const savedRoute = localStorage.getItem('currentRoute');
    if (savedRoute && routes[savedRoute as keyof typeof routes]) {
      setCurrentRoute(savedRoute);
    }
    
    const savedSidebar = localStorage.getItem('sidebarOpen');
    if (savedSidebar) {
      setSidebarOpen(JSON.parse(savedSidebar));
    }
  }, []);

  useEffect(() => {
  if (!isClientReady) return;
  
  // Check if we're coming back from Stripe
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get('session_id');
  
  if (sessionId && window.location.pathname === '/') {
    // User returned from Stripe, navigate to return page
    setCurrentRoute('/return');
  }
}, [isClientReady]);

  // Verify authentication in background
  useEffect(() => {
    if (!isClientReady) return; // Wait for client hydration
    
    const verifyAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // No token - show login modal
          setIsAuthenticated(false);
          setShowAuthModal(true);
        }
      } catch (error) {
        // Token is invalid, clear it and show login
        authService.logout();
        setUser(null);
        setIsAuthenticated(false);
        setShowAuthModal(true);
      } finally {
        setIsVerifyingAuth(false); // Done verifying
      }
    };
    
    verifyAuth();
  }, [isClientReady]);

  // Persist user's current route (only on client)
  useEffect(() => {
    if (isClientReady && isAuthenticated && currentRoute) {
      localStorage.setItem('currentRoute', currentRoute);
    }
  }, [currentRoute, isAuthenticated, isClientReady]);

  // Persist sidebar state (only on client)
  useEffect(() => {
    if (isClientReady) {
      localStorage.setItem('sidebarOpen', JSON.stringify(sidebarOpen));
    }
  }, [sidebarOpen, isClientReady]);

  const handleAuthSuccess = (userData: any) => {
    setUser(userData)
    setIsAuthenticated(true)
    setShowAuthModal(false)
  }

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setCurrentRoute("/dashboard");
    localStorage.removeItem('currentRoute');
  };

  // FIXED: Don't render auth-dependent content until client is ready
  // This prevents hydration mismatches
  if (!isClientReady) {
    return (
      <div className="app-container">
        <div className="main-content">
          <div className="content-area">
            <div className="initial-loading">
              <div className="loading-spinner"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show landing page if not authenticated
  if (!isAuthenticated && !isVerifyingAuth) {
    return (
      <ThemeProvider>
        <LandingPage onShowAuth={() => setShowAuthModal(true)} />
        {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} onAuthSuccess={handleAuthSuccess} />}
      </ThemeProvider>
    )
  }

  const CurrentComponent = routes[currentRoute as keyof typeof routes]?.component || Dashboard
  const breadcrumb = routes[currentRoute as keyof typeof routes]?.breadcrumb || ["Dashboard"]

  const handleNavigation = (path: string, params?: Record<string, string>) => {
    setCurrentRoute(path)
    // Store navigation params for the target component
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        sessionStorage.setItem(`nav_${key}`, value)
      })
    }
  }

  // Show loading overlay before everything else
  if (isVerifyingAuth) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: '#0f172a',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          border: '6px solid #1e293b',
          borderTop: '6px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '24px'
        }}></div>
        <p style={{
          color: '#f1f5f9',
          fontSize: '18px',
          fontWeight: '500',
          marginBottom: '8px',
          textAlign: 'center'
        }}>Loading your workspace...</p>
        <p style={{
          color: '#94a3b8',
          fontSize: '14px',
          textAlign: 'center'
        }}>Please wait</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <div className="app-container" style={{ backgroundColor: '#0f172a', minHeight: '100vh' }}>

      <Sidebar
        isOpen={sidebarOpen}
        onNavigate={handleNavigation}
        currentRoute={currentRoute}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        user={user}
        onLogout={handleLogout}
      />

      <div className={`main-content ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
        <header className="app-header">
          <div className="header-left">
            <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <i className="fas fa-bars"></i>
            </button>
            <div className="breadcrumb">
              {breadcrumb.map((item, index) => (
                <span key={item}>
                  {index > 0 && <span className="breadcrumb-separator"> / </span>}
                  <span className={index === breadcrumb.length - 1 ? "breadcrumb-current" : "breadcrumb-link"}>
                    {item}
                  </span>
                </span>
              ))}
            </div>
          </div>
          <div className="header-right">
            {/* <button className="header-btn" title="Search">
              <i className="fas fa-search"></i>
            </button> */}
            <button className="upload-btn" onClick={() => handleNavigation('/upload')}>
              <i className="fas fa-cloud-upload-alt"></i>
              <span>Upload Document</span>
            </button>
            <div className="header-actions">
              {/* <button className="header-btn" title="Notifications">
                <i className="fas fa-bell"></i>
                <span className="notification-badge">3</span>
              </button> */}
              <button 
                  className="header-btn" 
                  title="Settings"
                  onClick={() => handleNavigation('/settings')}
                >
                  <i className="fas fa-cog"></i>
              </button>

              <div className="user-profile" onClick={() => handleNavigation('/profile')}>
                <div className="user-avatar">
                  <i className="fas fa-user"></i>
                </div>
                <span className="user-name">{user?.username || 'User'}</span>
                <i className="fas fa-chevron-down"></i>
              </div>

              {/* <button className="header-btn" title="Settings">
                <i className="fas fa-cog"></i>
              </button> */}
              {/* <div className="user-profile">
                <div className="user-avatar">
                  <i className="fas fa-user"></i>
                </div>
                <span className="user-name">{user?.username || 'User'}</span>
                <i className="fas fa-chevron-down"></i>
              </div> */}

              
              
            </div>
          </div>
        </header>

        <div className="content-area">
          {/* Show the user's intended page immediately, with subtle loading if needed */}
          {currentRoute === '/return' ? (
            <ReturnPage onNavigate={handleNavigation} />
          ) : (
            <CurrentComponent />
          )}
        </div>
      </div>
    </div>
    </ThemeProvider>
  )
}