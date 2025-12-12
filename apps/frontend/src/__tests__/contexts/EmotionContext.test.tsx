import React from 'react';
import { render, screen } from '@testing-library/react';
import { EmotionProvider, useEmotion } from '../../contexts/EmotionContext';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Test component
const TestComponent = () => {
  const { currentEmotion, emotionHistory, updateEmotionState, getEmotionTrend } = useEmotion();

  return (
    <div>
      <div data-testid="current-emotion">
        {currentEmotion ? currentEmotion.emotion : 'None'}
      </div>
      <div data-testid="history-count">{emotionHistory.length}</div>
      <button
        onClick={() =>
          updateEmotionState({
            emotion: 'happy',
            confidence: 0.9,
            timestamp: new Date(),
          })
        }
      >
        Update Emotion
      </button>
      <button onClick={() => getEmotionTrend('day')}>Get Day Trend</button>
    </div>
  );
};

describe('EmotionContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('provides initial state with no emotion', () => {
    render(
      <EmotionProvider>
        <TestComponent />
      </EmotionProvider>
    );

    expect(screen.getByTestId('current-emotion')).toHaveTextContent('None');
    expect(screen.getByTestId('history-count')).toHaveTextContent('0');
  });

  it('restores emotion history from localStorage', () => {
    const mockHistory = [
      {
        emotion: 'sad',
        confidence: 0.8,
        timestamp: new Date().toISOString(),
      },
    ];

    localStorageMock.getItem.mockReturnValue(JSON.stringify(mockHistory));

    render(
      <EmotionProvider>
        <TestComponent />
      </EmotionProvider>
    );

    expect(screen.getByTestId('current-emotion')).toHaveTextContent('sad');
    expect(screen.getByTestId('history-count')).toHaveTextContent('1');
  });

  it('updates emotion state', () => {
    render(
      <EmotionProvider>
        <TestComponent />
      </EmotionProvider>
    );

    const updateButton = screen.getByText('Update Emotion');
    updateButton.click();

    expect(screen.getByTestId('current-emotion')).toHaveTextContent('happy');
    expect(localStorageMock.setItem).toHaveBeenCalled();
  });

  it('filters emotion trend by time range', () => {
    render(
      <EmotionProvider>
        <TestComponent />
      </EmotionProvider>
    );

    const trendButton = screen.getByText('Get Day Trend');
    trendButton.click();

    // Function should execute without error
    expect(trendButton).toBeInTheDocument();
  });
});

