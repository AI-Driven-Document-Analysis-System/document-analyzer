"use client" // This directive tells Next.js this is a client-side component that runs in the browser
// (needed because we use hooks like useState which only work on the client)

import type React from "react" // Import React types for TypeScript intellisense and type checking

import { useState } from "react" // Import useState hook to manage component's internal state
// (React components need state to remember user input and UI changes)

import { authService } from "../../services/authService" // Import authentication service
// (This handles the actual API calls to login/register users on the backend)

/**
 * Interface defining the props (inputs) that this component expects from its parent
 * This ensures type safety - parent components must provide these exact functions
 */
interface AuthModalProps {
  onClose: () => void // Function parent provides to close/hide the modal
  onAuthSuccess: (user: any) => void // Function parent provides to handle successful login
  // (Parent needs to know when user successfully logs in to update the main app state)
}

/**
 * AuthModal: A popup window that lets users either login or create a new account
 * This is a "modal" because it appears on top of other content and blocks interaction with the background
 */
export function AuthModal({ onClose, onAuthSuccess }: AuthModalProps) {
  
  // STATE MANAGEMENT - These useState hooks store data that can change during user interaction
  
  // Toggle between login form and registration form
  // Why needed: Same modal shows different fields based on whether user wants to login or sign up
  const [isLogin, setIsLogin] = useState(true) // Start with login form by default
  
  // Store all form input values in one object
  // Why needed: React needs to track what user types so it can submit the data
  const [formData, setFormData] = useState({
    email: "",           // Required for both login and registration
    password: "",        // Required for both login and registration  
    firstName: "",       // Only needed for registration
    lastName: "",        // Only needed for registration
    confirmPassword: "", // Only needed for registration (to verify password was typed correctly)
  })
  
  // Track if form is currently being submitted
  // Why needed: Prevents user from clicking submit multiple times and shows loading indicator
  const [loading, setLoading] = useState(false)
  
  // Store any error messages to show user
  // Why needed: If login/registration fails, user needs to know what went wrong
  const [error, setError] = useState("")

  // EVENT HANDLERS - Functions that respond to user actions

  /**
   * Updates form data when user types in any input field
   * Why needed: React doesn't automatically update state when user types - we must do it manually
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData, // Keep all existing form data unchanged
      [e.target.name]: e.target.value, // Update only the field that changed
    })
    setError("") // Clear any previous error when user starts typing
    // (Gives user a fresh start rather than showing stale error messages)
  }

  /**
   * Handles form submission (when user clicks login/register button)
   * This is async because it needs to wait for server response
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault() // Prevent browser's default form submission behavior
    // (Default behavior would refresh the page, which we don't want in a single-page app)
    
    setLoading(true) // Show loading state to user
    setError("")     // Clear any previous errors
    
    try {
      if (isLogin) {
        // LOGIN FLOW - User wants to sign in with existing account
        const response = await authService.login(formData.email, formData.password)
        // Call parent's success handler with user data
        // (This lets the main app know user is now logged in)
        onAuthSuccess(response.user)
      } else {
        // REGISTRATION FLOW - User wants to create new account
        
        // Validation: Make sure passwords match before sending to server
        // (Prevents unnecessary server call and gives immediate feedback)
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match")
          setLoading(false)
          return // Exit early, don't proceed with registration
        }
        
        // Send registration data to server
        const response = await authService.register({
          email: formData.email,
          password: formData.password,
          firstName: formData.firstName,
          lastName: formData.lastName,
        })
        // Call parent's success handler with new user data
        onAuthSuccess(response.user)
      }
    } catch (err: any) {
      // If login/registration fails, show error message to user
      // (Server might return specific error like "email already exists" or "wrong password")
      setError(err.message || "An error occurred")
    } finally {
      // Always stop loading indicator, whether success or failure
      setLoading(false)
    }
  }

  // RENDER - The actual HTML/JSX that creates the visual interface
  return (
    // Overlay: Semi-transparent background that covers the whole screen
    // onClick={onClose} - Clicking outside the modal closes it (common UX pattern)
    <div className="auth-modal-overlay" onClick={onClose}>
      
      {/* Main modal container - the actual popup box */}
      {/* stopPropagation prevents overlay click when clicking inside modal */}
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-content">
          
          {/* LEFT SIDE: Branding and feature showcase */}
          {/* Why included: Makes the modal more engaging and explains value proposition */}
          <div className="auth-modal-left">
            
            {/* App branding section */}
            <div className="auth-brand">
              <div className="auth-brand-icon">📄</div>
              <h2 className="auth-brand-title">DocAnalyzer</h2>
            </div>
            
            {/* Dynamic content based on login vs registration */}
            <div className="auth-features">
              <h3 className="auth-features-title">
                {isLogin ? "Welcome Back!" : "Join DocAnalyzer"}
              </h3>
              <p className="auth-features-description">
                {isLogin
                  ? "Sign in to continue analyzing your documents with AI"
                  : "Start your journey with AI-powered document analysis"}
              </p>
              
              {/* Feature list - shows what the app can do */}
              {/* Why needed: Motivates user to complete registration */}
              <div className="auth-feature-list">
                <div className="auth-feature-item">
                  <span className="auth-feature-icon">🧠</span>
                  <span>AI-Powered Summarization</span>
                </div>
                <div className="auth-feature-item">
                  <span className="auth-feature-icon">🔍</span>
                  <span>Semantic Search</span>
                </div>
                <div className="auth-feature-item">
                  <span className="auth-feature-icon">💬</span>
                  <span>Interactive Document Chat</span>
                </div>
                <div className="auth-feature-item">
                  <span className="auth-feature-icon">📊</span>
                  <span>Advanced Analytics</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT SIDE: The actual login/registration form */}
          <div className="auth-modal-right">
            
            {/* Close button - X in top corner */}
            <button className="auth-modal-close" onClick={onClose}>
              ✕
            </button>

            <div className="auth-form-container">
              
              {/* Form header - title and description */}
              <div className="auth-form-header">
                <h2 className="auth-form-title">
                  {isLogin ? "Sign In" : "Create Account"}
                </h2>
                <p className="auth-form-subtitle">
                  {isLogin 
                    ? "Enter your credentials to access your account" 
                    : "Fill in your details to get started"}
                </p>
              </div>

              {/* The actual form that submits data */}
              <form onSubmit={handleSubmit} className="auth-form">
                
                {/* Name fields - only shown during registration */}
                {/* Conditional rendering: !isLogin means "if NOT in login mode" */}
                {!isLogin && (
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">First Name</label>
                      <input
                        type="text"
                        name="firstName" // This name matches the key in formData state
                        value={formData.firstName} // Controlled input - React controls the value
                        onChange={handleInputChange} // Updates state when user types
                        className="form-input"
                        required // HTML5 validation - browser won't submit if empty
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Last Name</label>
                      <input
                        type="text"
                        name="lastName"
                        value={formData.lastName}
                        onChange={handleInputChange}
                        className="form-input"
                        required
                      />
                    </div>
                  </div>
                )}

                {/* Email field - shown for both login and registration */}
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email" // Browser validates email format automatically
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

                {/* Password field - shown for both login and registration */}
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input
                    type="password" // Hides password characters with dots
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

                {/* Password confirmation - only shown during registration */}
                {/* Why needed: Prevents typos in password since user can't see what they're typing */}
                {!isLogin && (
                  <div className="form-group">
                    <label className="form-label">Confirm Password</label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    />
                  </div>
                )}

                {/* Error message display - only shown if there's an error */}
                {error && <div className="auth-error">{error}</div>}

                {/* Submit button - disabled during loading to prevent double-submission */}
                <button type="submit" className="btn btn-primary w-full" disabled={loading}>
                  {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
                  {/* Dynamic button text based on current state */}
                </button>
              </form>

              {/* Footer with link to switch between login/registration */}
              {/* Why needed: Users often land on wrong form, this lets them switch easily */}
              <div className="auth-form-footer">
                <p className="auth-switch-text">
                  {isLogin ? "Don't have an account?" : "Already have an account?"}
                  <button
                    type="button" // Not a submit button, just switches modes
                    className="auth-switch-button"
                    onClick={() => {
                      setIsLogin(!isLogin) // Toggle between login and registration
                      setError("") // Clear any errors when switching
                      // Reset form data to prevent confusion
                      // (User might have partially filled registration form, then switch to login)
                      setFormData({
                        email: "",
                        password: "",
                        firstName: "",
                        lastName: "",
                        confirmPassword: "",
                      })
                    }}
                  >
                    {isLogin ? "Sign Up" : "Sign In"}
                  </button>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/*
SUMMARY OF WHAT THIS CODE DOES:

1. Creates a popup modal (overlay window) for user authentication
2. Shows either a login form OR registration form (user can switch between them)
3. Collects user input (email, password, name for registration)
4. Validates input (checks if passwords match during registration)
5. Sends data to authentication service (backend API)
6. Handles success (calls parent component's success function) 
7. Handles errors (shows error messages to user)
8. Provides good user experience with loading states, form validation, and easy switching

WHY EACH PART IS NEEDED:
- State management: React needs to track user input and UI changes
- Event handlers: React needs explicit functions to respond to user actions
- Conditional rendering: Same component shows different content based on current mode
- Form validation: Prevents bad data from being sent to server
- Error handling: Users need feedback when something goes wrong
- Loading states: Users need to know when actions are in progress
- Type safety: TypeScript prevents bugs by checking data types
*/