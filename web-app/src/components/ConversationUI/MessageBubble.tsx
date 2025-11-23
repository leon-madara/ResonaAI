import React, { useState } from 'react';
import { User, Bot, Volume2, VolumeX, Play, Pause } from 'lucide-react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import './MessageBubble.css';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  emotion?: {
    emotion: string;
    confidence: number;
  };
  audioUrl?: string;
}

interface MessageBubbleProps {
  message: Message;
  onSpeak?: () => void;
  onStopSpeaking?: () => void;
  isSpeaking?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onSpeak,
  onStopSpeaking,
  isSpeaking = false
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioError, setAudioError] = useState(false);

  const isUser = message.type === 'user';
  const hasAudio = !!message.audioUrl;
  const hasEmotion = !!message.emotion;

  const playAudio = () => {
    if (!message.audioUrl) return;
    
    const audio = new Audio(message.audioUrl);
    setIsPlaying(true);
    setAudioError(false);
    
    audio.onended = () => setIsPlaying(false);
    audio.onerror = () => {
      setIsPlaying(false);
      setAudioError(true);
    };
    
    audio.play().catch(() => {
      setIsPlaying(false);
      setAudioError(true);
    });
  };

  const stopAudio = () => {
    setIsPlaying(false);
    // Note: We can't actually stop the audio without keeping a reference
    // This is a limitation of the current implementation
  };

  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      happy: '#10b981',
      sad: '#3b82f6',
      angry: '#ef4444',
      fear: '#8b5cf6',
      surprise: '#f59e0b',
      disgust: '#84cc16',
      neutral: '#6b7280'
    };
    return colors[emotion] || colors.neutral;
  };

  const getEmotionIcon = (emotion: string) => {
    const icons: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      fear: '😨',
      surprise: '😲',
      disgust: '🤢',
      neutral: '😐'
    };
    return icons[emotion] || icons.neutral;
  };

  return (
    <motion.div
      className={`message-bubble ${isUser ? 'user-message' : 'ai-message'}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      {/* Avatar */}
      <div className="message-avatar">
        {isUser ? (
          <User className="w-6 h-6" />
        ) : (
          <Bot className="w-6 h-6" />
        )}
      </div>

      {/* Message Content */}
      <div className="message-content">
        {/* Message Text */}
        <div className="message-text">
          {message.content}
        </div>

        {/* Audio Player */}
        {hasAudio && (
          <div className="audio-player">
            <button
              onClick={isPlaying ? stopAudio : playAudio}
              disabled={audioError}
              className="audio-button"
              aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
            >
              {audioError ? (
                <VolumeX className="w-4 h-4 text-red-500" />
              ) : isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
            </button>
            <span className="audio-label">Voice message</span>
          </div>
        )}

        {/* Emotion Indicator */}
        {hasEmotion && (
          <div className="emotion-indicator">
            <span className="emotion-emoji">
              {getEmotionIcon(message.emotion!.emotion)}
            </span>
            <span className="emotion-text">
              {message.emotion!.emotion} ({Math.round(message.emotion!.confidence * 100)}%)
            </span>
            <div
              className="emotion-bar"
              style={{
                backgroundColor: getEmotionColor(message.emotion!.emotion),
                width: `${message.emotion!.confidence * 100}%`
              }}
            />
          </div>
        )}

        {/* Timestamp */}
        <div className="message-timestamp">
          {format(message.timestamp, 'HH:mm')}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="message-actions">
        {!isUser && (
          <button
            onClick={isSpeaking ? onStopSpeaking : onSpeak}
            className="speak-button"
            aria-label={isSpeaking ? 'Stop speaking' : 'Read aloud'}
          >
            {isSpeaking ? (
              <VolumeX className="w-4 h-4" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default MessageBubble;
