"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { googleAuthService } from '../../../services/googleAuthService';

export default function AuthCallback() {
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [error, setError] = useState<string>('');
    const router = useRouter();

    useEffect(() => {
        const handleCallback = async () => {
            try {
                setStatus('loading');
                
                // Handle the OAuth callback
                const userData = await googleAuthService.handleOAuthCallback();
                
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
            <div className="auth-callback-content">
                {status === 'loading' && (
                    <>
                        <div className="auth-callback-spinner"></div>
                        <h2>Completing Google Sign-In...</h2>
                        <p>Please wait while we set up your account.</p>
                    </>
                )}
                
                {status === 'success' && (
                    <>
                        <div className="auth-callback-success">✅</div>
                        <h2>Welcome to DocAnalyzer!</h2>
                        <p>Your Google account has been successfully linked. Redirecting to dashboard...</p>
                    </>
                )}
                
                {status === 'error' && (
                    <>
                        <div className="auth-callback-error">❌</div>
                        <h2>Authentication Failed</h2>
                        <p>{error}</p>
                        <p>Redirecting back to sign-in...</p>
                    </>
                )}
            </div>
        </div>
    );
}
