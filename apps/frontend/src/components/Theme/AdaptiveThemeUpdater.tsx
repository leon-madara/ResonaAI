/**
 * AdaptiveThemeUpdater Component
 * 
 * Automatically updates the adaptive theme based on user's emotional state.
 * This component should be placed inside both ThemeProvider and EmotionProvider.
 */

import React, { useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useEmotion } from '../../contexts/EmotionContext';

const AdaptiveThemeUpdater: React.FC = () => {
  const { setAdaptiveTheme } = useTheme();
  const { currentEmotion, emotionHistory } = useEmotion();

  useEffect(() => {
    if (!currentEmotion) {
      setAdaptiveTheme('neutral');
      return;
    }

    const emotion = currentEmotion.emotion.toLowerCase();
    const confidence = currentEmotion.confidence;

    // Determine adaptive theme based on emotion
    // Only apply if confidence is high enough (>0.6)
    if (confidence < 0.6) {
      setAdaptiveTheme('neutral');
      return;
    }

    // Map emotions to adaptive themes
    if (emotion.includes('crisis') || emotion.includes('suicidal') || emotion.includes('panic')) {
      setAdaptiveTheme('crisis');
    } else if (emotion.includes('anxious') || emotion.includes('anxiety') || emotion.includes('worried') || emotion.includes('stressed')) {
      setAdaptiveTheme('anxiety');
    } else if (emotion.includes('sad') || emotion.includes('depressed') || emotion.includes('down') || emotion.includes('hopeless')) {
      setAdaptiveTheme('depression');
    } else if (emotion.includes('stable') || emotion.includes('calm') || emotion.includes('neutral') || emotion.includes('content')) {
      setAdaptiveTheme('stable');
    } else {
      // Default to neutral for other emotions
      setAdaptiveTheme('neutral');
    }
  }, [currentEmotion, setAdaptiveTheme]);

  // Also check recent emotion history for patterns
  useEffect(() => {
    if (emotionHistory.length < 3) return;

    // Check last 3 emotions for crisis patterns
    const recentEmotions = emotionHistory.slice(-3);
    const crisisCount = recentEmotions.filter(e => 
      e.emotion.toLowerCase().includes('crisis') || 
      e.emotion.toLowerCase().includes('suicidal') ||
      e.emotion.toLowerCase().includes('panic')
    ).length;

    if (crisisCount >= 2) {
      setAdaptiveTheme('crisis');
    }
  }, [emotionHistory, setAdaptiveTheme]);

  return null; // This component doesn't render anything
};

export default AdaptiveThemeUpdater;

