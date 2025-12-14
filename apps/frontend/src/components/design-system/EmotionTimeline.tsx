/**
 * EmotionTimeline Component
 * 
 * Shows user's emotional journey over time, with patterns highlighted.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import './EmotionTimeline.css';

export interface EmotionTimelineProps {
  timespan: '7day' | '30day' | 'session' | 'all';
  showPatterns: boolean;
  showTriggers?: boolean;
  showCoping?: boolean;
  highlightDissonance?: boolean;
  style: 'detailed' | 'simple' | 'sparkline';
  emotionData?: Array<{
    date: string;
    emotion: string;
    confidence: number;
    dissonance?: number;
  }>;
  patterns?: Array<{
    type: string;
    description: string;
    frequency: string;
  }>;
  copingStrategies?: Array<{
    strategy: string;
    effectiveness: number;
  }>;
}

const EMOTION_EMOJIS: Record<string, string> = {
  happy: '😌',
  sad: '😔',
  anxious: '😟',
  angry: '😠',
  neutral: '😐',
  fear: '😨',
  surprise: '😲',
};

export const EmotionTimeline: React.FC<EmotionTimelineProps> = ({
  timespan,
  showPatterns,
  showTriggers = false,
  showCoping = false,
  highlightDissonance = false,
  style,
  emotionData = [],
  patterns = [],
  copingStrategies = [],
}) => {
  if (style === 'sparkline') {
    return (
      <div className="emotion-timeline emotion-timeline--sparkline">
        <div className="emotion-timeline__sparkline">
          {emotionData.map((entry, index) => (
            <div
              key={index}
              className={`emotion-timeline__sparkline-dot emotion-timeline__sparkline-dot--${entry.emotion}`}
              style={{ left: `${(index / emotionData.length) * 100}%` }}
              title={`${entry.date}: ${entry.emotion}`}
            />
          ))}
        </div>
      </div>
    );
  }

  if (style === 'simple') {
    return (
      <div className="emotion-timeline emotion-timeline--simple">
        <div className="emotion-timeline__header">
          <h3>Your Emotional Journey</h3>
        </div>
        <div className="emotion-timeline__days">
          {emotionData.map((entry, index) => (
            <div key={index} className="emotion-timeline__day">
              <span className="emotion-timeline__day-label">
                {new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short' })}
              </span>
              <span className="emotion-timeline__day-emoji">
                {EMOTION_EMOJIS[entry.emotion] || '😐'}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="emotion-timeline emotion-timeline--detailed">
      <div className="emotion-timeline__header">
        <h3>Your Emotional Journey ({timespan === '7day' ? 'Last 7 Days' : 'Last 30 Days'})</h3>
      </div>

      <div className="emotion-timeline__days">
        {emotionData.map((entry, index) => (
          <div
            key={index}
            className={`emotion-timeline__day ${
              highlightDissonance && entry.dissonance && entry.dissonance > 0.5
                ? 'emotion-timeline__day--dissonance'
                : ''
            }`}
          >
            <span className="emotion-timeline__day-label">
              {new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short' })}
            </span>
            <span className="emotion-timeline__day-emoji">
              {EMOTION_EMOJIS[entry.emotion] || '😐'}
            </span>
            {highlightDissonance && entry.dissonance && entry.dissonance > 0.5 && (
              <span className="emotion-timeline__dissonance-indicator" title="Dissonance detected">
                ⚠️
              </span>
            )}
          </div>
        ))}
      </div>

      {showPatterns && patterns.length > 0 && (
        <div className="emotion-timeline__patterns">
          <h4>Patterns We Notice:</h4>
          <ul>
            {patterns.map((pattern, index) => (
              <li key={index}>
                <strong>{pattern.frequency}:</strong> {pattern.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {showCoping && copingStrategies.length > 0 && (
        <div className="emotion-timeline__coping">
          <h4>What Seems to Help:</h4>
          <ul>
            {copingStrategies.map((strategy, index) => (
              <li key={index}>
                <span className="emotion-timeline__coping-strategy">
                  ✓ {strategy.strategy}
                </span>
                <span className="emotion-timeline__coping-effectiveness">
                  ({Math.round(strategy.effectiveness * 100)}% effective)
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default EmotionTimeline;

