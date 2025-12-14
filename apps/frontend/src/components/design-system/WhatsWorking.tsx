/**
 * WhatsWorking Component
 * 
 * Shows coping strategies that actually help THIS user.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import './WhatsWorking.css';

export interface WhatsWorkingProps {
  strategies: Array<{
    name: string;
    effectiveness: number; // 0-1
    evidence: string;
  }>;
  maxItems?: number;
  showEvidence?: boolean;
}

export const WhatsWorking: React.FC<WhatsWorkingProps> = ({
  strategies,
  maxItems = 5,
  showEvidence = true,
}) => {
  // Filter strategies with effectiveness > 0.6 and sort by effectiveness
  const effectiveStrategies = strategies
    .filter(s => s.effectiveness > 0.6)
    .sort((a, b) => b.effectiveness - a.effectiveness)
    .slice(0, maxItems);

  // Don't render if no effective strategies
  if (effectiveStrategies.length === 0) {
    return null;
  }

  const formatEffectiveness = (effectiveness: number): string => {
    return `${Math.round(effectiveness * 100)}%`;
  };

  return (
    <div className="whats-working">
      <div className="whats-working__header">
        <span className="whats-working__icon">🌱</span>
        <h3 className="whats-working__title">What's Working for You</h3>
      </div>

      <div className="whats-working__content">
        <p className="whats-working__intro">
          These help you (we can tell from your voice):
        </p>

        <ul className="whats-working__strategies">
          {effectiveStrategies.map((strategy, index) => (
            <li key={index} className="whats-working__strategy">
              <div className="whats-working__strategy-header">
                <CheckCircle2 className="whats-working__check-icon" />
                <span className="whats-working__strategy-name">{strategy.name}</span>
              </div>
              {showEvidence && (
                <div className="whats-working__strategy-evidence">
                  <span className="whats-working__arrow">→</span>
                  <span className="whats-working__evidence-text">{strategy.evidence}</span>
                </div>
              )}
              <div className="whats-working__effectiveness-bar">
                <div
                  className="whats-working__effectiveness-fill"
                  style={{ width: `${strategy.effectiveness * 100}%` }}
                />
                <span className="whats-working__effectiveness-label">
                  {formatEffectiveness(strategy.effectiveness)} effective
                </span>
              </div>
            </li>
          ))}
        </ul>

        <p className="whats-working__footer">
          Keep doing what works for YOU.
        </p>
      </div>
    </div>
  );
};

export default WhatsWorking;

