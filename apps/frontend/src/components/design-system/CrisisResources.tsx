/**
 * CrisisResources Component
 * 
 * Adaptive crisis resources that appear/disappear based on risk.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import { Phone, MessageCircle, ExternalLink } from 'lucide-react';
import './CrisisResources.css';

export interface CrisisResourcesProps {
  prominence: 'hidden' | 'sidebar' | 'card' | 'top' | 'modal';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  localContext: 'kenya' | 'uganda' | 'tanzania' | 'rwanda' | 'global';
  showCounselor: boolean;
  oneClickConnect: boolean;
  onConnectCounselor?: () => void;
  onClose?: () => void;
}

const CRISIS_NUMBERS: Record<string, Record<string, string>> = {
  kenya: {
    emergency: '999',
    mentalHealth: '+254 20 272 3477',
    suicide: '+254 722 178 177',
  },
  uganda: {
    emergency: '999',
    mentalHealth: '+256 414 234 567',
    suicide: '+256 800 100 100',
  },
  tanzania: {
    emergency: '112',
    mentalHealth: '+255 22 215 1234',
    suicide: '+255 756 123 456',
  },
  rwanda: {
    emergency: '112',
    mentalHealth: '+250 788 123 456',
    suicide: '+250 788 123 456',
  },
  global: {
    emergency: '112',
    mentalHealth: 'International helpline',
    suicide: 'International helpline',
  },
};

export const CrisisResources: React.FC<CrisisResourcesProps> = ({
  prominence,
  urgency,
  localContext,
  showCounselor,
  oneClickConnect,
  onConnectCounselor,
  onClose,
}) => {
  if (prominence === 'hidden') {
    return null;
  }

  const numbers = CRISIS_NUMBERS[localContext] || CRISIS_NUMBERS.global;

  const CrisisContent = () => (
    <div className={`crisis-resources crisis-resources--${urgency}`}>
      <div className="crisis-resources__header">
        <span className="crisis-resources__icon">🆘</span>
        <h3 className="crisis-resources__title">We're Here to Support You</h3>
        {onClose && prominence === 'modal' && (
          <button className="crisis-resources__close" onClick={onClose}>
            ×
          </button>
        )}
      </div>

      <div className="crisis-resources__content">
        {urgency === 'critical' && (
          <div className="crisis-resources__alert">
            <p className="crisis-resources__alert-text">
              If you're in immediate danger, please call emergency services now.
            </p>
            <a
              href={`tel:${numbers.emergency}`}
              className="crisis-resources__emergency-button"
            >
              <Phone className="crisis-resources__button-icon" />
              Call {numbers.emergency}
            </a>
          </div>
        )}

        {showCounselor && (
          <div className="crisis-resources__counselor">
            <h4 className="crisis-resources__section-title">Connect with a Counselor</h4>
            {oneClickConnect ? (
              <button
                className="crisis-resources__connect-button"
                onClick={onConnectCounselor}
              >
                <MessageCircle className="crisis-resources__button-icon" />
                Connect Now
              </button>
            ) : (
              <p className="crisis-resources__counselor-text">
                Our counselors are available 24/7. Click to connect.
              </p>
            )}
          </div>
        )}

        <div className="crisis-resources__helplines">
          <h4 className="crisis-resources__section-title">Crisis Helplines</h4>
          <div className="crisis-resources__helpline-list">
            <a href={`tel:${numbers.mentalHealth}`} className="crisis-resources__helpline">
              <Phone className="crisis-resources__helpline-icon" />
              <div>
                <span className="crisis-resources__helpline-label">Mental Health Support</span>
                <span className="crisis-resources__helpline-number">{numbers.mentalHealth}</span>
              </div>
            </a>
            <a href={`tel:${numbers.suicide}`} className="crisis-resources__helpline">
              <Phone className="crisis-resources__helpline-icon" />
              <div>
                <span className="crisis-resources__helpline-label">Suicide Prevention</span>
                <span className="crisis-resources__helpline-number">{numbers.suicide}</span>
              </div>
            </a>
          </div>
        </div>

        <div className="crisis-resources__resources">
          <h4 className="crisis-resources__section-title">Additional Resources</h4>
          <ul className="crisis-resources__resource-list">
            <li>
              <a href="#" className="crisis-resources__resource-link">
                Safety Planning Guide
                <ExternalLink className="crisis-resources__link-icon" />
              </a>
            </li>
            <li>
              <a href="#" className="crisis-resources__resource-link">
                Coping Strategies
                <ExternalLink className="crisis-resources__link-icon" />
              </a>
            </li>
            <li>
              <a href="#" className="crisis-resources__resource-link">
                Local Support Groups
                <ExternalLink className="crisis-resources__link-icon" />
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );

  if (prominence === 'modal') {
    return (
      <div className="crisis-resources__modal-overlay">
        <CrisisContent />
      </div>
    );
  }

  return <CrisisContent />;
};

export default CrisisResources;

