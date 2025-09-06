


import React, { useState, useEffect } from 'react';
import './settings.css';

const Settings: React.FC = () => {
  const [activeSection, setActiveSection] = useState('security');
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form states
  const [changeEmailForm, setChangeEmailForm] = useState({ email: '', password: '' });
  const [changePasswordForm, setChangePasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, []);

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
    if (newDarkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    showMessage('success', `Dark mode ${newDarkMode ? 'enabled' : 'disabled'}`);
  };

  const handleChangeEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        showMessage('error', 'Authentication required');
        return;
      }

      const response = await fetch('http://localhost:8000/api/profile/change-email', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_email: changeEmailForm.email,
          password: changeEmailForm.password,
        }),
      });

      if (response.ok) {
        setChangeEmailForm({ email: '', password: '' });
        showMessage('success', 'Email changed successfully!');
      } else {
        const errorData = await response.json();
        showMessage('error', errorData.detail || 'Failed to change email');
      }
    } catch (error) {
      showMessage('error', 'An error occurred while changing email');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    if (changePasswordForm.newPassword !== changePasswordForm.confirmPassword) {
      showMessage('error', 'New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        showMessage('error', 'Authentication required');
        return;
      }

      const response = await fetch('http://localhost:8000/api/profile/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: changePasswordForm.currentPassword,
          new_password: changePasswordForm.newPassword,
        }),
      });

      if (response.ok) {
        setChangePasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
        showMessage('success', 'Password changed successfully!');
      } else {
        const errorData = await response.json();
        showMessage('error', errorData.detail || 'Failed to change password');
      }
    } catch (error) {
      showMessage('error', 'An error occurred while changing password');
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { id: 'security', name: 'Security & Login', icon: 'fa-lock' },
    { id: 'personalization', name: 'Personalization', icon: 'fa-palette' },
    { id: 'documents', name: 'Document Preferences', icon: 'fa-file-lines' },
    { id: 'notifications', name: 'Notifications', icon: 'fa-bell' },
    { id: 'billing', name: 'Billing & Subscription', icon: 'fa-credit-card' },
  ];

  return (
    <div className="settings-container">
      <div className="settings-layout">
        {/* Header */}
        <header className="settings-header">
          <h1>Settings</h1>
          <p>Manage your account preferences and security settings</p>
        </header>

        {/* Message Toast */}
        {message && (
          <div className={`settings-message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="settings-body">
          {/* Sidebar */}
          <nav className="settings-sidebar">
            <ul>
              {sections.map((section) => (
                <li key={section.id}>
                  <button
                    onClick={() => setActiveSection(section.id)}
                    className={activeSection === section.id ? 'active' : ''}
                  >
                    <i className={`fas ${section.icon}`}></i>
                    <span>{section.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          </nav>

          {/* Main Content */}
          <main className="settings-content">
            <div className="settings-card">
              {/* Security Section */}
              {activeSection === 'security' && (
                <div>
                  <h2>
                    <i className="fas fa-lock"></i> Security & Login
                  </h2>
                  <div className="settings-section">
                    <h3>Change Email Address</h3>
                    <form onSubmit={handleChangeEmail}>
                      <div className="form-group">
                        <label>New Email Address</label>
                        <input
                          type="email"
                          value={changeEmailForm.email}
                          onChange={(e) =>
                            setChangeEmailForm({ ...changeEmailForm, email: e.target.value })
                          }
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Current Password</label>
                        <input
                          type="password"
                          value={changeEmailForm.password}
                          onChange={(e) =>
                            setChangeEmailForm({ ...changeEmailForm, password: e.target.value })
                          }
                          required
                        />
                      </div>
                      <button type="submit" disabled={loading}>
                        {loading ? 'Changing...' : 'Change Email'}
                      </button>
                    </form>
                  </div>

                  <div className="settings-section">
                    <h3>Change Password</h3>
                    <form onSubmit={handleChangePassword}>
                      <div className="form-group">
                        <label>Current Password</label>
                        <input
                          type="password"
                          value={changePasswordForm.currentPassword}
                          onChange={(e) =>
                            setChangePasswordForm({
                              ...changePasswordForm,
                              currentPassword: e.target.value,
                            })
                          }
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>New Password</label>
                        <input
                          type="password"
                          value={changePasswordForm.newPassword}
                          onChange={(e) =>
                            setChangePasswordForm({
                              ...changePasswordForm,
                              newPassword: e.target.value,
                            })
                          }
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label>Confirm New Password</label>
                        <input
                          type="password"
                          value={changePasswordForm.confirmPassword}
                          onChange={(e) =>
                            setChangePasswordForm({
                              ...changePasswordForm,
                              confirmPassword: e.target.value,
                            })
                          }
                          required
                        />
                      </div>
                      <button type="submit" disabled={loading}>
                        {loading ? 'Changing...' : 'Change Password'}
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* Personalization */}
              {activeSection === 'personalization' && (
                <div>
                  <h2>
                    <i className="fas fa-palette"></i> Personalization
                  </h2>
                  <div className="settings-section">
                    <h3>Theme Preferences</h3>
                    <div className="toggle-group">
                      <span>Dark Mode</span>
                      <button
                        className={`toggle-switch ${darkMode ? 'active' : ''}`}
                        onClick={toggleDarkMode}
                      >
                        <span></span>
                      </button>
                    </div>
                  </div>
                  <div className="settings-section">
                    <h3>Default Dashboard View</h3>
                    <div className="radio-group">
                      <label>
                        <input type="radio" name="dashboardView" defaultChecked />
                        Invoices
                      </label>
                      <label>
                        <input type="radio" name="dashboardView" />
                        Medical
                      </label>
                      <label>
                        <input type="radio" name="dashboardView" />
                        Legal
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* Document Preferences */}
              {activeSection === 'documents' && (
                <div>
                  <h2>
                    <i className="fas fa-file-lines"></i> Document Preferences
                  </h2>
                  <div className="settings-section">
                    <h3>Auto-categorization</h3>
                    <p className="disabled-feature">Coming Soon</p>
                  </div>
                  <div className="settings-section">
                    <h3>Document Notifications</h3>
                    <p className="disabled-feature">Coming Soon</p>
                  </div>
                  <div className="settings-section">
                    <h3>Default Export Format</h3>
                    <select>
                      <option>PDF</option>
                      <option>CSV</option>
                      <option>JSON</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeSection === 'notifications' && (
                <div>
                  <h2>
                    <i className="fas fa-bell"></i> Notifications
                  </h2>
                  <div className="settings-section">
                    <h3>Email Notifications</h3>
                    <div className="notification-item">
                      <span>New document processed</span>
                      <p className="disabled-feature">Coming Soon</p>
                    </div>
                    <div className="notification-item">
                      <span>AI recommendations available</span>
                      <p className="disabled-feature">Coming Soon</p>
                    </div>
                    <div className="notification-item">
                      <span>Contract deadlines</span>
                      <p className="disabled-feature">Coming Soon</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Billing */}
              {activeSection === 'billing' && (
                <div>
                  <h2>
                    <i className="fas fa-credit-card"></i> Billing & Subscription
                  </h2>
                  <div className="settings-section">
                    <h3>Current Plan</h3>
                    <div className="plan-info">
                      <h4>Pro Plan</h4>
                      <p>Status: Active</p>
                      <p>Next billing: 2024-02-01</p>
                    </div>
                  </div>
                  <div className="settings-section">
                    <h3>Plan Management</h3>
                    <button className="btn-primary disabled">Upgrade Plan</button>
                    <button className="btn-secondary disabled">Downgrade Plan</button>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Settings;