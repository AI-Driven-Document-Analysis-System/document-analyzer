"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabaseAuthService } from '../../../services/supabaseAuthService';
import './auth-callback.css';

export default function AuthCallback() {
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [error, setError] = useState<string>('');
    const router = useRouter();

    useEffect(() => {
        const handleCallback = async () => {
            try {
                setStatus('loading');
                
                // Handle the OAuth callback
                const userData = await supabaseAuthService.handleOAuthCallback();
                
                setStatus('success');
                
                // Redirect to dashboard after successful authentication
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
                
            } catch (error: any) {
                console.error('OAuth callback error:', error);
                setError(error.message || 'Authentication failed');
                setStatus('error');
                
                // Redirect back to landing page after error
                setTimeout(() => {
                    window.location.href = '/';
                }, 3000);
            }
        };

        handleCallback();
    }, [router]);

    return (
        <div className="auth-callback-container">
            <div className={`auth-callback-content ${status}`}>
                <h1>DocuMind AI</h1>

                {status === 'loading' && (
                    <>
                        <div className="auth-callback-spinner"></div>
                        <div className="auth-status-indicator"></div>
                        <h2>Authenticating</h2>
                        <p>Please wait while we verify your credentials and set up your account.</p>
                        <div className="auth-security-badge">
                            Secured with Google Authentication
                        </div>
                    </>
                )}
                
                {status === 'success' && (
                    <>
                        <div className="auth-status-indicator"></div>
                        <h2>Welcome to DocuMind AI</h2>
                        <p>Your account has been successfully authenticated. Redirecting to your dashboard.</p>
                        <div className="auth-security-badge">
                            Protected by Google OAuth 2.0
                        </div>
                    </>
                )}
                
                {status === 'error' && (
                    <>
                        <div className="auth-status-indicator"></div>
                        <h2>Authentication Failed</h2>
                        <p>Unable to complete authentication: {error}</p>
                        <p>You will be redirected to try again.</p>
                        <div className="auth-security-badge">
                            Your data remains secure
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
