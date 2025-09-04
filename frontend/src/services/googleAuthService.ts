// DEPRECATED: This file is replaced by supabaseAuthService.ts
// This file is kept temporarily for reference during migration
// TODO: Remove this file after confirming all references are updated

import { authService } from './authService';

export class GoogleAuthService {
    /**
     * @deprecated Use supabaseAuthService.signInWithGoogle() instead
     */
    async signInWithGoogle(): Promise<void> {
        throw new Error('GoogleAuthService is deprecated. Use supabaseAuthService.signInWithGoogle() instead.');
    }

    /**
     * @deprecated Use supabaseAuthService.handleOAuthCallback() instead
     */
    async handleOAuthCallback(): Promise<any> {
        throw new Error('GoogleAuthService is deprecated. Use supabaseAuthService.handleOAuthCallback() instead.');
    }

    /**
     * @deprecated Use supabaseAuthService.syncWithLocalAuth() instead
     */
    private async syncWithLocalAuth(userData: any): Promise<any> {
        throw new Error('GoogleAuthService is deprecated. Use supabaseAuthService instead.');
    }

    /**
     * @deprecated Use supabaseAuthService.signOut() instead
     */
    async signOut(): Promise<void> {
        try {
            // Always clear local auth
            await authService.logout();
        } catch (error) {
            console.error('Sign-out error:', error);
        }
    }

    /**
     * @deprecated Use supabaseAuthService.isGoogleAuthenticated() instead
     */
    async isGoogleAuthenticated(): Promise<boolean> {
        return false;
    }
}

export const googleAuthService = new GoogleAuthService();
