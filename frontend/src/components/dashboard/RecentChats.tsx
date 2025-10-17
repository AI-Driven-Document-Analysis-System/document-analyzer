import React, { useState, useEffect } from 'react';

interface Chat {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

const RecentChats: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentChats();
  }, []);

  const fetchRecentChats = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Get user info first
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!userResponse.ok) {
        setLoading(false);
        return;
      }

      const userData = await userResponse.json();
      const userId = userData.id || userData.user_id;

      // Fetch conversations with user_id
      const response = await fetch(`http://localhost:8000/api/chat/conversations?user_id=${userId}&limit=5`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Chats data:', data);
        setChats(data.conversations || []);
      }
    } catch (error) {
      console.error('Error fetching chats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="feature-container" style={{ flex: '1' }}>
      <div className="tab-content-container">
        <h5 className="mb-4"><i className="fas fa-comments me-2"></i>Recent Chats</h5>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
            <p>Loading chats...</p>
          </div>
        ) : chats.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
            <i className="fas fa-comments" style={{ fontSize: '2rem', marginBottom: '1rem', opacity: 0.3 }}></i>
            <p>No recent chats</p>
          </div>
        ) : (
          <div>
            {chats.slice(0, 5).map((chat) => (
              <div 
                key={chat.id} 
                className="result-item"
                style={{ cursor: 'pointer' }}
                onClick={() => window.location.href = `/chat/${chat.id}`}
              >
                <div className="flex-grow-1">
                  <div className="result-title" style={{ marginBottom: '0.5rem' }}>
                    {chat.title || 'Untitled Chat'}
                  </div>
                  <div className="result-meta">
                    {chat.message_count} messages • {formatDate(chat.created_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentChats;
