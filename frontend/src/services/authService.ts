interface RegisterData {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: any;
}

interface RegisterResponse {
  user: any;
}

class AuthService {
  private baseURL = 'http://localhost:8000/api/auth';

  async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // THIS IS THE KEY FIX - Store the token in localStorage
      localStorage.setItem('token', data.access_token);
      
      // Optional: Store user data
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      console.log('Token stored successfully:', data.access_token);
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(userData: RegisterData): Promise<RegisterResponse> {
    try {
      const response = await fetch(`${this.baseURL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          first_name: userData.firstName,
          last_name: userData.lastName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      
      // After successful registration, automatically log them in
      const loginResponse = await this.login(userData.email, userData.password);
      
      return { user: loginResponse.user };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        await fetch(`${this.baseURL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear all persistence data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('lastPath'); // Add this line
    }
  }

  async getCurrentUser(): Promise<any> {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await fetch(`${this.baseURL}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          this.logout();
          throw new Error('Session expired');
        }
        throw new Error('Failed to get user info');
      }

      return await response.json();
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  async googleOAuth(userData: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseURL}/google-oauth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          first_name: userData.firstName,
          last_name: userData.lastName,
          google_id: userData.googleId,
          provider: userData.provider,
          supabase_access_token: userData.supabaseAccessToken,
          supabase_refresh_token: userData.supabaseRefreshToken
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Google OAuth failed');
      }

      const data = await response.json();
      
      // Store the token in localStorage
      localStorage.setItem('token', data.access_token);
      
      // Store user data
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      console.log('Google OAuth token stored successfully:', data.access_token);
      
      return data;
    } catch (error) {
      console.error('Google OAuth error:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();
