import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Calendar, Shield, Download } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './ProfilePage.css';

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');

  const handleSave = () => {
    updateUser({ name });
    setIsEditing(false);
    toast.success('Profile updated successfully');
  };

  const handleExportData = () => {
    toast.success('Data export started. You will receive an email when ready.');
    // TODO: Implement data export
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar">
          {user.email.charAt(0).toUpperCase()}
        </div>
        <h1 className="profile-name">
          {user.name || user.email.split('@')[0]}
        </h1>
        <p className="profile-email">{user.email}</p>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h2 className="section-title">Personal Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <Mail className="w-5 h-5" />
              <div>
                <label className="info-label">Email</label>
                <p className="info-value">{user.email}</p>
              </div>
            </div>
            <div className="info-item">
              <User className="w-5 h-5" />
              <div>
                <label className="info-label">Name</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="info-input"
                    placeholder="Enter your name"
                  />
                ) : (
                  <p className="info-value">{user.name || 'Not set'}</p>
                )}
              </div>
            </div>
            <div className="info-item">
              <Calendar className="w-5 h-5" />
              <div>
                <label className="info-label">Member Since</label>
                <p className="info-value">
                  {new Date(user.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="info-item">
              <Shield className="w-5 h-5" />
              <div>
                <label className="info-label">Privacy Mode</label>
                <p className="info-value">
                  {user.isAnonymous ? 'Anonymous' : 'Identified'}
                </p>
              </div>
            </div>
          </div>
          <div className="profile-actions">
            {isEditing ? (
              <>
                <button onClick={handleSave} className="btn-primary">
                  Save Changes
                </button>
                <button onClick={() => setIsEditing(false)} className="btn-secondary">
                  Cancel
                </button>
              </>
            ) : (
              <button onClick={() => setIsEditing(true)} className="btn-primary">
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="profile-section">
          <h2 className="section-title">Data Management</h2>
          <div className="data-actions">
            <button onClick={handleExportData} className="data-button">
              <Download className="w-5 h-5" />
              <span>Export My Data</span>
            </button>
            <p className="data-description">
              Download all your conversation data, emotion history, and profile information
            </p>
          </div>
        </div>

        <div className="profile-section">
          <h2 className="section-title">Voice Baseline</h2>
          <div className="baseline-info">
            <p className="baseline-text">
              Your personal voice fingerprint helps us detect changes in your emotional state
            </p>
            <div className="baseline-status">
              <span className="status-badge">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

