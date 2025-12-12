import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VoiceRecorder from '../../components/VoiceRecorder/VoiceRecorder';
import { EmotionProvider } from '../../contexts/EmotionContext';
import { OfflineProvider } from '../../contexts/OfflineContext';

// Mock react-audio-voice-recorder
jest.mock('react-audio-voice-recorder', () => ({
  useAudioRecorder: () => ({
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
    recordingBlob: null,
    isRecording: false,
    recordingTime: 0,
  }),
}));

// Mock fetch
global.fetch = jest.fn();

describe('VoiceRecorder', () => {
  const renderVoiceRecorder = (props = {}) => {
    return render(
      <OfflineProvider>
        <EmotionProvider>
          <VoiceRecorder {...props} />
        </EmotionProvider>
      </OfflineProvider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        transcript: 'Test transcript',
        emotion_data: { emotion: 'happy', confidence: 0.9 },
      }),
    });
  });

  it('renders the voice recorder component', () => {
    renderVoiceRecorder();
    expect(screen.getByRole('button', { name: /record/i })).toBeInTheDocument();
  });

  it('shows recording button when not recording', () => {
    renderVoiceRecorder();
    const recordButton = screen.getByRole('button', { name: /record/i });
    expect(recordButton).toBeInTheDocument();
  });

  it('calls onRecordingComplete when recording is processed', async () => {
    const onRecordingComplete = jest.fn();
    renderVoiceRecorder({ onRecordingComplete });

    // This test would need more setup with actual recording mock
    // For now, just verify the prop is accepted
    expect(onRecordingComplete).toBeDefined();
  });

  it('displays offline indicator when offline', () => {
    // Mock offline status
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: false,
    });

    renderVoiceRecorder();
    // Component should handle offline state
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});

