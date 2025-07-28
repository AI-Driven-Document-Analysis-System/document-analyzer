"use client"

import type React from "react"

import { useState } from "react"
// Update the import path if the file is located elsewhere, for example:
import { authService } from "../../services/authService"
// Or, if the file does not exist, create 'authService.ts' in 'src/services' with a basic export:

interface AuthModalProps {
  onClose: () => void
  onAuthSuccess: (user: any) => void
}

export function AuthModal({ onClose, onAuthSuccess }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    confirmPassword: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      if (isLogin) {
        const response = await authService.login(formData.email, formData.password)
        onAuthSuccess(response.user)
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match")
          setLoading(false)
          return
        }
        const response = await authService.register({
          email: formData.email,
          password: formData.password,
          firstName: formData.firstName,
          lastName: formData.lastName,
        })
        onAuthSuccess(response.user)
      }
    } catch (err: any) {
      setError(err.message || "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-content">
          {/* Left Side - Branding */}
          <div className="auth-modal-left">
            <div className="auth-brand">
              <div className="auth-brand-icon">📄</div>
              <h2 className="auth-brand-title">DocAnalyzer</h2>
            </div>
            <div className="auth-features">
              <h3 className="auth-features-title">{isLogin ? "Welcome Back!" : "Join DocAnalyzer"}</h3>
              <p className="auth-features-description">
                {isLogin
                  ? "Sign in to continue analyzing your documents with AI"
                  : "Start your journey with AI-powered document analysis"}
              </p>
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

          {/* Right Side - Form */}
          <div className="auth-modal-right">
            <button className="auth-modal-close" onClick={onClose}>
              ✕
            </button>

            <div className="auth-form-container">
              <div className="auth-form-header">
                <h2 className="auth-form-title">{isLogin ? "Sign In" : "Create Account"}</h2>
                <p className="auth-form-subtitle">
                  {isLogin ? "Enter your credentials to access your account" : "Fill in your details to get started"}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="auth-form">
                {!isLogin && (
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">First Name</label>
                      <input
                        type="text"
                        name="firstName"
                        value={formData.firstName}
                        onChange={handleInputChange}
                        className="form-input"
                        required
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

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>

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

                {error && <div className="auth-error">{error}</div>}

                <button type="submit" className="btn btn-primary w-full" disabled={loading}>
                  {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
                </button>
              </form>

              <div className="auth-form-footer">
                <p className="auth-switch-text">
                  {isLogin ? "Don't have an account?" : "Already have an account?"}
                  <button
                    type="button"
                    className="auth-switch-button"
                    onClick={() => {
                      setIsLogin(!isLogin)
                      setError("")
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
