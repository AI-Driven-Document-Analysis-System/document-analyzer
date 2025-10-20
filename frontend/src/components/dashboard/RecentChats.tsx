


// // //**********************Real */
// "use client"

// import type React from "react"
// import { useState, useEffect } from "react"

// interface Chat {
//   id: string
//   title: string
//   created_at: string
//   message_count: number
// }

// interface Message {
//   id: string
//   content: string
//   role: "user" | "assistant"
//   timestamp: string
// }

// const RecentChats: React.FC = () => {
//   const [chats, setChats] = useState<Chat[]>([])
//   const [loading, setLoading] = useState(true)
//   const [selectedChat, setSelectedChat] = useState<Chat | null>(null)
//   const [messages, setMessages] = useState<Message[]>([])
//   const [messagesLoading, setMessagesLoading] = useState(false)

//   useEffect(() => {
//     fetchRecentChats()
//   }, [])

//   const fetchRecentChats = async () => {
//     try {
//       const token = localStorage.getItem("token")
//       if (!token) {
//         setLoading(false)
//         return
//       }

//       const userResponse = await fetch("http://localhost:8000/api/auth/me", {
//         headers: {
//           Authorization: `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       })

//       if (!userResponse.ok) {
//         setLoading(false)
//         return
//       }

//       const userData = await userResponse.json()
//       const userId = userData.id || userData.user_id

//       const response = await fetch(`http://localhost:8000/api/chat/conversations?user_id=${userId}&limit=3`, {
//         headers: {
//           Authorization: `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       })

//       if (response.ok) {
//         const data = await response.json()
//         console.log("Chats data:", data)
//         setChats(data.conversations || [])
//       }
//     } catch (error) {
//       console.error("Error fetching chats:", error)
//     } finally {
//       setLoading(false)
//     }
//   }

//   const fetchChatMessages = async (chatId: string) => {
//     try {
//       setMessagesLoading(true)
//       const token = localStorage.getItem("token")

//       const response = await fetch(`http://localhost:8000/api/chat/conversations/${chatId}/history`, {
//         headers: {
//           Authorization: `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       })

//       if (response.ok) {
//         const data = await response.json()
//         console.log("[v0] Messages response:", data)
//         setMessages(data.messages || [])
//       } else {
//         console.error("[v0] Failed to fetch messages:", response.status, response.statusText)
//       }
//     } catch (error) {
//       console.error("Error fetching messages:", error)
//     } finally {
//       setMessagesLoading(false)
//     }
//   }

//   const handleViewConversation = (chat: Chat) => {
//     setSelectedChat(chat)
//     fetchChatMessages(chat.id)
//   }

//   const formatDate = (dateString: string) => {
//     const date = new Date(dateString)
//     const now = new Date()
//     const diffMs = now.getTime() - date.getTime()
//     const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

//     if (diffHours < 1) return "Just now"
//     if (diffHours < 24) return `${diffHours}h ago`
//     const diffDays = Math.floor(diffHours / 24)
//     if (diffDays < 7) return `${diffDays}d ago`
//     return date.toLocaleDateString()
//   }

//   if (selectedChat) {
//     return (
//       <div className="feature-container" style={{ flex: "1", display: "flex", flexDirection: "column" }}>
//         {/* Header with back button */}
//         <div
//           style={{
//             display: "flex",
//             alignItems: "center",
//             gap: "1rem",
//             marginBottom: "1.5rem",
//             paddingBottom: "1rem",
//             borderBottom: "1px solid #e2e8f0",
//           }}
//         >
//           <button
//             onClick={() => {
//               setSelectedChat(null)
//               setMessages([])
//             }}
//             style={{
//               padding: "6px 12px",
//               fontSize: "0.875rem",
//               backgroundColor: "#f1f5f9",
//               color: "#334155",
//               border: "none",
//               borderRadius: "6px",
//               cursor: "pointer",
//               transition: "all 0.2s ease",
//             }}
//             onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#e2e8f0")}
//             onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#f1f5f9")}
//           >
//             ← Back
//           </button>
//           <div>
//             <h5 style={{ margin: 0, marginBottom: "0.25rem" }}>{selectedChat.title || "Untitled Chat"}</h5>
//             <p style={{ margin: 0, fontSize: "0.875rem", color: "#94a3b8" }}>
//               {selectedChat.message_count} messages • {formatDate(selectedChat.created_at)}
//             </p>
//           </div>
//         </div>

