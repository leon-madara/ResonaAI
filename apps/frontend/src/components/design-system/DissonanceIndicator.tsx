/**
 * DissonanceIndicator Component
 * 
 * Shows the gap between what user says and what voice reveals.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import './DissonanceIndicator.css';

export interface DissonanceIndicatorProps {
  visibility: 'always' | 'when_detected' | 'never';
  showExplanation: boolean;
  statedEmotion: string;
  voiceEmotion: string;
  dissonanceScore: number; // 0-1
  interpretation: string;
  onTellMore?: () => void;
  onDismiss?: () => void;
}

export const DissonanceIndicator: React.FC<DissonanceIndicatorProps> = ({
  visibility,
  showExplanation,
  statedEmotion,
  voiceEmotion,
  dissonanceScore,
  interpretation,
  onTellMore,
  onDismiss,
}) => {
  // Don't render if visibility is 'never' or 'when_detected' but score is low
  if (visibility === 'never') {
    return null;
  }

  if (visibility === 'when_detected' && dissonanceScore < 0.3) {
    return null;
  }

  const getDissonanceLevel = (score: number): 'low' | 'medium' | 'high' => {
    if (score < 0.4) return 'low';
    if (score < 0.7) return 'medium';
    return 'high';
  };

  const dissonanceLevel = getDissonanceLevel(dissonanceScore);
  const scorePercentage = Math.round(dissonanceScore * 100);

  return (
    <div className={`dissonance-indicator dissonance-indicator--${dissonanceLevel}`}>
      <div className="dissonance-indicator__header">
        <span className="dissonance-indicator__icon">🔍</span>
        <h3 className="dissonance-indicator__title">We Notice a Gap</h3>
      </div>

      <div className="dissonance-indicator__content">
        <div className="dissonance-indicator__comparison">
          <div className="dissonance-indicator__comparison-item">
            <span className="dissonance-indicator__label">Your Words:</span>
            <span className="dissonance-indicator__value">"{statedEmotion}"</span>
          </div>
          <div className="dissonance-indicator__comparison-item">
            <span className="dissonance-indicator__label">Your Voice:</span>
            <span className="dissonance-indicator__value">{voiceEmotion}</span>
          </div>
        </div>

        <div className="dissonance-indicator__score">
          <div className="dissonance-indicator__score-bar">
            <div
              className={`dissonance-indicator__score-fill dissonance-indicator__score-fill--${dissonanceLevel}`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
          <span className="dissonance-indicator__score-text">
            {dissonanceLevel === 'high' ? 'High' : dissonanceLevel === 'medium' ? 'Medium' : 'Low'} Dissonance ({scorePercentage}%)
          </span>
        </div>

        {showExplanation && interpretation && (
          <div className="dissonance-indicator__interpretation">
            <p className="dissonance-indicator__interpretation-title">What this might mean:</p>
            <p className="dissonance-indicator__interpretation-text">{interpretation}</p>
          </div>
        )}

        <div className="dissonance-indicator__actions">
          {onTellMore && (
            <button
              className="dissonance-indicator__button dissonance-indicator__button--primary"
              onClick={onTellMore}
            >
              Tell me more
            </button>
          )}
          {onDismiss && (
            <button
              className="dissonance-indicator__button dissonance-indicator__button--secondary"
              onClick={onDismiss}
            >
              I'm okay, really
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DissonanceIndicator;

