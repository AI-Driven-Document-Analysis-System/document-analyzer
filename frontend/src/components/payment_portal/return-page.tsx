import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, Clock, AlertCircle, ArrowLeft } from 'lucide-react';

export default function ReturnPage({ onNavigate }: { onNavigate?: (path: string) => void }) {
  const [status, setStatus] = useState<string | null>(null);
  const [customerEmail, setCustomerEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (!sessionId) {
      setError('Missing session_id in the URL');
      setLoading(false);
      return;
    }

    fetch(`http://localhost:8000/api/payments/session-status?session_id=${encodeURIComponent(sessionId)}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setStatus(data.status);
        setCustomerEmail(data.customer_email || null);
        window.history.replaceState({}, '', '/');
      })
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  const handleBackToSettings = () => {
    if (onNavigate) {
      onNavigate('/settings');
    } else {
      window.location.href = '/settings';
    }
  };

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '24px',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)'
  };

  const cardStyle: React.CSSProperties = {
    width: '100%',
    maxWidth: '500px',
    padding: '48px',
    textAlign: 'center',
    backgroundColor: 'rgba(30, 41, 59, 0.5)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
  };

  const iconContainerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '24px'
  };

  const buttonStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s'
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={{...cardStyle, border: '1px solid #475569'}}>
          <div style={iconContainerStyle}>
            <div style={{position: 'relative'}}>
              <div style={{
                width: '80px',
                height: '80px',
                border: '4px solid #475569',
                borderTopColor: '#3b82f6',
                borderRadius: '50%',
                animation: 'returnPageSpin 1s linear infinite'
              }}></div>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Clock size={32} color="#60a5fa" />
              </div>
            </div>
          </div>
          <h2 style={{fontSize: '24px', fontWeight: '600', color: '#f1f5f9', marginBottom: '8px'}}>
            Processing Payment
          </h2>
          <p style={{color: '#94a3b8', fontSize: '16px'}}>
            Please wait while we verify your payment status...
          </p>
        </div>
        <style>{`
          @keyframes returnPageSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={{...cardStyle, border: '1px solid rgba(239, 68, 68, 0.3)'}}>
          <div style={iconContainerStyle}>
            <div style={{
              width: '80px',
              height: '80px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <XCircle size={48} color="#ef4444" />
            </div>
          </div>
          <h2 style={{fontSize: '24px', fontWeight: '600', color: '#f1f5f9', marginBottom: '12px'}}>
            Payment Error
          </h2>
          <p style={{color: '#94a3b8', fontSize: '16px', marginBottom: '24px'}}>{error}</p>
          <button
            onClick={handleBackToSettings}
            style={{...buttonStyle, backgroundColor: '#475569', color: '#f1f5f9'}}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#64748b'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#475569'}
          >
            <ArrowLeft size={16} />
            Back to Settings
          </button>
        </div>
      </div>
    );
  }

  if (status === 'open') {
    return (
      <div style={containerStyle}>
        <div style={{...cardStyle, border: '1px solid rgba(245, 158, 11, 0.3)'}}>
          <div style={iconContainerStyle}>
            <div style={{
              width: '80px',
              height: '80px',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <AlertCircle size={48} color="#f59e0b" />
            </div>
          </div>
          <h2 style={{fontSize: '24px', fontWeight: '600', color: '#f1f5f9', marginBottom: '12px'}}>
            Checkout In Progress
          </h2>
          <p style={{color: '#94a3b8', fontSize: '16px', marginBottom: '24px'}}>
            Your checkout session is still open. Please complete the payment in the checkout window.
          </p>
          <button
            onClick={handleBackToSettings}
            style={{...buttonStyle, backgroundColor: '#475569', color: '#f1f5f9'}}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#64748b'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#475569'}
          >
            <ArrowLeft size={16} />
            Cancel & Return to Settings
          </button>
        </div>
      </div>
    );
  }

  if (status === 'complete') {
    return (
      <div style={containerStyle}>
        <div style={{...cardStyle, border: '1px solid rgba(34, 197, 94, 0.3)'}}>
          <div style={iconContainerStyle}>
            <div style={{position: 'relative'}}>
              <div style={{
                width: '80px',
                height: '80px',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                animation: 'returnPagePulse 2s ease-in-out infinite'
              }}>
                <CheckCircle size={48} color="#22c55e" />
              </div>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '80px',
                height: '80px',
                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                borderRadius: '50%',
                animation: 'returnPagePing 2s ease-in-out infinite'
              }}></div>
            </div>
          </div>
          <h2 style={{fontSize: '28px', fontWeight: '700', color: '#f1f5f9', marginBottom: '12px'}}>
            Payment Successful!
          </h2>
          <p style={{color: '#cbd5e1', fontSize: '16px', marginBottom: '8px'}}>
            Thank you for your purchase.
          </p>
          {customerEmail && (
            <p style={{color: '#94a3b8', fontSize: '14px', marginBottom: '24px'}}>
              A confirmation email has been sent to <span style={{color: '#60a5fa', fontWeight: '500'}}>{customerEmail}</span>
            </p>
          )}
          <div style={{
            padding: '16px',
            backgroundColor: 'rgba(51, 65, 85, 0.3)',
            border: '1px solid #475569',
            borderRadius: '8px',
            marginBottom: '24px'
          }}>
            <p style={{color: '#cbd5e1', fontSize: '14px'}}>
              Your subscription is now active. You can start using all premium features immediately.
            </p>
          </div>
          <button
            onClick={handleBackToSettings}
            style={{
              ...buttonStyle, 
              width: '100%', 
              justifyContent: 'center',
              backgroundColor: '#2563eb', 
              color: '#ffffff',
              boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.2)'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1d4ed8'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
          >
            <ArrowLeft size={16} />
            Return to Settings
          </button>
        </div>
        <style>{`
          @keyframes returnPagePulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
          @keyframes returnPagePing {
            0% { transform: scale(1); opacity: 0.7; }
            50% { transform: scale(1.1); opacity: 0.3; }
            100% { transform: scale(1.2); opacity: 0; }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={{...cardStyle, border: '1px solid #475569'}}>
        <div style={iconContainerStyle}>
          <div style={{
            width: '80px',
            height: '80px',
            backgroundColor: '#475569',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <AlertCircle size={48} color="#94a3b8" />
          </div>
        </div>
        <h2 style={{fontSize: '24px', fontWeight: '600', color: '#f1f5f9', marginBottom: '12px'}}>
          Payment Status: {status || 'Unknown'}
        </h2>
        <p style={{color: '#94a3b8', fontSize: '16px', marginBottom: '24px'}}>
          If you believe this is an error, please contact our support team.
        </p>
        <button
          onClick={handleBackToSettings}
          style={{...buttonStyle, backgroundColor: '#475569', color: '#f1f5f9'}}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#64748b'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#475569'}
        >
          <ArrowLeft size={16} />
          Back to Settings
        </button>
      </div>
    </div>
  );
}