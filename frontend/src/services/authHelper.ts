/**
 * Authentication helper utilities
 */

export interface AuthStatus {
  isAuthenticated: boolean
  token: string | null
  user: any | null
}

/**
 * Check if user is currently authenticated
 */
export function checkAuthStatus(): AuthStatus {
  const token = localStorage.getItem("token")
  const user = localStorage.getItem("user")
  
  return {
    isAuthenticated: !!token,
    token,
    user: user ? JSON.parse(user) : null
  }
}

/**
 * Get the current authentication token
 */
export function getAuthToken(): string | null {
  return localStorage.getItem("token")
}

/**
 * Check if token is valid (basic check)
 */
export function isTokenValid(token: string): boolean {
  if (!token) return false
  
  try {
    // Basic JWT token validation (check if it's not expired)
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Date.now() / 1000
    
    return payload.exp > currentTime
  } catch (error) {
    return false
  }
}

/**
 * Clear authentication data
 */
export function clearAuth(): void {
  localStorage.removeItem("token")
  localStorage.removeItem("user")
}

/**
 * Set authentication data
 */
export function setAuth(token: string, user: any): void {
  localStorage.setItem("token", token)
  localStorage.setItem("user", JSON.stringify(user))
}
