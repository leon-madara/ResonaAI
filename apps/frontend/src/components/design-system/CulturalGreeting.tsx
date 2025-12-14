/**
 * CulturalGreeting Component
 * 
 * Culturally-aware greeting that adapts to language preference and time of day.
 * Part of the ResonaAI Design System.
 */

import React from 'react';
import './CulturalGreeting.css';

export interface CulturalGreetingProps {
  language: 'swahili' | 'english' | 'mixed';
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  mood: 'warm' | 'gentle' | 'concerned' | 'celebratory';
  personalization?: string;
  userName?: string;
}

const GREETINGS = {
  swahili: {
    morning: 'Habari za asubuhi',
    afternoon: 'Habari za mchana',
    evening: 'Habari za jioni',
    night: 'Usiku mwema',
  },
  english: {
    morning: 'Good morning',
    afternoon: 'Good afternoon',
    evening: 'Good evening',
    night: 'Good night',
  },
  mixed: {
    morning: 'Habari, good morning',
    afternoon: 'Habari, good afternoon',
    evening: 'Habari, good evening',
    night: 'Usiku mwema, good night',
  },
};

const MOOD_EMOJIS = {
  warm: '🌅',
  gentle: '💙',
  concerned: '🤗',
  celebratory: '🎉',
};

export const CulturalGreeting: React.FC<CulturalGreetingProps> = ({
  language,
  timeOfDay,
  mood,
  personalization,
  userName,
}) => {
  const greeting = GREETINGS[language][timeOfDay];
  const emoji = MOOD_EMOJIS[mood];
  const displayName = userName ? `, ${userName}` : '';

  return (
    <div className={`cultural-greeting cultural-greeting--${mood}`}>
      <div className="cultural-greeting__text">
        <span className="cultural-greeting__greeting">
          {greeting}{displayName} {emoji}
        </span>
        {personalization && (
          <p className="cultural-greeting__personalization">{personalization}</p>
        )}
      </div>
    </div>
  );
};

export default CulturalGreeting;

