import React from 'react';
import VoiceRecorder from '../components/VoiceRecorder/VoiceRecorder';
import ConversationUI from '../components/ConversationUI/ConversationUI';
import { useEmotion } from '../contexts/EmotionContext';
import { useOffline } from '../contexts/OfflineContext';
import { Wifi, WifiOff } from 'lucide-react';
import './ChatPage.css';

const ChatPage: React.FC = () => {
  const { isOnline } = useOffline();
  const { currentEmotion } = useEmotion();

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

      {currentEmotion && (
        <div className="emotion-indicator">
          <span className="emotion-label">Current emotion:</span>
          <span className="emotion-value">{currentEmotion.emotion}</span>
          <span className="emotion-confidence">
            ({Math.round(currentEmotion.confidence * 100)}%)
          </span>
        </div>
      )}

      <div className="chat-container">
        <ConversationUI />
        
        <div className="recorder-section">
          <VoiceRecorder
            onRecordingComplete={(audioBlob) => {
              console.log('Recording complete:', audioBlob);
            }}
            onTranscriptionComplete={(text) => {
              console.log('Transcription:', text);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;

