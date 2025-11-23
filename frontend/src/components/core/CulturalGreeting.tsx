/**
 * Cultural Greeting Component
 *
 * Personalized greeting that adapts to:
 * - Language (Swahili, English, Mixed)
 * - Time of day
 * - Emotional mood
 * - User patterns
 */

import React, { useMemo } from 'react';
import { CulturalGreetingProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function CulturalGreeting({
  language,
  timeOfDay,
  mood,
  personalization,
  userName,
  prominence,
  urgency
}: CulturalGreetingProps) {
  // Generate greeting based on language and time
  const greeting = useMemo(() => {
    const time = timeOfDay || getCurrentTimeOfDay();

    if (language === 'swahili') {
      return getSwahiliGreeting(time);
    } else if (language === 'mixed') {
      return getMixedGreeting(time);
    } else {
      return getEnglishGreeting(time);
    }
  }, [language, timeOfDay]);

  // Get mood styling
  const moodStyles = useMemo(() => {
    switch (mood) {
      case 'concerned':
        return {
          emoji: '💙',
          color: 'text-blue-600',
          bg: 'bg-blue-50'
        };

      case 'celebratory':
        return {
          emoji: '🌟',
          color: 'text-yellow-600',
          bg: 'bg-yellow-50'
        };

      case 'gentle':
        return {
          emoji: '🌸',
          color: 'text-pink-600',
          bg: 'bg-pink-50'
        };

      case 'warm':
      default:
        return {
          emoji: '☀️',
          color: 'text-orange-600',
          bg: 'bg-orange-50'
        };
    }
  }, [mood]);

  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className={`${moodStyles.bg} rounded-lg p-[calc(1.5rem*var(--spacing-scale))]`}>
        <div className="flex items-start gap-4">
          {/* Mood emoji */}
          <div className="text-4xl flex-shrink-0" style={{ fontSize: 'calc(2.5rem * var(--font-scale))' }}>
            {moodStyles.emoji}
          </div>

          <div className="flex-1">
            {/* Greeting */}
            <h2
              className={`${moodStyles.color} font-semibold mb-2`}
              style={{ fontSize: 'calc(1.5rem * var(--font-scale))' }}
            >
              {greeting}
              {userName && `, ${userName}`}
            </h2>

            {/* Personalized message */}
            <p
              className="text-gray-700 leading-relaxed"
              style={{ fontSize: 'calc(1rem * var(--font-scale))' }}
            >
              {personalization}
            </p>
          </div>
        </div>
      </div>
    </ComponentWrapper>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getCurrentTimeOfDay(): 'morning' | 'afternoon' | 'evening' | 'night' {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 17) return 'afternoon';
  if (hour >= 17 && hour < 21) return 'evening';
  return 'night';
}

function getSwahiliGreeting(time: string): string {
  switch (time) {
    case 'morning':
      return 'Habari ya asubuhi';
    case 'afternoon':
      return 'Habari ya mchana';
    case 'evening':
      return 'Habari ya jioni';
    case 'night':
      return 'Habari ya usiku';
    default:
      return 'Habari';
  }
}

function getEnglishGreeting(time: string): string {
  switch (time) {
    case 'morning':
      return 'Good morning';
    case 'afternoon':
      return 'Good afternoon';
    case 'evening':
      return 'Good evening';
    case 'night':
      return 'Hello';
    default:
      return 'Hello';
  }
}

function getMixedGreeting(time: string): string {
  switch (time) {
    case 'morning':
      return 'Habari, good morning';
    case 'afternoon':
      return 'Good afternoon, mambo vipi';
    case 'evening':
      return 'Habari ya jioni';
    case 'night':
      return 'Hello, mambo';
    default:
      return 'Habari';
  }
}
