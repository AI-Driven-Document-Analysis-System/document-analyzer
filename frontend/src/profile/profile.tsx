"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { User, Mail, Calendar, Crown, LogOut, Edit, Save, X } from "lucide-react"

// === Types ===
interface UserProfile {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  documents_count: number
  current_plan: string
  plan_features: Record<string, any>
  created_at: string
}

// === Main Component ===
const UserProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    first_name: "",
    last_name: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Fetch profile data from backend
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true)
        const token = localStorage.getItem("token")

        if (!token) {
          setError("No authentication token found")
          return
        }

        const response = await fetch("http://localhost:8000/api/profile/me", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          if (response.status === 401) {
            setError("Authentication expired. Please login again.")
            // Redirect to login or refresh token
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setProfile(data)
        setEditForm({
          first_name: data.first_name || "",
          last_name: data.last_name || "",
        })
      } catch (err) {
        console.error("Error fetching profile:", err)
        setError("Failed to load profile data. Please try again.")
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  const handleUpdateProfile = async () => {
    try {
      setError(null)
      setLoading(true)

      const token = localStorage.getItem("token")
      if (!token) {
        setError("No authentication token found")
        return
      }

      const response = await fetch("http://localhost:8000/api/auth/me", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: editForm.first_name || null,
          last_name: editForm.last_name || null,
        }),
      })

      if (!response.ok) {
        if (response.status === 401) {
          setError("Authentication expired. Please login again.")
          return
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const updatedUser = await response.json()

      // Update profile with new user data
      if (profile) {
        setProfile({
          ...profile,
          first_name: updatedUser.first_name,
          last_name: updatedUser.last_name,
        })
      }

      setSuccess("Profile updated successfully!")
      setEditing(false)
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error("Error updating profile:", err)
      setError("Failed to update profile. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    window.location.reload() // This will trigger the auth check and redirect to landing
  }

  const handleUpgradePlan = () => {
    alert("Upgrade plan feature coming soon!")
  }

  // Loading state
  if (loading && !profile) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p style={styles.loadingText}>Loading profile...</p>
      </div>
    )
  }

  if (error && !profile) {
    return (
      <div style={styles.errorContainer}>
        <p style={styles.errorText}>{error}</p>
        <button onClick={() => window.location.reload()} style={styles.retryButton}>
          Retry
        </button>
      </div>
    )
  }

  if (!profile) {
    return (
      <div style={styles.errorContainer}>
        <p style={styles.errorText}>No profile data available.</p>
        <button onClick={() => window.location.reload()} style={styles.retryButton}>
          Retry
        </button>
      </div>
    )
  }

  return (
    <>
      {/* Embedded CSS */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>

      <div style={styles.container}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>User Profile</h1>
          <p style={styles.subtitle}>Manage your account settings and view your activity</p>
        </div>

        {/* Alerts */}
        {error && (
          <div style={styles.alertError} className="animate-fade-in">
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div style={styles.alertSuccess} className="animate-fade-in">
            <p>{success}</p>
          </div>
        )}

        <div style={styles.grid}>
          {/* Basic Info */}
          <div style={styles.card} className="animate-fade-in">
            <div style={styles.cardHeader}>
              <h2 style={styles.cardTitle}>
                <User style={iconStyles} /> Basic Information
              </h2>
              {!editing ? (
                <button onClick={() => setEditing(true)} style={styles.editButton} disabled={loading}>
                  <Edit style={iconStyles} /> Edit
                </button>
              ) : (
                <div style={styles.buttonGroup}>
                  <button
                    onClick={handleUpdateProfile}
                    style={loading ? styles.savingButton : styles.saveButton}
                    disabled={loading}
                  >
                    {loading ? <span style={styles.spinnerSmall}></span> : <Save style={iconStyles} />}
                    {loading ? "Saving..." : "Save"}
                  </button>
                  <button
                    onClick={() => {
                      setEditing(false)
                      setEditForm({
                        first_name: profile.first_name || "",
                        last_name: profile.last_name || "",
                      })
                    }}
                    style={styles.cancelButton}
                    disabled={loading}
                  >
                    <X style={iconStyles} /> Cancel
                  </button>
                </div>
              )}
            </div>

            <div style={styles.formGroup}>
              <div style={styles.grid2}>
                <div>
                  <label style={styles.label}>First Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.first_name}
                      onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                      style={styles.input}
                      placeholder="Enter your first name"
                      disabled={loading}
                    />
                  ) : (
                    <p style={styles.value}>{profile.first_name || "Not set"}</p>
                  )}
                </div>
                <div>
                  <label style={styles.label}>Last Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.last_name}
                      onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                      style={styles.input}
                      placeholder="Enter your last name"
                      disabled={loading}
                    />
                  ) : (
                    <p style={styles.value}>{profile.last_name || "Not set"}</p>
                  )}
                </div>
              </div>

              <div>
                <label style={styles.label}>Email</label>
                <p style={styles.valueWithIcon}>
                  <Mail style={iconStyles} /> {profile.email}
                </p>
              </div>

              <div>
                <label style={styles.label}>Member Since</label>
                <p style={styles.valueWithIcon}>
                  <Calendar style={iconStyles} />
                  {new Date(profile.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>

              <div>
                <label style={styles.label}>Documents Uploaded</label>
                <p style={styles.docCount}>{profile.documents_count}</p>
              </div>
            </div>

            <div style={styles.logoutSection}>
              <button onClick={handleLogout} style={styles.logoutButton}>
                <LogOut style={iconStyles} /> Logout
              </button>
            </div>
          </div>

          {/* Plan Info */}
          <div style={styles.card} className="animate-fade-in">
            <h2 style={styles.cardTitle}>
              <Crown style={iconStyles} /> Current Plan
            </h2>
            <div style={styles.planInfo}>
              <div style={styles.planName}>{profile.current_plan}</div>
              <div style={styles.features}>
                <div style={styles.featureTitle}>Features:</div>
                <ul style={styles.featureList}>
                  {Object.entries(profile.plan_features).map(([key, value]) => (
                    <li key={key} style={styles.featureItem}>
                      <span>{key.replace("_", " ")}:</span>
                      <span style={styles.featureValue}>{String(value)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <button onClick={handleUpgradePlan} style={styles.upgradeButton}>
              Upgrade Plan
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

// === Inline Styles ===
const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#F9FAFB",
    padding: "2rem",
    fontFamily: "system-ui, -apple-system, sans-serif",
    color: "#1F2937",
  },
  header: {
    marginBottom: "2rem",
    textAlign: "center" as const,
  },
  title: {
    fontSize: "2rem",
    fontWeight: "bold",
    color: "#111827",
    marginBottom: "0.5rem",
  },
  subtitle: {
    color: "#6B7280",
    marginBottom: "0.5rem",
  },
  alertError: {
    backgroundColor: "#FEE2E2",
    borderColor: "#FCA5A5",
    color: "#991B1B",
    padding: "1rem",
    borderRadius: "0.5rem",
    border: "1px solid",
    marginBottom: "1.5rem",
  },
  alertSuccess: {
    backgroundColor: "#DCFCE7",
    borderColor: "#86EFAC",
    color: "#166534",
    padding: "1rem",
    borderRadius: "0.5rem",
    border: "1px solid",
    marginBottom: "1.5rem",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "3fr 1fr",
    gap: "2rem",
    marginBottom: "2rem",
  },
  card: {
    backgroundColor: "#FFFFFF",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)",
    borderRadius: "0.75rem",
    padding: "1.5rem",
    transition: "all 0.2s ease",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1.5rem",
  },
  cardTitle: {
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#1F2937",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
  },
  editButton: {
    backgroundColor: "#2563EB",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "0.375rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
  },
  buttonGroup: {
    display: "flex",
    gap: "0.5rem",
  },
  saveButton: {
    backgroundColor: "#059669",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "0.375rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
  },
  savingButton: {
    backgroundColor: "#047857",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "0.375rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    opacity: 0.8,
  },
  cancelButton: {
    backgroundColor: "#6B7280",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "0.375rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
  },
  formGroup: {
    marginBottom: "1rem",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "1rem",
    marginBottom: "1rem",
  },
  label: {
    display: "block",
    fontSize: "0.875rem",
    fontWeight: "500",
    color: "#374151",
    marginBottom: "0.25rem",
  },
  input: {
    width: "100%",
    padding: "0.75rem",
    border: "1px solid #D1D5DB",
    borderRadius: "0.375rem",
    fontSize: "1rem",
    outline: "none",
  },
  value: {
    color: "#1F2937",
    fontSize: "1rem",
  },
  valueWithIcon: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    color: "#1F2937",
  },
  docCount: {
    fontSize: "1.875rem",
    fontWeight: "bold",
    color: "#2563EB",
  },
  logoutSection: {
    marginTop: "2rem",
    paddingTop: "1rem",
    borderTop: "1px solid #E5E7EB",
  },
  logoutButton: {
    backgroundColor: "#DC2626",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "0.375rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
  },
  planInfo: {
    marginBottom: "1rem",
  },
  planName: {
    fontSize: "1.5rem",
    fontWeight: "bold",
    color: "#2563EB",
  },
  features: {
    marginTop: "0.75rem",
  },
  featureTitle: {
    fontWeight: "600",
    color: "#374151",
    marginBottom: "0.5rem",
  },
  featureList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
  },
  featureItem: {
    display: "flex",
    justifyContent: "space-between",
    padding: "0.25rem 0",
    fontSize: "0.875rem",
    color: "#4B5563",
  },
  featureValue: {
    fontWeight: "600",
    color: "#1F2937",
  },
  upgradeButton: {
    width: "100%",
    backgroundColor: "linear-gradient(90deg, #2563EB, #7C3AED)",
    background: "linear-gradient(90deg, #2563EB, #7C3AED)",
    color: "white",
    border: "none",
    padding: "0.75rem",
    borderRadius: "0.375rem",
    fontSize: "1rem",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  chartCard: {
    backgroundColor: "#FFFFFF",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)",
    borderRadius: "0.75rem",
    padding: "1.5rem",
    marginBottom: "2rem",
  },
  chartTitle: {
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#1F2937",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    marginBottom: "1.5rem",
  },
  chartContainer: {
    height: "256px",
  },
  loadingContainer: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F9FAFB",
  },
  spinner: {
    width: "48px",
    height: "48px",
    border: "4px solid #E5E7EB",
    borderTop: "4px solid #3B82F6",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },
  loadingText: {
    marginTop: "1rem",
    color: "#6B7280",
  },
  errorContainer: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F9FAFB",
  },
  errorText: {
    color: "#DC2626",
    marginBottom: "1rem",
  },
  retryButton: {
    padding: "0.5rem 1rem",
    backgroundColor: "#2563EB",
    color: "white",
    border: "none",
    borderRadius: "0.375rem",
    cursor: "pointer",
  },
  spinnerSmall: {
    width: "16px",
    height: "16px",
    border: "2px solid white",
    borderTop: "2px solid transparent",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    display: "inline-block",
    marginRight: "0.5rem",
  },
}

// Icon styles
const iconStyles = {
  marginRight: "0.5rem",
} as const

export default UserProfilePage