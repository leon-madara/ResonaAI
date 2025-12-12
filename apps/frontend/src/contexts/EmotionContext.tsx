import React, { createContext, useContext, useState, ReactNode } from 'react';

interface EmotionState {
  emotion: string;
  confidence: number;
  timestamp: Date;
}

interface EmotionContextType {
  currentEmotion: EmotionState | null;
  emotionHistory: EmotionState[];
  updateEmotionState: (emotion: EmotionState) => void;
  clearEmotionHistory: () => void;
  getEmotionTrend: (timeRange: 'day' | 'week' | 'month') => EmotionState[];
}

const EmotionContext = createContext<EmotionContextType | undefined>(undefined);

interface EmotionProviderProps {
  children: ReactNode;
}

export const EmotionProvider: React.FC<EmotionProviderProps> = ({ children }) => {
  const [currentEmotion, setCurrentEmotion] = useState<EmotionState | null>(null);
  const [emotionHistory, setEmotionHistory] = useState<EmotionState[]>([]);

  const updateEmotionState = (emotion: EmotionState) => {
    setCurrentEmotion(emotion);
    setEmotionHistory(prev => [...prev, emotion].slice(-100)); // Keep last 100 emotions
    
    // Store in localStorage for persistence
    try {
      const stored = localStorage.getItem('emotionHistory');
      const history = stored ? JSON.parse(stored) : [];
      const updatedHistory = [...history, emotion].slice(-100);
      localStorage.setItem('emotionHistory', JSON.stringify(updatedHistory));
    } catch (error) {
      console.error('Failed to store emotion history:', error);
    }
  };

  const clearEmotionHistory = () => {
    setEmotionHistory([]);
    setCurrentEmotion(null);
    localStorage.removeItem('emotionHistory');
  };

  const getEmotionTrend = (timeRange: 'day' | 'week' | 'month'): EmotionState[] => {
    const now = new Date();
    let cutoffDate: Date;
    
    switch (timeRange) {
      case 'day':
        cutoffDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case 'week':
        cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      default:
        cutoffDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    }
    
    return emotionHistory.filter(emotion => 
      new Date(emotion.timestamp) >= cutoffDate
    );
  };

  // Load emotion history from localStorage on mount
  React.useEffect(() => {
    try {
      const stored = localStorage.getItem('emotionHistory');
      if (stored) {
        const history = JSON.parse(stored).map((emotion: any) => ({
          ...emotion,
          timestamp: new Date(emotion.timestamp)
        }));
        setEmotionHistory(history);
        
        // Set current emotion to the most recent one
        if (history.length > 0) {
          setCurrentEmotion(history[history.length - 1]);
        }
      }
    } catch (error) {
      console.error('Failed to load emotion history:', error);
    }
  }, []);

  const value: EmotionContextType = {
    currentEmotion,
    emotionHistory,
    updateEmotionState,
    clearEmotionHistory,
    getEmotionTrend,
  };

  return (
    <EmotionContext.Provider value={value}>
      {children}
    </EmotionContext.Provider>
  );
};

export const useEmotion = (): EmotionContextType => {
  const context = useContext(EmotionContext);
  if (context === undefined) {
    throw new Error('useEmotion must be used within an EmotionProvider');
  }
  return context;
};
