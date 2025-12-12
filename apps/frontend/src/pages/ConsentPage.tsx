import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './ConsentPage.css';

interface ConsentType {
  id: string;
  name: string;
  description: string;
  required: boolean;
  granted: boolean;
  version: string;
}

const ConsentPage: React.FC = () => {
  const { user, token } = useAuth();
  const [consents, setConsents] = useState<ConsentType[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadConsents();
  }, []);

  const loadConsents = async () => {
    try {
      // TODO: Fetch from API
      // For now, use default consents
      setConsents([
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
      ]);
    } catch (error) {
      console.error('Failed to load consents:', error);
      toast.error('Failed to load consent preferences');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleConsent = async (consentId: string) => {
    const consent = consents.find(c => c.id === consentId);
    if (!consent) return;

    if (consent.required) {
      toast.error('This consent is required and cannot be revoked');
      return;
    }

    try {
      const newGranted = !consent.granted;
      // TODO: Update via API
      setConsents(consents.map(c =>
        c.id === consentId ? { ...c, granted: newGranted } : c
      ));
      toast.success(`Consent ${newGranted ? 'granted' : 'revoked'} successfully`);
    } catch (error) {
      console.error('Failed to update consent:', error);
      toast.error('Failed to update consent');
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

      <div className="consent-footer">
        <a href="/settings" className="back-link">
          ← Back to Settings
        </a>
      </div>
    </div>
  );
};

export default ConsentPage;

