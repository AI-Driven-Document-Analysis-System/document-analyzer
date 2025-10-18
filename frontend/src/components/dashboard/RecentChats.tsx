// import React, { useState, useEffect } from 'react';

// interface Chat {
//   id: string;
//   title: string;
//   created_at: string;
//   message_count: number;
// }

// const RecentChats: React.FC = () => {
//   const [chats, setChats] = useState<Chat[]>([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     fetchRecentChats();
//   }, []);

//   const fetchRecentChats = async () => {
//     try {
//       const token = localStorage.getItem('token');
//       if (!token) {
//         setLoading(false);
//         return;
//       }

//       // Get user info first
//       const userResponse = await fetch('http://localhost:8000/api/auth/me', {
//         headers: {
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json',
//         },
//       });

//       if (!userResponse.ok) {
//         setLoading(false);
//         return;
//       }

//       const userData = await userResponse.json();
//       const userId = userData.id || userData.user_id;

//       // Fetch conversations with user_id
//       const response = await fetch(`http://localhost:8000/api/chat/conversations?user_id=${userId}&limit=3`, {
//         headers: {
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json',
//         },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         console.log('Chats data:', data);
//         setChats(data.conversations || []);
//       }
//     } catch (error) {
//       console.error('Error fetching chats:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const formatDate = (dateString: string) => {
//     const date = new Date(dateString);
//     const now = new Date();
//     const diffMs = now.getTime() - date.getTime();
//     const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
//     if (diffHours < 1) return 'Just now';
//     if (diffHours < 24) return `${diffHours}h ago`;
//     const diffDays = Math.floor(diffHours / 24);
//     if (diffDays < 7) return `${diffDays}d ago`;
//     return date.toLocaleDateString();
//   };

//   return (
//     <div className="feature-container" style={{ flex: '1' }}>
//       <div className="tab-content-container">
//         <h5 className="mb-4"><i className="fas fa-thumbtack me-2"></i>Pinned Chats</h5>

//         {loading ? (
//           <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
//             <p>Loading chats...</p>
//           </div>
//         ) : chats.length === 0 ? (
//           <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
//             <i className="fas fa-comments" style={{ fontSize: '2rem', marginBottom: '1rem', opacity: 0.3 }}></i>
//             <p>No recent chats</p>
//           </div>
//         ) : (
//           <div>
//             {chats.slice(0, 3).map((chat) => (
//               <div 
//                 key={chat.id} 
//                 className="result-item"
//               >
//                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
//                   <div className="flex-grow-1">
//                     <div className="result-title" style={{ marginBottom: '0.5rem' }}>
//                       {chat.title || 'Untitled Chat'}
//                     </div>
//                     <div className="result-meta">
//                       {chat.message_count} messages • {formatDate(chat.created_at)}
//                     </div>
//                   </div>
//                   <button
//                     onClick={() => window.location.href = `/chat/${chat.id}`}
//                     style={{
//                       padding: '6px 12px',
//                       fontSize: '0.75rem',
//                       fontWeight: 500,
//                       backgroundColor: '#3b82f6',
//                       color: 'white',
//                       border: 'none',
//                       borderRadius: '6px',
//                       cursor: 'pointer',
//                       transition: 'all 0.2s ease',
//                       whiteSpace: 'nowrap'
//                     }}
//                     onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
//                     onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
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
//   );
// };

// export default RecentChats;


import React from 'react';

const RecentChats: React.FC = () => {
  return (
    <div className="feature-container" style={{ flex: '1' }}>
      <div className="tab-content-container" style={{
        backgroundColor: 'var(--bg-primary)',
        borderRadius: '8px',
        boxShadow: 'var(--card-shadow)',
        padding: '24px',
        border: '1px solid var(--border-color)',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '200px'
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '12px', color: 'var(--text-tertiary)' }}>
          <i className="fas fa-comments"></i>
        </div>
        <h5 style={{ 
          fontSize: '1.1rem', 
          fontWeight: '600', 
          color: 'var(--text-primary)', 
          marginBottom: '8px',
          margin: '0 0 8px 0'
        }}>
          No Pinned Chats
        </h5>
        <p style={{ 
          color: 'var(--text-secondary)', 
          fontSize: '0.9rem', 
          margin: 0 
        }}>
          Pin your important chats for quick access here.
        </p>
      </div>
    </div>
  );
};

export default RecentChats;
