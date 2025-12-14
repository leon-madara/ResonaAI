import React, { useState, useEffect } from 'react';
import { Phone, MessageCircle, Globe, Heart, AlertTriangle, Shield, X, Save, Plus, Trash2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { getApiBaseUrl, getAuthHeader } from '../utils/api';
import { CrisisResources, SafetyCheck } from '../components/design-system';
import './CrisisPage.css';

interface SafetyPlan {
  triggers: string[];
  copingStrategies: string[];
  supportContacts: string[];
  warningSigns: string[];
  lastUpdated: string;
}

const CrisisPage: React.FC = () => {
  const { token } = useAuth();
  const [showSafetyPlanModal, setShowSafetyPlanModal] = useState(false);
  const [safetyPlan, setSafetyPlan] = useState<SafetyPlan>({
    triggers: [],
    copingStrategies: [],
    supportContacts: [],
    warningSigns: [],
    lastUpdated: new Date().toISOString(),
  });
  const [newTrigger, setNewTrigger] = useState('');
  const [newStrategy, setNewStrategy] = useState('');
  const [newContact, setNewContact] = useState('');
  const [newWarningSign, setNewWarningSign] = useState('');
  const [isEscalating, setIsEscalating] = useState(false);
  const [showSafetyCheck, setShowSafetyCheck] = useState(false);
  const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
  const emergencyContacts = [
    {
      name: 'Kenya Mental Health Helpline',
      phone: '+254 800 723 333',
      available: '24/7',
    },
    {
      name: 'Uganda Mental Health Helpline',
      phone: '+256 800 200 600',
      available: '24/7',
    },
    {
      name: 'Tanzania Mental Health Helpline',
      phone: '+255 800 111 222',
      available: '24/7',
    },
  ];

  useEffect(() => {
    loadSafetyPlan();
  }, []);

  const loadSafetyPlan = () => {
    const stored = localStorage.getItem('safetyPlan');
    if (stored) {
      try {
        setSafetyPlan(JSON.parse(stored));
      } catch (error) {
        console.error('Failed to load safety plan:', error);
      }
    }
  };

  const saveSafetyPlan = () => {
    const updated = {
      ...safetyPlan,
      lastUpdated: new Date().toISOString(),
    };
    localStorage.setItem('safetyPlan', JSON.stringify(updated));
    setSafetyPlan(updated);
    toast.success('Safety plan saved successfully');
    setShowSafetyPlanModal(false);
  };

  const addItem = (type: 'triggers' | 'copingStrategies' | 'supportContacts' | 'warningSigns', value: string) => {
    if (!value.trim()) return;
    setSafetyPlan((prev) => ({
      ...prev,
      [type]: [...prev[type], value.trim()],
    }));
    if (type === 'triggers') setNewTrigger('');
    if (type === 'copingStrategies') setNewStrategy('');
    if (type === 'supportContacts') setNewContact('');
    if (type === 'warningSigns') setNewWarningSign('');
  };

  const removeItem = (type: 'triggers' | 'copingStrategies' | 'supportContacts' | 'warningSigns', index: number) => {
    setSafetyPlan((prev) => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index),
    }));
  };

  const handleEscalate = async () => {
    if (!token) {
      toast.error('Please log in to escalate');
      return;
    }

    setIsEscalating(true);
    try {
      const apiBaseUrl = getApiBaseUrl();
      const response = await fetch(`${apiBaseUrl}/crisis-detection/escalate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(token),
        },
        body: JSON.stringify({
          reason: 'User requested escalation',
          urgency: 'high',
        }),
      });

      if (!response.ok) {
        throw new Error('Escalation failed');
      }

      toast.success('Crisis escalation submitted. A counselor will contact you soon.');
    } catch (error) {
      console.error('Escalation error:', error);
      toast.error('Failed to escalate. Please call emergency services if in immediate danger.');
    } finally {
      setIsEscalating(false);
    }
  };

  const handleResourceAction = (action: string) => {
    if (action === 'Call 999') {
      window.location.href = 'tel:999';
    } else if (action === 'Text HOME to 741741') {
      window.location.href = 'sms:741741?body=HOME';
    } else if (action === 'Create Safety Plan') {
      setShowSafetyPlanModal(true);
    }
  };

  const resources = [
    {
      title: 'Immediate Help',
      description: 'If you are in immediate danger, please call emergency services',
      action: 'Call 999',
      urgent: true,
    },
    {
      title: 'Crisis Text Line',
      description: 'Text with a trained crisis counselor',
      action: 'Text HOME to 741741',
      urgent: false,
    },
    {
      title: 'Safety Planning',
      description: 'Create a safety plan for difficult moments',
      action: 'Create Safety Plan',
      urgent: false,
    },
  ];

  const handleSafetyCheckResponse = (response: 'yes' | 'no' | 'unsure' | 'skip') => {
    if (response === 'yes') {
      setRiskLevel('critical');
      toast.error('Please call emergency services immediately if you are in danger.');
    } else if (response === 'unsure') {
      setRiskLevel('high');
    }
    setShowSafetyCheck(false);
  };

  return (
    <div className="crisis-page">
      <CrisisResources
        prominence={riskLevel === 'critical' ? 'modal' : riskLevel === 'high' ? 'card' : 'sidebar'}
        urgency={riskLevel}
        localContext="kenya"
        showCounselor={true}
        oneClickConnect={riskLevel === 'critical'}
        onConnectCounselor={handleEscalate}
        onClose={() => setRiskLevel('low')}
      />

      {showSafetyCheck && (
        <div className="safety-check-container">
          <SafetyCheck
            tone={riskLevel === 'critical' ? 'urgent' : riskLevel === 'high' ? 'direct' : 'gentle'}
            context="Your voice has sounded different lately—flatter, more pauses. We want to make sure you're okay."
            frequency="once"
            onResponse={handleSafetyCheckResponse}
            showSkip={true}
          />
        </div>
      )}

      <div className="crisis-hero">
        <AlertTriangle className="w-12 h-12 text-red-600 dark:text-red-400 mb-4" />
        <h1 className="crisis-title">Crisis Support</h1>
        <p className="crisis-subtitle">
          You are not alone. Help is available 24/7.
        </p>
        <button
          onClick={() => setShowSafetyCheck(true)}
          className="safety-check-trigger"
        >
          Quick Safety Check-In
        </button>
      </div>

      <div className="crisis-content">
        <div className="crisis-section urgent">
          <h2 className="section-title">
            <Phone className="w-6 h-6" />
            Emergency Contacts
          </h2>
          <div className="contacts-list">
            {emergencyContacts.map((contact, index) => (
              <div key={index} className="contact-card">
                <div className="contact-info">
                  <h3 className="contact-name">{contact.name}</h3>
                  <p className="contact-phone">{contact.phone}</p>
                  <p className="contact-available">Available: {contact.available}</p>
                </div>
                <a
                  href={`tel:${contact.phone.replace(/\s/g, '')}`}
                  className="contact-button"
                >
                  <Phone className="w-5 h-5" />
                  Call Now
                </a>
              </div>
            ))}
          </div>
        </div>

        <div className="crisis-section">
          <h2 className="section-title">
            <Heart className="w-6 h-6" />
            Resources & Support
          </h2>
          <div className="resources-grid">
            {resources.map((resource, index) => (
              <div
                key={index}
                className={`resource-card ${resource.urgent ? 'urgent' : ''}`}
              >
                <h3 className="resource-title">{resource.title}</h3>
                <p className="resource-description">{resource.description}</p>
                <button 
                  className="resource-button"
                  onClick={() => handleResourceAction(resource.action)}
                >
                  {resource.action}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="crisis-section">
          <h2 className="section-title">
            <Shield className="w-6 h-6" />
            Escalation & Support
          </h2>
          <div className="escalation-content">
            <p className="escalation-description">
              If you need immediate professional support, you can request escalation to a human counselor.
              Our team is available 24/7 to provide assistance.
            </p>
            <button
              onClick={handleEscalate}
              disabled={isEscalating}
              className="escalation-button"
            >
              {isEscalating ? (
                <>
                  <AlertTriangle className="w-5 h-5 animate-spin" />
                  Escalating...
                </>
              ) : (
                <>
                  <AlertTriangle className="w-5 h-5" />
                  Request Counselor Support
                </>
              )}
            </button>
          </div>
        </div>

        <div className="crisis-section">
          <h2 className="section-title">
            <Globe className="w-6 h-6" />
            Additional Resources
          </h2>
          <div className="additional-resources">
            <div className="resource-item">
              <MessageCircle className="w-5 h-5" />
              <div>
                <h4>Online Support Groups</h4>
                <p>Connect with others who understand what you're going through</p>
              </div>
            </div>
            <div className="resource-item">
              <Heart className="w-5 h-5" />
              <div>
                <h4>Self-Care Resources</h4>
                <p>Tools and techniques to help you manage difficult moments</p>
              </div>
            </div>
          </div>
        </div>

        <div className="crisis-footer">
          <p className="crisis-message">
            Remember: It's okay to ask for help. Reaching out is a sign of strength, not weakness.
          </p>
        </div>
      </div>

      {showSafetyPlanModal && (
        <div className="modal-overlay" onClick={() => setShowSafetyPlanModal(false)}>
          <div className="modal-content safety-plan-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-wrapper">
                <Shield className="w-6 h-6 text-blue-600" />
                <h2 className="modal-title">Safety Plan</h2>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowSafetyPlanModal(false)}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="modal-body">
              <div className="safety-plan-section">
                <h3 className="safety-plan-section-title">Warning Signs</h3>
                <div className="safety-plan-list">
                  {safetyPlan.warningSigns.map((sign, index) => (
                    <div key={index} className="safety-plan-item">
                      <span>{sign}</span>
                      <button onClick={() => removeItem('warningSigns', index)} className="remove-button">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  <div className="safety-plan-add">
                    <input
                      type="text"
                      value={newWarningSign}
                      onChange={(e) => setNewWarningSign(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addItem('warningSigns', newWarningSign)}
                      placeholder="Add warning sign..."
                      className="safety-plan-input"
                    />
                    <button onClick={() => addItem('warningSigns', newWarningSign)} className="add-button">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="safety-plan-section">
                <h3 className="safety-plan-section-title">Triggers</h3>
                <div className="safety-plan-list">
                  {safetyPlan.triggers.map((trigger, index) => (
                    <div key={index} className="safety-plan-item">
                      <span>{trigger}</span>
                      <button onClick={() => removeItem('triggers', index)} className="remove-button">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  <div className="safety-plan-add">
                    <input
                      type="text"
                      value={newTrigger}
                      onChange={(e) => setNewTrigger(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addItem('triggers', newTrigger)}
                      placeholder="Add trigger..."
                      className="safety-plan-input"
                    />
                    <button onClick={() => addItem('triggers', newTrigger)} className="add-button">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="safety-plan-section">
                <h3 className="safety-plan-section-title">Coping Strategies</h3>
                <div className="safety-plan-list">
                  {safetyPlan.copingStrategies.map((strategy, index) => (
                    <div key={index} className="safety-plan-item">
                      <span>{strategy}</span>
                      <button onClick={() => removeItem('copingStrategies', index)} className="remove-button">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  <div className="safety-plan-add">
                    <input
                      type="text"
                      value={newStrategy}
                      onChange={(e) => setNewStrategy(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addItem('copingStrategies', newStrategy)}
                      placeholder="Add coping strategy..."
                      className="safety-plan-input"
                    />
                    <button onClick={() => addItem('copingStrategies', newStrategy)} className="add-button">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="safety-plan-section">
                <h3 className="safety-plan-section-title">Support Contacts</h3>
                <div className="safety-plan-list">
                  {safetyPlan.supportContacts.map((contact, index) => (
                    <div key={index} className="safety-plan-item">
                      <span>{contact}</span>
                      <button onClick={() => removeItem('supportContacts', index)} className="remove-button">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  <div className="safety-plan-add">
                    <input
                      type="text"
                      value={newContact}
                      onChange={(e) => setNewContact(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addItem('supportContacts', newContact)}
                      placeholder="Add support contact..."
                      className="safety-plan-input"
                    />
                    <button onClick={() => addItem('supportContacts', newContact)} className="add-button">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="modal-button secondary"
                onClick={() => setShowSafetyPlanModal(false)}
              >
                Cancel
              </button>
              <button
                className="modal-button primary"
                onClick={saveSafetyPlan}
              >
                <Save className="w-4 h-4" />
                Save Plan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CrisisPage;

