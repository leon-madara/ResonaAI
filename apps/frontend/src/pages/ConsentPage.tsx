import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, CheckCircle, XCircle, AlertCircle, FileText, Clock, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getConsents, updateConsent, revokeConsent, type ConsentRecord } from '../utils/api';
import './ConsentPage.css';

interface ConsentType {
  id: string;
  name: string;
  description: string;
  required: boolean;
  granted: boolean;
  version: string;
  grantedAt?: string;
  revokedAt?: string;
}

const ConsentPage: React.FC = () => {
  const { user, token } = useAuth();
  const [consents, setConsents] = useState<ConsentType[]>([]);
  const [consentHistory, setConsentHistory] = useState<ConsentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false);

  useEffect(() => {
    if (token) {
      loadConsents();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const loadConsents = async () => {
    if (!token) return;

    try {
      setIsLoading(true);
      const apiConsents = await getConsents(token);
      
      // Map API consents to local format
      const mappedConsents: ConsentType[] = apiConsents.map((record) => ({
        id: record.consent_type,
        name: formatConsentName(record.consent_type),
        description: getConsentDescription(record.consent_type),
        required: isRequiredConsent(record.consent_type),
        granted: record.granted,
        version: record.consent_version,
        grantedAt: record.granted_at,
        revokedAt: record.revoked_at || undefined,
      }));

      // If no consents from API, use defaults
      if (mappedConsents.length === 0) {
        setConsents(getDefaultConsents());
      } else {
        setConsents(mappedConsents);
      }

      setConsentHistory(apiConsents);
    } catch (error) {
      console.error('Failed to load consents:', error);
      // Fallback to defaults if API fails
      setConsents(getDefaultConsents());
      if (error instanceof Error && !error.message.includes('404')) {
        toast.error('Failed to load consent preferences');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getDefaultConsents = (): ConsentType[] => [
    {
      id: 'data_processing',
      name: 'Data Processing',
      description: 'Allow us to process your conversation data to provide mental health support',
      required: true,
      granted: true,
      version: '1.0',
    },
    {
      id: 'emotion_analysis',
      name: 'Emotion Analysis',
      description: 'Analyze your voice and text to detect emotional states',
      required: false,
      granted: true,
      version: '1.0',
    },
    {
      id: 'cultural_context',
      name: 'Cultural Context',
      description: 'Use cultural context to provide more relevant support',
      required: false,
      granted: false,
      version: '1.0',
    },
    {
      id: 'research_participation',
      name: 'Research Participation',
      description: 'Allow anonymized data to be used for mental health research',
      required: false,
      granted: false,
      version: '1.0',
    },
    {
      id: 'crisis_intervention',
      name: 'Crisis Intervention',
      description: 'Enable automatic crisis detection and emergency response',
      required: true,
      granted: true,
      version: '1.0',
    },
  ];

  const formatConsentName = (type: string): string => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getConsentDescription = (type: string): string => {
    const descriptions: Record<string, string> = {
      data_processing: 'Allow us to process your conversation data to provide mental health support',
      emotion_analysis: 'Analyze your voice and text to detect emotional states',
      cultural_context: 'Use cultural context to provide more relevant support',
      research_participation: 'Allow anonymized data to be used for mental health research',
      crisis_intervention: 'Enable automatic crisis detection and emergency response',
    };
    return descriptions[type] || 'Consent for data processing';
  };

  const isRequiredConsent = (type: string): boolean => {
    return ['data_processing', 'crisis_intervention'].includes(type);
  };

  const handleToggleConsent = async (consentId: string) => {
    if (!token) {
      toast.error('Please log in to manage consents');
      return;
    }

    const consent = consents.find(c => c.id === consentId);
    if (!consent) return;

    if (consent.required) {
      toast.error('This consent is required and cannot be revoked');
      return;
    }

    try {
      const newGranted = !consent.granted;
      
      if (newGranted) {
        await updateConsent(token, {
          consent_type: consentId,
          consent_version: consent.version,
          granted: true,
        });
      } else {
        await revokeConsent(token, {
          consent_type: consentId,
          consent_version: consent.version,
        });
      }

      // Reload consents to get updated data
      await loadConsents();
      toast.success(`Consent ${newGranted ? 'granted' : 'revoked'} successfully`);
    } catch (error) {
      console.error('Failed to update consent:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to update consent');
    }
  };

  if (isLoading) {
    return <div className="consent-page">Loading...</div>;
  }

  return (
    <div className="consent-page">
      <div className="consent-header">
        <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
        <h1 className="consent-title">Consent Management</h1>
        <p className="consent-subtitle">
          Control how your data is collected and used
        </p>
      </div>

      <div className="consent-info">
        <AlertCircle className="w-5 h-5" />
        <p>
          Your privacy is important to us. You can manage your consent preferences below.
          Required consents cannot be revoked as they are necessary for the service to function.
        </p>
      </div>

      <div className="consents-list">
        {consents.map((consent) => (
          <div
            key={consent.id}
            className={`consent-item ${consent.required ? 'required' : ''} ${consent.granted ? 'granted' : 'revoked'}`}
          >
            <div className="consent-content">
              <div className="consent-header-item">
                <h3 className="consent-name">{consent.name}</h3>
                {consent.required && (
                  <span className="required-badge">Required</span>
                )}
              </div>
              <p className="consent-description">{consent.description}</p>
              <p className="consent-version">Version: {consent.version}</p>
            </div>
            <div className="consent-actions">
              {consent.granted ? (
                <div className="consent-status granted">
                  <CheckCircle className="w-5 h-5" />
                  <span>Granted</span>
                </div>
              ) : (
                <div className="consent-status revoked">
                  <XCircle className="w-5 h-5" />
                  <span>Revoked</span>
                </div>
              )}
              <button
                onClick={() => handleToggleConsent(consent.id)}
                disabled={consent.required}
                className={`consent-toggle ${consent.granted ? 'active' : ''}`}
              >
                {consent.granted ? 'Revoke' : 'Grant'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="consent-actions-section">
        <button
          onClick={() => setShowPrivacyPolicy(true)}
          className="privacy-policy-button"
        >
          <FileText className="w-5 h-5" />
          View Privacy Policy
        </button>
      </div>

      {consentHistory.length > 0 && (
        <div className="consent-history-section">
          <h2 className="history-title">
            <Clock className="w-5 h-5" />
            Consent History
          </h2>
          <div className="history-timeline">
            {consentHistory
              .sort((a, b) => new Date(b.granted_at).getTime() - new Date(a.granted_at).getTime())
              .slice(0, 10)
              .map((record) => (
                <div key={record.id} className="history-item">
                  <div className="history-dot" />
                  <div className="history-content">
                    <div className="history-header">
                      <span className="history-type">{formatConsentName(record.consent_type)}</span>
                      <span className={`history-status ${record.granted ? 'granted' : 'revoked'}`}>
                        {record.granted ? (
                          <>
                            <CheckCircle className="w-4 h-4" />
                            Granted
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4" />
                            Revoked
                          </>
                        )}
                      </span>
                    </div>
                    <p className="history-date">
                      {record.granted
                        ? `Granted: ${new Date(record.granted_at).toLocaleString()}`
                        : record.revoked_at
                        ? `Revoked: ${new Date(record.revoked_at).toLocaleString()}`
                        : `Updated: ${new Date(record.granted_at).toLocaleString()}`}
                    </p>
                    <p className="history-version">Version: {record.consent_version}</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      <div className="consent-footer">
        <a href="/settings" className="back-link">
          ← Back to Settings
        </a>
      </div>

      {showPrivacyPolicy && (
        <div className="modal-overlay" onClick={() => setShowPrivacyPolicy(false)}>
          <div className="modal-content privacy-policy-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-wrapper">
                <FileText className="w-6 h-6 text-blue-600" />
                <h2 className="modal-title">Privacy Policy</h2>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowPrivacyPolicy(false)}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="modal-body privacy-policy-content">
              <h3>Data Collection and Use</h3>
              <p>
                ResonaAI collects and processes your data to provide mental health support services.
                We are committed to protecting your privacy and ensuring data security.
              </p>
              
              <h3>What We Collect</h3>
              <ul>
                <li>Conversation data and voice recordings</li>
                <li>Emotion analysis data</li>
                <li>User preferences and settings</li>
                <li>Technical information (device, browser)</li>
              </ul>

              <h3>How We Use Your Data</h3>
              <ul>
                <li>Provide personalized mental health support</li>
                <li>Detect emotional states and crisis situations</li>
                <li>Improve our services through analysis</li>
                <li>Comply with legal obligations</li>
              </ul>

              <h3>Data Security</h3>
              <p>
                All data is encrypted in transit and at rest. We use industry-standard security
                measures to protect your information.
              </p>

              <h3>Your Rights</h3>
              <ul>
                <li>Right to access your data</li>
                <li>Right to correct inaccurate data</li>
                <li>Right to delete your data</li>
                <li>Right to data portability</li>
                <li>Right to withdraw consent</li>
              </ul>

              <h3>Contact Us</h3>
              <p>
                For questions about this privacy policy or your data, please contact us at
                privacy@resonaai.com
              </p>

              <p className="policy-date">Last updated: {new Date().toLocaleDateString()}</p>
            </div>
            <div className="modal-footer">
              <button
                className="modal-button primary"
                onClick={() => setShowPrivacyPolicy(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsentPage;

