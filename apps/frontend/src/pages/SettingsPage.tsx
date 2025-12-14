import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { Moon, Sun, Globe, Bell, Shield, Trash2, Save, AlertTriangle, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getUserSettings, saveUserSettings, requestAccountDeletion } from '../utils/api';
import './SettingsPage.css';

const SettingsPage: React.FC = () => {
  const { theme, setTheme, actualTheme } = useTheme();
  const { user, token, logout } = useAuth();
  const [language, setLanguage] = useState('en');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    reminders: true,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteReason, setDeleteReason] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadSettings();
  }, [user?.id, token]);

  const loadSettings = async () => {
    if (!user?.id || !token) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const settings = await getUserSettings(token, user.id);
      if (settings.language) setLanguage(settings.language);
      if (settings.notifications) {
        setNotifications({
          email: settings.notifications.email ?? true,
          push: settings.notifications.push ?? false,
          reminders: settings.notifications.reminders ?? true,
        });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      // Don't show error for 404 (endpoint might not exist yet)
      if (error instanceof Error && !error.message.includes('404')) {
        toast.error('Failed to load settings');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!user?.id || !token) {
      toast.error('Unable to save settings');
      return;
    }

    setIsSaving(true);
    try {
      await saveUserSettings(token, user.id, {
        language,
        theme,
        notifications,
      });
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAccount = () => {
    setShowDeleteModal(true);
  };

  const confirmDeleteAccount = async () => {
    if (!user?.id || !token) {
      toast.error('Unable to delete account');
      return;
    }

    setIsDeleting(true);
    try {
      const response = await requestAccountDeletion(token, {
        user_id: user.id,
        reason: deleteReason || 'User requested account deletion',
        immediate: false, // Use grace period
      });
      
      toast.success(
        response.scheduled_deletion_date
          ? `Account deletion scheduled. You have ${response.grace_period_days || 30} days to cancel.`
          : 'Account deletion request submitted successfully'
      );
      
      setShowDeleteModal(false);
      setDeleteReason('');
      
      // Optionally log out after a delay
      setTimeout(() => {
        logout();
      }, 3000);
    } catch (error) {
      console.error('Failed to delete account:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to delete account');
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="settings-page">
        <div className="loading-state">
          <Save className="w-6 h-6 animate-spin" />
          <span>Loading settings...</span>
        </div>
      </div>
    );
  }

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

      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => !isDeleting && setShowDeleteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-wrapper">
                <AlertTriangle className="w-6 h-6 text-red-600" />
                <h2 className="modal-title">Delete Account</h2>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-warning">
                Are you sure you want to delete your account? This action cannot be undone.
              </p>
              <p className="modal-info">
                Your account will be scheduled for deletion with a grace period. You can cancel
                the deletion request within the grace period if you change your mind.
              </p>
              <div className="modal-form-group">
                <label htmlFor="delete-reason" className="modal-label">
                  Reason for deletion (optional)
                </label>
                <textarea
                  id="delete-reason"
                  value={deleteReason}
                  onChange={(e) => setDeleteReason(e.target.value)}
                  className="modal-textarea"
                  placeholder="Help us improve by sharing why you're leaving..."
                  rows={3}
                  disabled={isDeleting}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="modal-button secondary"
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                className="modal-button danger"
                onClick={confirmDeleteAccount}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <>
                    <Save className="w-4 h-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    Delete Account
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;

