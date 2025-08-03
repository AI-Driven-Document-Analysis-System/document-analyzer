// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

// interface LoginData {
//   email: string
//   password: string
// }

// interface RegisterData {
//   email: string
//   password: string
//   firstName: string
//   lastName: string
// }

// class AuthService {
//   private async request(endpoint: string, options: RequestInit = {}) {
//     const url = `${API_BASE_URL}${endpoint}`
//     const config = {
//       headers: {
//         "Content-Type": "application/json",
//         ...options.headers,
//       },
//       ...options,
//     }

//     const response = await fetch(url, config)
//     const data = await response.json()

//     if (!response.ok) {
//       throw new Error(data.message || "An error occurred")
//     }

//     return data
//   }

//   async login(email: string, password: string) {
//     const response = await this.request("/auth/login", {
//       method: "POST",
//       body: JSON.stringify({ email, password }),
//     })

//     if (response.token) {
//       localStorage.setItem("auth_token", response.token)
//       localStorage.setItem("user", JSON.stringify(response.user))
//     }

//     return response
//   }

//   async register(userData: RegisterData) {
//     const response = await this.request("/auth/register", {
//       method: "POST",
//       body: JSON.stringify(userData),
//     })

//     if (response.token) {
//       localStorage.setItem("auth_token", response.token)
//       localStorage.setItem("user", JSON.stringify(response.user))
//     }

//     return response
//   }

//   async logout() {
//     localStorage.removeItem("auth_token")
//     localStorage.removeItem("user")
//   }

//   getToken() {
//     return localStorage.getItem("auth_token")
//   }

//   getUser() {
//     const user = localStorage.getItem("user")
//     return user ? JSON.parse(user) : null
//   }

//   isAuthenticated() {
//     return !!this.getToken()
//   }
// }

// export const authService = new AuthService()





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
      // Always clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
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
}

export const authService = new AuthService();