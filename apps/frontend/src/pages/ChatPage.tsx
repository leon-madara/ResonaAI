import React, { useState, useCallback } from 'react';
import { VoiceRecorder, EmotionTimeline, DissonanceIndicator, GentleObservations } from '../components/design-system';
import ConversationUI from '../components/ConversationUI/ConversationUI';
import { useEmotion } from '../contexts/EmotionContext';
import { useOffline } from '../contexts/OfflineContext';
import { useAuth } from '../contexts/AuthContext';
import { analyzeDissonance, updateBaseline, checkDeviation, type DissonanceAnalysisResponse, getApiBaseUrl, getAuthHeader } from '../utils/api';
import { Wifi, WifiOff } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './ChatPage.css';

const ChatPage: React.FC = () => {
  const { isOnline } = useOffline();
  const { currentEmotion, emotionHistory, updateEmotionState } = useEmotion();
  const { user, token } = useAuth();
  const [dissonanceData, setDissonanceData] = useState<DissonanceAnalysisResponse | null>(null);
  const [sessionId] = useState<string>(() => `session-${Date.now()}`);

  // Process audio recording: transcribe, detect emotion, analyze dissonance, update baseline
  const handleRecordingComplete = useCallback(async (audioBlob: Blob) => {
    if (!token || !user?.id || !isOnline) {
      toast.error('Please connect to the internet to process your recording');
      return;
    }

    try {
      const apiBaseUrl = getApiBaseUrl();
      
      // Step 1: Transcribe audio and detect emotion
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.wav');
      formData.append('language', 'en');
      formData.append('accent', 'kenyan');
      formData.append('enable_emotion_detection', 'true');

      const transcribeResponse = await fetch(`${apiBaseUrl}/speech/transcribe`, {
        method: 'POST',
        body: formData,
        headers: getAuthHeader(token),
      });

      if (!transcribeResponse.ok) {
        throw new Error('Transcription failed');
      }

      const transcribeResult = await transcribeResponse.json();
      const transcript = transcribeResult.text || '';
      const voiceEmotion = transcribeResult.emotion_data;

      // Update emotion context
      if (voiceEmotion) {
        updateEmotionState({
          emotion: voiceEmotion.emotion,
          confidence: voiceEmotion.confidence,
          timestamp: new Date(),
        });
      }

      // Step 2: Analyze dissonance if we have both transcript and emotion
      if (transcript.trim() && voiceEmotion) {
        try {
          const dissonanceResult = await analyzeDissonance(token, {
            transcript: transcript,
            voice_emotion: voiceEmotion,
            session_id: sessionId,
            user_id: user.id,
            timestamp: new Date().toISOString(),
          });

          // Show dissonance indicator if detected
          if (dissonanceResult.dissonance_level !== 'low') {
            setDissonanceData(dissonanceResult);
          }
        } catch (error) {
          console.error('Failed to analyze dissonance:', error);
          // Non-critical, continue
        }
      }

      // Step 3: Update baseline with emotion data
      if (voiceEmotion) {
        try {
          await updateBaseline(token, {
            user_id: user.id,
            emotion_data: voiceEmotion,
            session_id: sessionId,
          });
        } catch (error) {
          console.error('Failed to update baseline:', error);
          // Non-critical, continue
        }
      }

      toast.success('Recording processed successfully');
    } catch (error) {
      console.error('Failed to process recording:', error);
      toast.error('Failed to process recording. Please try again.');
    }
  }, [token, user?.id, sessionId, isOnline, updateEmotionState]);

  // Emotion history for timeline
  const timelineData = emotionHistory || [
    { date: new Date().toISOString(), emotion: currentEmotion?.emotion || 'neutral', confidence: currentEmotion?.confidence || 0.5 }
  ];

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1 className="chat-title">Voice Conversation</h1>
        <div className="connection-status">
          {isOnline ? (
            <div className="status-online">
              <Wifi className="w-4 h-4" />
              <span>Online</span>
            </div>
          ) : (
            <div className="status-offline">
              <WifiOff className="w-4 h-4" />
              <span>Offline</span>
            </div>
          )}
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-main">
          <ConversationUI />
          
          {dissonanceData && (
            <DissonanceIndicator
              visibility="when_detected"
              showExplanation={true}
              statedEmotion={dissonanceData.stated_emotion}
              voiceEmotion={dissonanceData.actual_emotion}
              dissonanceScore={dissonanceData.dissonance_score}
              interpretation={dissonanceData.interpretation}
              onDismiss={() => setDissonanceData(null)}
              onTellMore={() => {
                // Could show more details in a modal or expand the indicator
                toast('Dissonance detected: Your words and voice tone don\'t match. This is normal and we\'re here to help.');
              }}
            />
          )}

          {/* Gentle Observations - show when emotion is detected */}
          {currentEmotion && currentEmotion.confidence > 0.7 && (
            <GentleObservations
              observations={[
                { type: 'pattern', message: `I notice ${currentEmotion.emotion} in your voice` },
                { type: 'pattern', message: `Your tone suggests you might be feeling ${currentEmotion.emotion}` },
              ]}
              tone="validating"
            />
          )}

          <div className="recorder-section">
            <VoiceRecorder
              prompt="Take your time. When you're ready, tell me what's on your mind."
              promptLanguage="english"
              visualFeedback="waveform"
              culturallyAdapted={true}
              urgency="low"
              maxDuration={300}
              onRecordingComplete={handleRecordingComplete}
              disabled={!isOnline}
            />
          </div>
        </div>

        <div className="chat-sidebar">
          {timelineData.length > 0 && (
            <EmotionTimeline
              timespan="session"
              showPatterns={true}
              showTriggers={false}
              showCoping={false}
              highlightDissonance={true}
              style="simple"
              emotionData={timelineData.map(e => ({
                date: e.timestamp?.toISOString() || new Date().toISOString(),
                emotion: e.emotion || 'neutral',
                confidence: e.confidence || 0.5
              }))}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

