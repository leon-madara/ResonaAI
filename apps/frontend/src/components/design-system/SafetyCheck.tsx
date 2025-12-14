/**
 * SafetyCheck Component
 * 
 * Gentle check-in when risk is detected.
 * Part of the ResonaAI Design System.
 */

import React, { useState } from 'react';
import './SafetyCheck.css';

export interface SafetyCheckProps {
  tone: 'gentle' | 'direct' | 'urgent';
  context: string;
  frequency: 'once' | 'daily' | 'session';
  onResponse?: (response: 'yes' | 'no' | 'unsure' | 'skip') => void;
  showSkip?: boolean;
}

export const SafetyCheck: React.FC<SafetyCheckProps> = ({
  tone,
  context,
  frequency,
  onResponse,
  showSkip = false,
}) => {
  const [selectedResponse, setSelectedResponse] = useState<'yes' | 'no' | 'unsure' | 'skip' | null>(null);

  const handleResponse = (response: 'yes' | 'no' | 'unsure' | 'skip') => {
    setSelectedResponse(response);
    onResponse?.(response);
  };

  const getTitle = () => {
    switch (tone) {
      case 'gentle':
        return 'Quick Check-In';
      case 'direct':
        return 'We Need to Check In';
      case 'urgent':
        return 'Important Check-In';
      default:
        return 'Quick Check-In';
    }
  };

  const getSubtext = () => {
    if (tone === 'gentle' && frequency === 'once') {
      return "Your answer helps us support you better. We won't judge—we just want you safe.";
    }
    if (tone === 'direct') {
      return "We're concerned and want to make sure you're okay.";
    }
    if (tone === 'urgent') {
      return "We're here to help. Please let us know how you're doing.";
    }
    return "Your answer helps us support you better.";
  };

  return (
    <div className={`safety-check safety-check--${tone}`}>
      <div className="safety-check__header">
        <h3 className="safety-check__title">{getTitle()}</h3>
      </div>

      <div className="safety-check__content">
        <p className="safety-check__context">{context}</p>

        <div className="safety-check__question">
          <p className="safety-check__question-text">Are you thinking about hurting yourself?</p>
        </div>

        <div className="safety-check__responses">
          <button
            className={`safety-check__button safety-check__button--yes ${
              selectedResponse === 'yes' ? 'safety-check__button--selected' : ''
            }`}
            onClick={() => handleResponse('yes')}
          >
            Yes
          </button>
          <button
            className={`safety-check__button safety-check__button--no ${
              selectedResponse === 'no' ? 'safety-check__button--selected' : ''
            }`}
            onClick={() => handleResponse('no')}
          >
            No
          </button>
          <button
            className={`safety-check__button safety-check__button--unsure ${
              selectedResponse === 'unsure' ? 'safety-check__button--selected' : ''
            }`}
            onClick={() => handleResponse('unsure')}
          >
            I don't know
          </button>
          {showSkip && (
            <button
              className={`safety-check__button safety-check__button--skip ${
                selectedResponse === 'skip' ? 'safety-check__button--selected' : ''
              }`}
              onClick={() => handleResponse('skip')}
            >
              I don't want to answer
            </button>
          )}
        </div>

        <p className="safety-check__subtext">{getSubtext()}</p>
      </div>
    </div>
  );
};

export default SafetyCheck;

