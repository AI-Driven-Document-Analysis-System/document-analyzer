"use client";

import { useEffect } from 'react';

export default function AuthFailure() {
    useEffect(() => {
        // Redirect back to landing page after 3 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 3000);
    }, []);

    return (
        <div className="auth-callback-container">
            <div className="auth-callback-content">
                <div className="auth-callback-error">❌</div>
                <h2>Authentication Failed</h2>
                <p>There was an issue with your Google sign-in. Please try again.</p>
                <p>Redirecting back to sign-in...</p>
            </div>
        </div>
    );
}