//         {/* Messages container */}
//         <div
//           style={{
//             flex: 1,
//             overflowY: "auto",
//             marginBottom: "1rem",
//             display: "flex",
//             flexDirection: "column",
//             gap: "1rem",
//           }}
//         >
//           {messagesLoading ? (
//             <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
//               <p>Loading messages...</p>
//             </div>
//           ) : messages.length === 0 ? (
//             <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
//               <p>No messages in this conversation</p>
//             </div>
//           ) : (
//             messages.map((message) => (
//               <div
//                 key={message.id}
//                 style={{
//                   display: "flex",
//                   justifyContent: message.role === "user" ? "flex-end" : "flex-start",
//                   gap: "0.5rem",
//                 }}
//               >
//                 <div
//                   style={{
//                     maxWidth: "70%",
//                     padding: "0.75rem 1rem",
//                     borderRadius: "8px",
//                     backgroundColor: message.role === "user" ? "#3b82f6" : "#f1f5f9",
//                     color: message.role === "user" ? "white" : "#1e293b",
//                     wordWrap: "break-word",
//                   }}
//                 >
//                   <p style={{ margin: 0, marginBottom: "0.25rem" }}>{message.content}</p>
//                   <p style={{ margin: 0, fontSize: "0.75rem", opacity: 0.7 }}>
//                     {new Date(message.timestamp).toLocaleTimeString()}
//                   </p>
//                 </div>
//               </div>
//             ))
//           )}
//         </div>
//       </div>
//     )
//   }

//   return (
//     <div className="feature-container" style={{ flex: "1" }}>
//       <div className="tab-content-container">
//         <h5 className="mb-4">
//           <i className="fas fa-thumbtack me-2"></i>Recent Chats
//         </h5>

//         {loading ? (
//           <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
//             <p>Loading chats...</p>
//           </div>
//         ) : chats.length === 0 ? (
//           <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
//             <i className="fas fa-comments" style={{ fontSize: "2rem", marginBottom: "1rem", opacity: 0.3 }}></i>
//             <p>No recent chats</p>
//           </div>
//         ) : (
//           <div>
//             {chats.slice(0, 3).map((chat) => (
//               <div key={chat.id} className="result-item">
//                 <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
//                   <div className="flex-grow-1">
//                     <div className="result-title" style={{ marginBottom: "0.5rem" }}>
//                       {chat.title || "Untitled Chat"}
//                     </div>
//                     <div className="result-meta">
//                       {chat.message_count} messages • {formatDate(chat.created_at)}
//                     </div>
//                   </div>
//                   <button
//                     onClick={() => handleViewConversation(chat)}
//                     style={{
//                       padding: "6px 12px",
//                       fontSize: "0.75rem",
//                       fontWeight: 500,
//                       backgroundColor: "#3b82f6",
//                       color: "white",
//                       border: "none",
//                       borderRadius: "6px",
//                       cursor: "pointer",
//                       transition: "all 0.2s ease",
//                       whiteSpace: "nowrap",
//                     }}
//                     onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#2563eb")}
//                     onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#3b82f6")}
//                   >
//                     View Conversation
//                   </button>
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}
//       </div>
//     </div>
//   )
// }

// export default RecentChats



//*******************Optimised */

"use client"

import type React from "react"
import { useState, useEffect } from "react"

interface Chat {
  id: string
  title: string
  created_at: string
  message_count: number
}

interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: string
}

