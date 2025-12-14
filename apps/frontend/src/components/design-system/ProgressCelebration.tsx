/**
 * ProgressCelebration Component
 * 
 * Celebrates genuine progress (hidden when user is declining).
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import { CheckCircle2, TrendingUp } from 'lucide-react';
import './ProgressCelebration.css';

export interface ProgressCelebrationProps {
  visibility: 'shown' | 'hidden';
  metrics: Array<{
    label: string;
    improvement: number;
  }>;
  tone: 'quiet' | 'warm' | 'celebratory';
  timeframe?: string;
}

export const ProgressCelebration: React.FC<ProgressCelebrationProps> = ({
  visibility,
  metrics,
  tone,
  timeframe = 'the last 2 weeks',
}) => {
  if (visibility === 'hidden' || metrics.length === 0) {
    return null;
  }

  const getTitle = () => {
    switch (tone) {
      case 'quiet':
        return 'We See Your Progress';
      case 'warm':
        return '🌟 We See Your Progress';
      case 'celebratory':
        return '🎉 Celebrating Your Progress';
      default:
        return 'We See Your Progress';
    }
  };

  const getFooter = () => {
    switch (tone) {
      case 'quiet':
        return "These might seem small, but they're not. Healing isn't linear—and you're moving.";
      case 'warm':
        return "These changes matter. You're doing the work, and it shows.";
      case 'celebratory':
        return "You're making real progress! Keep going—you've got this.";
      default:
        return "These might seem small, but they're not. Healing isn't linear—and you're moving.";
    }
  };

  return (
    <div className={`progress-celebration progress-celebration--${tone}`}>
      <div className="progress-celebration__header">
        <TrendingUp className="progress-celebration__icon" />
        <h3 className="progress-celebration__title">{getTitle()}</h3>
      </div>

      <div className="progress-celebration__content">
        <p className="progress-celebration__timeframe">Over {timeframe}:</p>

        <ul className="progress-celebration__metrics">
          {metrics.map((metric, index) => (
            <li key={index} className="progress-celebration__metric">
              <CheckCircle2 className="progress-celebration__check-icon" />
              <span className="progress-celebration__metric-label">{metric.label}</span>
              {metric.improvement > 0 && (
                <span className="progress-celebration__metric-improvement">
                  +{Math.round(metric.improvement * 100)}%
                </span>
              )}
            </li>
          ))}
        </ul>

        <p className="progress-celebration__footer">{getFooter()}</p>
      </div>
    </div>
  );
};

export default ProgressCelebration;

