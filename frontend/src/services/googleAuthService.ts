import { account } from './appwriteConfig';
import { authService } from './authService';

export class GoogleAuthService {
    /**
     * Initiate Google OAuth sign-in
     */
    async signInWithGoogle(): Promise<void> {
        try {
            // Create OAuth2 session with Google using Appwrite
            const redirectUrl = window.location.origin + '/auth/callback';
            const failureUrl = window.location.origin + '/auth/failure';
            
            // Use Appwrite's OAuth2 method
            account.createOAuth2Session('google' as any, redirectUrl, failureUrl);
        } catch (error) {
            console.error('Google sign-in error:', error);
            throw new Error('Failed to initiate Google sign-in');
        }
    }

    /**
     * Handle OAuth callback and sync with local auth system
     */
    async handleOAuthCallback(): Promise<any> {
        try {
            // Get the current session from Appwrite
            const session = await account.getSession('current');
            
            // Get user details from Appwrite
            const user = await account.get();
            
            // Extract user information
            const userData = {
                email: user.email,
                firstName: user.name.split(' ')[0] || '',
                lastName: user.name.split(' ').slice(1).join(' ') || '',
                googleId: user.$id,
                provider: 'google'
            };

            // Sync with your local authentication system
            const localAuthResponse = await this.syncWithLocalAuth(userData);
            
            return localAuthResponse;
        } catch (error) {
            console.error('OAuth callback error:', error);
            throw new Error('Failed to complete Google authentication');
        }
    }

    /**
     * Sync Google user with local authentication system
     */
    private async syncWithLocalAuth(userData: any): Promise<any> {
        try {
            // Use the authService method for consistency
            return await authService.googleOAuth(userData);
        } catch (error) {
            console.error('Local auth sync error:', error);
            throw error;
        }
    }

    /**
     * Sign out from Google and local system
     */
    async signOut(): Promise<void> {
        try {
            // Sign out from Appwrite
            await account.deleteSession('current');
        } catch (error) {
            console.error('Google sign-out error:', error);
        } finally {
            // Always clear local auth
            await authService.logout();
        }
    }

    /**
     * Check if user is authenticated with Google
     */
    async isGoogleAuthenticated(): Promise<boolean> {
        try {
            await account.getSession('current');
            return true;
        } catch {
            return false;
        }
    }
}

export const googleAuthService = new GoogleAuthService();
