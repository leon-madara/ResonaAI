/**
 * GentleObservations Component
 * 
 * Validates what the system detects without judgment.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import './GentleObservations.css';

export interface GentleObservationsProps {
  observations: Array<{
    type: 'trigger' | 'deflection' | 'pattern' | 'progress';
    message: string;
  }>;
  tone: 'validating' | 'curious' | 'concerned';
  maxItems?: number;
}

const OBSERVATION_ICONS = {
  trigger: '🎯',
  deflection: '💭',
  pattern: '📊',
  progress: '🌟',
};

const OBSERVATION_COLORS = {
  trigger: '#f59e0b',
  deflection: '#3b82f6',
  pattern: '#8b5cf6',
  progress: '#10b981',
};

export const GentleObservations: React.FC<GentleObservationsProps> = ({
  observations,
  tone,
  maxItems = 3,
}) => {
  // Limit to maxItems
  const displayedObservations = observations.slice(0, maxItems);

  if (displayedObservations.length === 0) {
    return null;
  }

  const getTitle = () => {
    switch (tone) {
      case 'validating':
        return 'Gentle Observations (Not Judgments)';
      case 'curious':
        return 'What We Notice';
      case 'concerned':
        return 'Observations We Want to Share';
      default:
        return 'Gentle Observations';
    }
  };

  return (
    <div className={`gentle-observations gentle-observations--${tone}`}>
      <div className="gentle-observations__header">
        <span className="gentle-observations__icon">💭</span>
        <h3 className="gentle-observations__title">{getTitle()}</h3>
      </div>

      <ul className="gentle-observations__list">
        {displayedObservations.map((observation, index) => (
          <li
            key={index}
            className={`gentle-observations__item gentle-observations__item--${observation.type}`}
          >
            <div className="gentle-observations__item-header">
              <span className="gentle-observations__item-icon">
                {OBSERVATION_ICONS[observation.type]}
              </span>
              <span className="gentle-observations__item-type">
                {observation.type.charAt(0).toUpperCase() + observation.type.slice(1)}
              </span>
            </div>
            <p className="gentle-observations__item-message">{observation.message}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GentleObservations;