const RecentChats: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedChat, setSelectedChat] = useState<Chat | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [messagesLoading, setMessagesLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Chat[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    fetchRecentChats()
  }, [])

  const fetchRecentChats = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        setLoading(false)
        return
      }

      // Fetch user info first
      const userRes = await fetch("http://localhost:8000/api/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (!userRes.ok) {
        setLoading(false)
        return
      }

      const userData = await userRes.json()
      const userId = userData.id || userData.user_id

      // Fetch pinned conversations
      const pinnedRes = await fetch(
        `http://localhost:8000/api/chat/conversations/pinned?user_id=${userId}&limit=3`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      )

      if (pinnedRes.ok) {
        const data = await pinnedRes.json()
        console.log('📌 Pinned chats from API:', data)
        const chatsData = data.conversations || []
        console.log('📌 Total pinned chats:', chatsData.length, chatsData)
        setChats(chatsData)
      } else {
        const errorText = await pinnedRes.text()
        console.error('❌ Failed to fetch pinned chats:', pinnedRes.status, errorText)
        setLoading(false)
        return
      }
    } catch (error) {
      console.error("Error fetching chats:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchChatMessages = async (chatId: string) => {
    try {
      setMessagesLoading(true)
      const token = localStorage.getItem("token")

      const response = await fetch(
        `http://localhost:8000/api/chat/conversations/${chatId}/history`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        const messagesData = data.messages || []
        setMessages(messagesData)
      }
    } catch (error) {
      console.error("Error fetching messages:", error)
    } finally {
      setMessagesLoading(false)
    }
  }

  const handleViewConversation = (chat: Chat) => {
    // Store conversation ID for the chat component to pick up
    sessionStorage.setItem('nav_conversation_id', chat.id)
    // Navigate to chat route
    localStorage.setItem('currentRoute', '/chat')
    // Trigger page reload to navigate
    window.location.reload()
  }

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    
    if (query.trim().length === 0) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    try {
      const token = localStorage.getItem('token')
      
      // Get user ID first
      const userRes = await fetch("http://localhost:8000/api/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (!userRes.ok) {
        setIsSearching(false)
        return
      }

      const userData = await userRes.json()
      const userId = userData.id || userData.user_id

      // Fetch ALL conversations for this user
      const response = await fetch(
        `http://localhost:8000/api/chat/conversations?user_id=${userId}&limit=100`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        const allChats = data.conversations || []
        
        // Filter chats based on search query
        const filtered = allChats.filter((chat: Chat) => 
          chat.title?.toLowerCase().includes(query.toLowerCase())
        )
        
        setSearchResults(filtered)
      }
    } catch (error) {
      console.error('Error searching chats:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

    if (diffHours < 1) return "Just now"
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  if (selectedChat) {
    return (
      <div className="feature-container" style={{ flex: "1", display: "flex", flexDirection: "column" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            marginBottom: "1.5rem",
            paddingBottom: "1rem",
            borderBottom: "1px solid #e2e8f0",
          }}
        >
          <button
            onClick={() => {
              setSelectedChat(null)
              setMessages([])
            }}
            style={{
              padding: "6px 12px",
              fontSize: "0.875rem",
              backgroundColor: "#f1f5f9",
              color: "#334155",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#e2e8f0")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#f1f5f9")}
          >
            ← Back
          </button>
          <div>
            <h5 style={{ margin: 0, marginBottom: "0.25rem" }}>{selectedChat.title || "Untitled Chat"}</h5>
            <p style={{ margin: 0, fontSize: "0.875rem", color: "#94a3b8" }}>
              {selectedChat.message_count} messages • {formatDate(selectedChat.created_at)}
            </p>
          </div>
        </div>

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            marginBottom: "1rem",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
          }}
        >
          {messagesLoading ? (
            <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
              <p>Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
              <p>No messages in this conversation</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                style={{
                  display: "flex",
                  justifyContent: message.role === "user" ? "flex-end" : "flex-start",
                  gap: "0.5rem",
                }}
              >
                <div
                  style={{
                    maxWidth: "70%",
                    padding: "0.75rem 1rem",
                    borderRadius: "8px",
                    backgroundColor: message.role === "user" ? "#3b82f6" : "#f1f5f9",
                    color: message.role === "user" ? "white" : "#1e293b",
                    wordWrap: "break-word",
                  }}
                >
                  <p style={{ margin: 0, marginBottom: "0.25rem" }}>{message.content}</p>
                  <p style={{ margin: 0, fontSize: "0.75rem", opacity: 0.7 }}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    )
  }

  // Use search results if searching, otherwise show pinned chats
  const displayedChats = searchQuery ? searchResults : chats

  return (
    <div className="feature-container" style={{ flex: "1" }}>
      <div className="tab-content-container">
        <div className="search-input-group" style={{ marginBottom: '1.5rem' }}>
          <span className="search-icon"><i className="fas fa-search"></i></span>
          <input
            type="text"
            className="form-control"
            placeholder="Search all your chats..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            style={{
              background: 'var(--bg-primary)',
              border: '2px solid #3b82f6',
              borderRadius: '12px',
              padding: '12px 12px 12px 45px',
              fontSize: '15px',
              color: 'var(--text-primary)',
              width: '100%',
              transition: 'all 0.3s ease',
              boxShadow: searchQuery ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none'
            }}
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('')
                setSearchResults([])
              }}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: '#9ca3af',
                cursor: 'pointer',
                fontSize: '16px',
                padding: '4px 8px'
              }}
            >
              <i className="fas fa-times"></i>
            </button>
          )}
        </div>

        <h5 className="mb-4">
          <i className={`fas ${searchQuery ? 'fa-search' : 'fa-thumbtack'} me-2`}></i>
          {searchQuery ? `Search Results (${displayedChats.length})` : 'Pinned Chats'}
        </h5>

        {loading || isSearching ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid var(--border-color)',
              borderTop: '4px solid #3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px'
            }}></div>
            <p>{isSearching ? 'Searching...' : 'Loading chats...'}</p>
          </div>
        ) : displayedChats.length === 0 ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "#94a3b8" }}>
            <i className="fas fa-search" style={{ fontSize: "2rem", marginBottom: "1rem", opacity: 0.3 }}></i>
            <p>{searchQuery ? `No chats found matching "${searchQuery}"` : 'No pinned chats'}</p>
          </div>
        ) : (
          <div>
            {displayedChats.map((chat) => (
              <div key={chat.id} className="result-item">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
                  <div className="flex-grow-1">
                    <div className="result-title" style={{ marginBottom: "0.5rem" }}>
                      {chat.title || "Untitled Chat"}
                    </div>
                    <div className="result-meta">
                      {chat.message_count} messages • {formatDate(chat.created_at)}
                    </div>
                  </div>
                  <button
                    onClick={() => handleViewConversation(chat)}
                    style={{
                      padding: "6px 12px",
                      fontSize: "0.75rem",
                      fontWeight: 500,
                      backgroundColor: "#3b82f6",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      whiteSpace: "nowrap",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#2563eb")}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#3b82f6")}
                  >
                    View Conversation
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default RecentChats