
// "use client"

// import { useState, useEffect } from "react"
// import { LandingPage } from "../components/landing/landing-page"
// // If the file exists elsewhere, update the path accordingly, e.g.:
// // import { LandingPage } from "../components/LandingPage"
// // Otherwise, create 'landing-page.tsx' in 'frontend/src/components/landing/'.
// import { AuthModal } from "../components/auth/auth-modal"
// import { Dashboard } from "../components/dashboard/dashboard"
// import { DocumentUpload } from "../components/upload/document-upload"
// import Summarization from "../components/summarization/summarization";
// import { SearchInterface } from "../components/search/search-interface"
// import { RAGChatbot } from "../components/chat/rag-chatbot"
// import { Sidebar } from "../components/layout/sidebar"
// import "../styles/globals.css"
// import { authService } from "../services/authService"

// const routes = {
//   "/dashboard": { component: Dashboard, title: "Dashboard", breadcrumb: ["Dashboard"] },
//   "/upload": { component: DocumentUpload, title: "Upload Documents", breadcrumb: ["Upload Documents"] },
//   "/summarization": { component: Summarization, title: "Summarization", breadcrumb: ["Analysis", "Summarization"] },
//   "/search": { component: SearchInterface, title: "Search", breadcrumb: ["Analysis", "Search"] },
//   "/chat": { component: RAGChatbot, title: "AI Chat", breadcrumb: ["Analysis", "AI Chat"] },
// }

// export default function Page() {
//   const [isAuthenticated, setIsAuthenticated] = useState(false)
//   const [showAuthModal, setShowAuthModal] = useState(false)
//   const [currentRoute, setCurrentRoute] = useState("/dashboard")
//   const [sidebarOpen, setSidebarOpen] = useState(true)
//   const [user, setUser] = useState(null)

//   const handleAuthSuccess = (userData: any) => {
//     setUser(userData)
//     setIsAuthenticated(true)
//     setShowAuthModal(false)
//   }

  

//   const handleLogout = async () => {
//   await authService.logout();
//   setUser(null);
//   setIsAuthenticated(false);
//   setCurrentRoute("/dashboard");
// };



//   if (!isAuthenticated) {
//     return (
//       <>
//         <LandingPage onShowAuth={() => setShowAuthModal(true)} />
//         {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} onAuthSuccess={handleAuthSuccess} />}
//       </>
//     )
//   }

//  // Add this to the top of your Page component, after the imports

// // Add this useEffect in your Page component
// useEffect(() => {
//   // Check if user is already authenticated
//   const checkAuth = async () => {
//     if (authService.isAuthenticated()) {
//       try {
//         const userData = await authService.getCurrentUser();
//         setUser(userData);
//         setIsAuthenticated(true);
//       } catch (error) {
//         // Token is invalid, clear it
//         authService.logout();
//         setIsAuthenticated(false);
//       }
//     }
//   };
  
//   checkAuth();
// }, []);

//   const CurrentComponent = routes[currentRoute as keyof typeof routes]?.component || Dashboard
//   const breadcrumb = routes[currentRoute as keyof typeof routes]?.breadcrumb || ["Dashboard"]

//   const handleNavigation = (path: string) => {
//     setCurrentRoute(path)
//   }

//   return (
//     <div className="app-container">
//       <Sidebar
//         isOpen={sidebarOpen}
//         onNavigate={handleNavigation}
//         currentRoute={currentRoute}
//         onToggle={() => setSidebarOpen(!sidebarOpen)}
//         user={user}
//         onLogout={handleLogout}
//       />

//       <div className={`main-content ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
//         <header className="app-header">
//           <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
//             ☰
//           </button>
//           <div className="breadcrumb">
//             {breadcrumb.map((item, index) => (
//               <span key={item}>
//                 {index > 0 && <span className="breadcrumb-separator"> / </span>}
//                 <span className={index === breadcrumb.length - 1 ? "breadcrumb-current" : "breadcrumb-link"}>
//                   {item}
//                 </span>
//               </span>
//             ))}
//           </div>
//         </header>

//         <div className="content-area">
//           <CurrentComponent />
//         </div>
//       </div>
//     </div>
//   )
// }



"use client"

import { useState, useEffect } from "react"
import { LandingPage } from "../components/landing/landing-page"
// If the file exists elsewhere, update the path accordingly, e.g.:
// import { LandingPage } from "../components/LandingPage"
// Otherwise, create 'landing-page.tsx' in 'frontend/src/components/landing/'.
import { AuthModal } from "../components/auth/auth-modal"
import { Dashboard } from "../components/dashboard/dashboard"
import { DocumentUpload } from "../components/upload/document-upload"
import Summarization from "../components/summarization/summarization";
import { SearchInterface } from "../components/search/search-interface"
import { RAGChatbot } from "../components/chat/rag-chatbot"
import { Sidebar } from "../components/layout/sidebar"
import "../styles/globals.css"
import { authService } from "../services/authService"

const routes = {
  "/dashboard": { component: Dashboard, title: "Dashboard", breadcrumb: ["Dashboard"] },
  "/upload": { component: DocumentUpload, title: "Upload Documents", breadcrumb: ["Upload Documents"] },
  "/summarization": { component: Summarization, title: "Summarization", breadcrumb: ["Analysis", "Summarization"] },
  "/search": { component: SearchInterface, title: "Search", breadcrumb: ["Analysis", "Search"] },
  "/chat": { component: RAGChatbot, title: "AI Chat", breadcrumb: ["Analysis", "AI Chat"] },
}

export default function Page() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [currentRoute, setCurrentRoute] = useState("/dashboard")
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [user, setUser] = useState(null)

  // Move useEffect to the top, before any conditional returns
  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          // Token is invalid, clear it
          authService.logout();
          setIsAuthenticated(false);
        }
      }
    };
    
    checkAuth();
  }, []);

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
  };

  // Now the conditional return comes after all hooks
  if (!isAuthenticated) {
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
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            ☰
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
        </header>

        <div className="content-area">
          <CurrentComponent />
        </div>
      </div>
    </div>
  )
}
