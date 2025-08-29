

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
// import "../styles/globals.css"
import './globals.css' 
import { authService } from "../services/authService"

const routes = {
  "/dashboard": { component: Dashboard, title: "Dashboard", breadcrumb: ["Dashboard"] },
  "/upload": { component: DocumentUpload, title: "Upload Documents", breadcrumb: ["Upload Documents"] },
  "/summarization": { component: Summarization, title: "Summarization", breadcrumb: ["Analysis", "Summarization"] },
  "/search": { component: SearchInterface, title: "Search", breadcrumb: ["Analysis", "Search"] },
  "/chat": { component: RAGChatbot, title: "AI Chat", breadcrumb: ["Analysis", "AI Chat"] },
}

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
          setIsAuthenticated(false);
        }
      } catch (error) {
        // Token is invalid, clear it and redirect to landing
        authService.logout();
        setUser(null);
        setIsAuthenticated(false);
        setCurrentRoute("/dashboard");
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

  // Show landing page only if we're sure user is not authenticated
  if (!isAuthenticated && !isVerifyingAuth) {
    return (
      <>
        <LandingPage onShowAuth={() => setShowAuthModal(true)} />
        {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} onAuthSuccess={handleAuthSuccess} />}
      </>
    )
  }

  const CurrentComponent = routes[currentRoute as keyof typeof routes]?.component || Dashboard
  const breadcrumb = routes[currentRoute as keyof typeof routes]?.breadcrumb || ["Dashboard"]

  const handleNavigation = (path: string) => {
    setCurrentRoute(path)
  }

  return (
    <div className="app-container">
      {/* IMPROVED: Show subtle loading indicator while verifying auth */}
      {isVerifyingAuth && (
        <div className="auth-verifying-overlay">
          <div className="auth-verifying-spinner"></div>
        </div>
      )}

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
            <div className="header-actions">
              <button className="header-btn" title="Search">
                <i className="fas fa-search"></i>
              </button>
              <button className="header-btn" title="Notifications">
                <i className="fas fa-bell"></i>
                <span className="notification-badge">3</span>
              </button>
              <button className="header-btn" title="Settings">
                <i className="fas fa-cog"></i>
              </button>
              <div className="user-profile">
                <div className="user-avatar">
                  <i className="fas fa-user"></i>
                </div>
                <span className="user-name">{user?.username || 'User'}</span>
                <i className="fas fa-chevron-down"></i>
              </div>
            </div>
            <button className="upload-btn" onClick={() => handleNavigation('/upload')}>
              <i className="fas fa-cloud-upload-alt"></i>
              <span>Upload Document</span>
            </button>
          </div>
        </header>

        <div className="content-area">
          {/* Show the user's intended page immediately, with subtle loading if needed */}
          <CurrentComponent />
        </div>
      </div>
    </div>
  )
}

