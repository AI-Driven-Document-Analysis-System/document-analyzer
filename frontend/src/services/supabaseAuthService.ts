import { supabase } from '../lib/supabase';
import { authService } from './authService';

export class SupabaseAuthService {
  /**
   * Sign in with Google using Supabase OAuth
   * Forces account selection to fix the previous Appwrite issue
   */
  async signInWithGoogle(): Promise<void> {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'select_account', // Forces account selection
          },
        },
      });

      if (error) {
        console.error('Google sign-in error:', error);
        throw new Error(error.message || 'Failed to initiate Google sign-in');
      }
    } catch (error) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  }

  /**
   * Sign up with Google using Supabase OAuth
   * Forces account selection and consent screen
   */
  async signUpWithGoogle(): Promise<void> {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?mode=signup`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent select_account', // Forces consent and account selection
          },
        },
      });

      if (error) {
        console.error('Google sign-up error:', error);
        throw new Error(error.message || 'Failed to initiate Google sign-up');
      }
    } catch (error) {
      console.error('Google sign-up error:', error);
      throw error;
    }
  }

  /**
   * Handle OAuth callback from Supabase
   */
  async handleOAuthCallback(): Promise<any> {
    try {
      // Get the current session from Supabase
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError) {
        throw new Error(`Session error: ${sessionError.message}`);
      }

      if (!session || !session.user) {
        throw new Error('No valid session found');
      }

      // Extract user information from Supabase session
      const user = session.user;
      const userData = {
        email: user.email || '',
        firstName: user.user_metadata?.full_name?.split(' ')[0] || user.user_metadata?.name?.split(' ')[0] || '',
        lastName: user.user_metadata?.full_name?.split(' ').slice(1).join(' ') || user.user_metadata?.name?.split(' ').slice(1).join(' ') || '',
        googleId: user.id,
        provider: 'google',
        supabaseAccessToken: session.access_token,
        supabaseRefreshToken: session.refresh_token
      };

      // Sync with your local authentication system
      const localAuthResponse = await this.syncWithLocalAuth(userData);
      
      return localAuthResponse;
    } catch (error) {
      console.error('OAuth callback error:', error);
      throw new Error(`Failed to complete Google authentication: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
   * Sign out from Supabase and local system
   */
  async signOut(): Promise<void> {
    try {
      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Supabase sign-out error:', error);
      }
    } catch (error) {
      console.error('Google sign-out error:', error);
    } finally {
      // Always clear local auth
      await authService.logout();
    }
  }

  /**
   * Check if user is authenticated with Supabase
   */
  async isGoogleAuthenticated(): Promise<boolean> {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      return !!session;
    } catch {
      return false;
    }
  }

  /**
   * Get current Supabase session
   */
  async getCurrentSession() {
    try {
      const { data: { session }, error } = await supabase.auth.getSession();
      if (error) throw error;
      return session;
    } catch (error) {
      console.error('Error getting current session:', error);
      return null;
    }
  }

  /**
   * Clear any existing sessions to force fresh login
   */
  async clearExistingSessions(): Promise<void> {
    try {
      await supabase.auth.signOut();
      // Clear any cached auth data
      localStorage.removeItem('supabase.auth.token');
      sessionStorage.clear();
    } catch (error) {
      console.error('Error clearing sessions:', error);
    }
  }
}

export const supabaseAuthService = new SupabaseAuthService();
