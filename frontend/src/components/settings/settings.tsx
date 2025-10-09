import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import './settings.css';

const Settings: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [activeSection, setActiveSection] = useState('security');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form states
  const [changeEmailForm, setChangeEmailForm] = useState({ email: '', password: '' });
  const [changePasswordForm, setChangePasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // Document Preferences states
  const [documentPrefs, setDocumentPrefs] = useState({
    autoCategorization: true,
    autoProcessing: false,
    smartTagging: true,
    duplicateDetection: false,
    defaultExportFormat: 'PDF'
  });

  // Notification Preferences states
  const [notificationPrefs, setNotificationPrefs] = useState({
    emailNotifications: {
      documentProcessed: true,
      aiRecommendations: false,
      contractDeadlines: true,
      weeklyDigest: false,
      securityAlerts: true
    },
    pushNotifications: {
      documentUploaded: true,
      processingComplete: true,
      errorAlerts: true
    },
    frequency: 'immediate' // immediate, daily, weekly
  });

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleToggleDarkMode = () => {
    toggleDarkMode();
    showMessage('success', `Dark mode ${!isDarkMode ? 'enabled' : 'disabled'}`);
  };

  // Document Preferences handlers
  const handleDocumentPrefToggle = (key: keyof typeof documentPrefs) => {
    if (key === 'defaultExportFormat') return; // Handle separately
    
    setDocumentPrefs(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
    
    const prefNames = {
      autoCategorization: 'Auto-categorization',
      autoProcessing: 'Auto-processing',
      smartTagging: 'Smart tagging',
      duplicateDetection: 'Duplicate detection'
    };
    
    const newValue = !documentPrefs[key];
    showMessage('success', `${prefNames[key as keyof typeof prefNames]} ${newValue ? 'enabled' : 'disabled'}`);
  };

  const handleExportFormatChange = (format: string) => {
    setDocumentPrefs(prev => ({
      ...prev,
      defaultExportFormat: format
    }));
    showMessage('success', `Default export format changed to ${format}`);
  };

  // Notification Preferences handlers
  const handleEmailNotificationToggle = (key: keyof typeof notificationPrefs.emailNotifications) => {
    setNotificationPrefs(prev => ({
      ...prev,
      emailNotifications: {
        ...prev.emailNotifications,
        [key]: !prev.emailNotifications[key]
      }
    }));
    
    const prefNames = {
      documentProcessed: 'Document processed notifications',
      aiRecommendations: 'AI recommendations',
      contractDeadlines: 'Contract deadline alerts',
      weeklyDigest: 'Weekly digest',
      securityAlerts: 'Security alerts'
    };
    
    const newValue = !notificationPrefs.emailNotifications[key];
    showMessage('success', `${prefNames[key]} ${newValue ? 'enabled' : 'disabled'}`);
  };

  const handlePushNotificationToggle = (key: keyof typeof notificationPrefs.pushNotifications) => {
    setNotificationPrefs(prev => ({
      ...prev,
      pushNotifications: {
        ...prev.pushNotifications,
        [key]: !prev.pushNotifications[key]
      }
    }));
    
    const prefNames = {
      documentUploaded: 'Document upload notifications',
      processingComplete: 'Processing complete notifications',
      errorAlerts: 'Error alerts'
    };
    
    const newValue = !notificationPrefs.pushNotifications[key];
    showMessage('success', `${prefNames[key]} ${newValue ? 'enabled' : 'disabled'}`);
  };

  const handleFrequencyChange = (frequency: string) => {
    setNotificationPrefs(prev => ({
      ...prev,
      frequency
    }));
    showMessage('success', `Notification frequency changed to ${frequency}`);
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
                        className={`toggle-switch ${isDarkMode ? 'active' : ''}`}
                        onClick={handleToggleDarkMode}
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
                    <h3>Processing Settings</h3>
                    <div className="toggle-list">
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Auto-categorization</span>
                          <p>Automatically categorize documents based on content</p>
                        </div>
                        <button
                          className={`toggle-switch ${documentPrefs.autoCategorization ? 'active' : ''}`}
                          onClick={() => handleDocumentPrefToggle('autoCategorization')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Auto-processing</span>
                          <p>Process documents immediately after upload</p>
                        </div>
                        <button
                          className={`toggle-switch ${documentPrefs.autoProcessing ? 'active' : ''}`}
                          onClick={() => handleDocumentPrefToggle('autoProcessing')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Smart tagging</span>
                          <p>Automatically add relevant tags to documents</p>
                        </div>
                        <button
                          className={`toggle-switch ${documentPrefs.smartTagging ? 'active' : ''}`}
                          onClick={() => handleDocumentPrefToggle('smartTagging')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Duplicate detection</span>
                          <p>Detect and flag potential duplicate documents</p>
                        </div>
                        <button
                          className={`toggle-switch ${documentPrefs.duplicateDetection ? 'active' : ''}`}
                          onClick={() => handleDocumentPrefToggle('duplicateDetection')}
                        >
                          <span></span>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="settings-section">
                    <h3>Default Export Format</h3>
                    <div className="radio-group">
                      <label>
                        <input 
                          type="radio" 
                          name="exportFormat" 
                          checked={documentPrefs.defaultExportFormat === 'PDF'}
                          onChange={() => handleExportFormatChange('PDF')}
                        />
                        PDF
                      </label>
                      <label>
                        <input 
                          type="radio" 
                          name="exportFormat" 
                          checked={documentPrefs.defaultExportFormat === 'CSV'}
                          onChange={() => handleExportFormatChange('CSV')}
                        />
                        CSV
                      </label>
                      <label>
                        <input 
                          type="radio" 
                          name="exportFormat" 
                          checked={documentPrefs.defaultExportFormat === 'JSON'}
                          onChange={() => handleExportFormatChange('JSON')}
                        />
                        JSON
                      </label>
                      <label>
                        <input 
                          type="radio" 
                          name="exportFormat" 
                          checked={documentPrefs.defaultExportFormat === 'DOCX'}
                          onChange={() => handleExportFormatChange('DOCX')}
                        />
                        DOCX
                      </label>
                    </div>
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
                    <div className="toggle-list">
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Document processed</span>
                          <p>Get notified when document processing is complete</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.emailNotifications.documentProcessed ? 'active' : ''}`}
                          onClick={() => handleEmailNotificationToggle('documentProcessed')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>AI recommendations</span>
                          <p>Receive AI-powered insights and suggestions</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.emailNotifications.aiRecommendations ? 'active' : ''}`}
                          onClick={() => handleEmailNotificationToggle('aiRecommendations')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Contract deadlines</span>
                          <p>Important deadline reminders for contracts</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.emailNotifications.contractDeadlines ? 'active' : ''}`}
                          onClick={() => handleEmailNotificationToggle('contractDeadlines')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Weekly digest</span>
                          <p>Summary of your document activity and insights</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.emailNotifications.weeklyDigest ? 'active' : ''}`}
                          onClick={() => handleEmailNotificationToggle('weeklyDigest')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Security alerts</span>
                          <p>Important security and account notifications</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.emailNotifications.securityAlerts ? 'active' : ''}`}
                          onClick={() => handleEmailNotificationToggle('securityAlerts')}
                        >
                          <span></span>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="settings-section">
                    <h3>Push Notifications</h3>
                    <div className="toggle-list">
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Document uploaded</span>
                          <p>Instant notification when upload is successful</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.pushNotifications.documentUploaded ? 'active' : ''}`}
                          onClick={() => handlePushNotificationToggle('documentUploaded')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Processing complete</span>
                          <p>Real-time updates when processing finishes</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.pushNotifications.processingComplete ? 'active' : ''}`}
                          onClick={() => handlePushNotificationToggle('processingComplete')}
                        >
                          <span></span>
                        </button>
                      </div>
                      <div className="toggle-item">
                        <div className="toggle-info">
                          <span>Error alerts</span>
                          <p>Immediate notification of processing errors</p>
                        </div>
                        <button
                          className={`toggle-switch ${notificationPrefs.pushNotifications.errorAlerts ? 'active' : ''}`}
                          onClick={() => handlePushNotificationToggle('errorAlerts')}
                        >
                          <span></span>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="settings-section">
                    <h3>Notification Frequency</h3>
                    <div className="radio-group">
                      <label>
                        <input 
                          type="radio" 
                          name="frequency" 
                          checked={notificationPrefs.frequency === 'immediate'}
                          onChange={() => handleFrequencyChange('immediate')}
                        />
                        Immediate
                      </label>
                      <label>
                        <input 
                          type="radio" 
                          name="frequency" 
                          checked={notificationPrefs.frequency === 'daily'}
                          onChange={() => handleFrequencyChange('daily')}
                        />
                        Daily digest
                      </label>
                      <label>
                        <input 
                          type="radio" 
                          name="frequency" 
                          checked={notificationPrefs.frequency === 'weekly'}
                          onChange={() => handleFrequencyChange('weekly')}
                        />
                        Weekly digest
                      </label>
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