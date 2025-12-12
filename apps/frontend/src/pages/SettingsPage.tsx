import React, { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { Moon, Sun, Globe, Bell, Shield, Trash2, Save } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './SettingsPage.css';

const SettingsPage: React.FC = () => {
  const { theme, setTheme, actualTheme } = useTheme();
  const { user } = useAuth();
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    reminders: true,
  });
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    // TODO: Save settings to backend
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsSaving(false);
    toast.success('Settings saved successfully');
  };

  const handleDeleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      toast.error('Account deletion not yet implemented');
      // TODO: Implement account deletion
    }
  };

  return (
    <div className="settings-page">
      <h1 className="settings-title">Settings</h1>

      <div className="settings-sections">
        <div className="settings-section">
          <h2 className="section-title">
            <Globe className="w-5 h-5" />
            Appearance & Language
          </h2>
          <div className="settings-content">
            <div className="setting-item">
              <label className="setting-label">Theme</label>
              <div className="theme-options">
                <button
                  onClick={() => setTheme('light')}
                  className={`theme-option ${theme === 'light' ? 'active' : ''}`}
                >
                  <Sun className="w-5 h-5" />
                  Light
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
                >
                  <Moon className="w-5 h-5" />
                  Dark
                </button>
                <button
                  onClick={() => setTheme('system')}
                  className={`theme-option ${theme === 'system' ? 'active' : ''}`}
                >
                  <Globe className="w-5 h-5" />
                  System
                </button>
              </div>
            </div>

            <div className="setting-item">
              <label className="setting-label" htmlFor="language">
                Language
              </label>
              <select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="setting-select"
              >
                <option value="en">English</option>
                <option value="sw">Swahili</option>
              </select>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2 className="section-title">
            <Bell className="w-5 h-5" />
            Notifications
          </h2>
          <div className="settings-content">
            <div className="setting-item">
              <label className="setting-toggle">
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                  className="toggle-input"
                />
                <span className="toggle-label">Email Notifications</span>
              </label>
              <p className="setting-description">
                Receive updates and reminders via email
              </p>
            </div>

            <div className="setting-item">
              <label className="setting-toggle">
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={(e) => setNotifications({ ...notifications, push: e.target.checked })}
                  className="toggle-input"
                />
                <span className="toggle-label">Push Notifications</span>
              </label>
              <p className="setting-description">
                Receive real-time notifications in your browser
              </p>
            </div>

            <div className="setting-item">
              <label className="setting-toggle">
                <input
                  type="checkbox"
                  checked={notifications.reminders}
                  onChange={(e) => setNotifications({ ...notifications, reminders: e.target.checked })}
                  className="toggle-input"
                />
                <span className="toggle-label">Reminders</span>
              </label>
              <p className="setting-description">
                Get reminders for your mental health check-ins
              </p>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <h2 className="section-title">
            <Shield className="w-5 h-5" />
            Privacy & Security
          </h2>
          <div className="settings-content">
            <div className="setting-item">
              <label className="setting-label">Privacy Mode</label>
              <p className="setting-description">
                {user?.isAnonymous
                  ? 'You are currently using anonymous mode. Your data is not linked to your identity.'
                  : 'You are using identified mode. Some features may require your identity.'}
              </p>
            </div>

            <div className="setting-item">
              <a href="/consent" className="consent-link">
                Manage Consent Preferences
              </a>
              <p className="setting-description">
                Control what data we collect and how we use it
              </p>
            </div>
          </div>
        </div>

        <div className="settings-section danger-zone">
          <h2 className="section-title">
            <Trash2 className="w-5 h-5" />
            Danger Zone
          </h2>
          <div className="settings-content">
            <div className="setting-item">
              <button onClick={handleDeleteAccount} className="danger-button">
                <Trash2 className="w-5 h-5" />
                Delete Account
              </button>
              <p className="setting-description danger-text">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
            </div>
          </div>
        </div>

        <div className="settings-actions">
          <button onClick={handleSave} disabled={isSaving} className="save-button">
            <Save className="w-5 h-5" />
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;

