import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Calendar, Shield, Download, MessageSquare, Activity, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { exportUserData, getSessionHistory, getVoiceBaseline, type ConversationSession, type VoiceBaseline } from '../utils/api';
import { ProgressCelebration, WhatsWorking, GentleObservations, PersonalizedResources, EmotionTimeline } from '../components/design-system';
import './ProfilePage.css';

const ProfilePage: React.FC = () => {
  const { user, updateUser, token } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [baseline, setBaseline] = useState<VoiceBaseline | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isLoadingBaseline, setIsLoadingBaseline] = useState(true);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    if (user?.id) {
      loadSessionHistory();
      loadVoiceBaseline();
    }
  }, [user?.id, token]);

  const loadSessionHistory = async () => {
    if (!user?.id || !token) return;
    try {
      setIsLoadingSessions(true);
      const sessionData = await getSessionHistory(token, user.id);
      setSessions(sessionData);
    } catch (error) {
      console.error('Failed to load session history:', error);
      // Don't show error toast for 404s (endpoint might not exist yet)
      if (error instanceof Error && !error.message.includes('404')) {
        toast.error('Failed to load session history');
      }
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const loadVoiceBaseline = async () => {
    if (!user?.id || !token) return;
    try {
      setIsLoadingBaseline(true);
      const baselineData = await getVoiceBaseline(token, user.id);
      setBaseline(baselineData);
    } catch (error) {
      console.error('Failed to load voice baseline:', error);
      // Don't show error toast for 404s (endpoint might not exist yet)
      if (error instanceof Error && !error.message.includes('404')) {
        toast.error('Failed to load voice baseline');
      }
    } finally {
      setIsLoadingBaseline(false);
    }
  };

  const handleSave = () => {
    updateUser({ name });
    setIsEditing(false);
    toast.success('Profile updated successfully');
  };

  const handleExportData = async () => {
    if (!user?.id || !token) {
      toast.error('Unable to export data');
      return;
    }

    setIsExporting(true);
    try {
      await exportUserData(token, {
        user_id: user.id,
        format: 'json',
        encrypt: true,
        include_conversations: true,
        include_emotions: true,
        include_consents: true,
        include_baselines: true,
        include_sessions: true,
      });
      toast.success('Data export started. You will receive an email when ready.');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to start data export');
    } finally {
      setIsExporting(false);
    }
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
            <button 
              onClick={handleExportData} 
              className="data-button"
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  <span>Export My Data</span>
                </>
              )}
            </button>
            <p className="data-description">
              Download all your conversation data, emotion history, and profile information
            </p>
          </div>
        </div>

        <div className="profile-section">
          <h2 className="section-title">
            <MessageSquare className="w-5 h-5 inline mr-2" />
            Session History
          </h2>
          {isLoadingSessions ? (
            <div className="loading-state">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading sessions...</span>
            </div>
          ) : sessions.length === 0 ? (
            <div className="empty-state">
              <MessageSquare className="w-8 h-8" />
              <p>No conversation sessions yet</p>
            </div>
          ) : (
            <div className="sessions-list">
              {sessions.slice(0, 10).map((session) => (
                <div key={session.session_id} className="session-item">
                  <div className="session-header">
                    <span className="session-date">
                      {new Date(session.started_at).toLocaleDateString()}
                    </span>
                    {session.risk_level && session.risk_level !== 'low' && (
                      <span className="crisis-badge">Risk: {session.risk_level}</span>
                    )}
                  </div>
                  <div className="session-details">
                    <span className="session-time">
                      {new Date(session.started_at).toLocaleTimeString()}
                      {session.ended_at && ` - ${new Date(session.ended_at).toLocaleTimeString()}`}
                    </span>
                    {session.message_count && (
                      <span className="session-messages">{session.message_count} messages</span>
                    )}
                  </div>
                  {session.primary_emotion && (
                    <div className="session-emotion">
                      <Activity className="w-4 h-4" />
                      <span>Emotion: {session.primary_emotion}</span>
                      {session.risk_level && <span> | Risk: {session.risk_level}</span>}
                    </div>
                  )}
                </div>
              ))}
              {sessions.length > 10 && (
                <p className="more-sessions">And {sessions.length - 10} more sessions...</p>
              )}
            </div>
          )}
        </div>

        {/* Design System Components */}
        <div className="profile-insights">
          <ProgressCelebration
            visibility={baseline && baseline.deviation_history && baseline.deviation_history.length > 0 ? 'shown' : 'hidden'}
            metrics={[
              { label: "Voice stability improved", improvement: 0.15 },
              { label: "Emotional consistency increased", improvement: 0.22 }
            ]}
            tone="warm"
            timeframe="the last 2 weeks"
          />

          <WhatsWorking
            strategies={[
              {
                name: "Breathing exercises",
                effectiveness: 0.8,
                evidence: "Your voice calms 80% of the time after"
              },
              {
                name: "Morning walks",
                effectiveness: 0.7,
                evidence: "You sound lighter when you mention them"
              }
            ]}
            maxItems={3}
            showEvidence={true}
          />

          <GentleObservations
            observations={[
              {
                type: "pattern",
                message: "You've been opening up more each session. That takes courage. We see it."
              },
              {
                type: "progress",
                message: "Your voice has more energy in the mornings (5 days straight)"
              }
            ]}
            tone="validating"
            maxItems={3}
          />

          <PersonalizedResources
            resources={[
              {
                id: "1",
                title: "Managing Family Expectations",
                type: "article",
                reason: "We noticed family is a trigger for you",
                url: "#",
                location: "East African Context"
              },
              {
                id: "2",
                title: "Understanding Emotional Exhaustion vs Physical Tiredness",
                type: "guide",
                reason: "You often say 'tired'—this explores what that really means",
                url: "#"
              }
            ]}
            filters={{
              mentalHealthNeeds: ["depression", "anxiety"],
              culturalContext: "kenya",
              triggers: ["family"],
              coping: ["breathing", "nature"]
            }}
            maxItems={3}
            showReason={true}
          />

          {sessions.length > 0 && (
            <EmotionTimeline
              timespan="30day"
              showPatterns={true}
              showTriggers={false}
              showCoping={false}
              highlightDissonance={true}
              style="detailed"
              emotionData={sessions.slice(0, 7).map(s => ({
                date: s.started_at,
                emotion: s.primary_emotion || "neutral",
                confidence: 0.5
              }))}
            />
          )}
        </div>

        <div className="profile-section">
          <h2 className="section-title">
            <Activity className="w-5 h-5 inline mr-2" />
            Voice Baseline
          </h2>
          {isLoadingBaseline ? (
            <div className="loading-state">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading baseline...</span>
            </div>
          ) : baseline ? (
            <div className="baseline-details">
              <div className="baseline-header">
                <p className="baseline-text">
                  Your personal voice fingerprint helps us detect changes in your emotional state
                </p>
                <div className="baseline-status">
                  <span className={`status-badge ${baseline.voice_fingerprint ? 'active' : ''}`}>
                    {baseline.voice_fingerprint ? 'Active' : 'Not Available'}
                  </span>
                </div>
              </div>
              {baseline.voice_fingerprint?.features && (
                <div className="baseline-metrics">
                  <h3 className="metrics-title">Baseline Metrics</h3>
                  <div className="metrics-grid">
                    {baseline.voice_fingerprint.features.pitch_mean !== undefined && (
                      <div className="metric-item">
                        <span className="metric-label">Pitch Mean</span>
                        <span className="metric-value">{baseline.voice_fingerprint.features.pitch_mean.toFixed(2)} Hz</span>
                      </div>
                    )}
                    {baseline.voice_fingerprint.features.energy_mean !== undefined && (
                      <div className="metric-item">
                        <span className="metric-label">Energy Mean</span>
                        <span className="metric-value">{baseline.voice_fingerprint.features.energy_mean.toFixed(2)}</span>
                      </div>
                    )}
                    {baseline.voice_fingerprint.features.speech_rate !== undefined && (
                      <div className="metric-item">
                        <span className="metric-label">Speaking Rate</span>
                        <span className="metric-value">{baseline.voice_fingerprint.features.speech_rate.toFixed(2)} wpm</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {baseline.voice_fingerprint?.calculated_at && (
                <p className="baseline-updated">
                  Last updated: {new Date(baseline.voice_fingerprint.calculated_at).toLocaleString()}
                </p>
              )}
              {baseline.deviation_history && baseline.deviation_history.length > 0 && (
                <div className="deviation-history">
                  <h3 className="metrics-title">Recent Deviations</h3>
                  <div className="deviations-list">
                    {baseline.deviation_history.slice(0, 5).map((deviation: any, index: number) => (
                      <div key={index} className="deviation-item">
                        <span className="deviation-date">
                          {new Date(deviation.timestamp).toLocaleDateString()}
                        </span>
                        <span className="deviation-score">
                          Score: {deviation.deviation_score.toFixed(2)}
                        </span>
                        <span className="deviation-emotion">{deviation.detected_emotion}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <AlertCircle className="w-8 h-8" />
              <p>No voice baseline established yet. Start a conversation to create your baseline.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

