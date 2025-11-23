import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, VolumeX, MoreVertical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import VoiceRecorder from '../VoiceRecorder/VoiceRecorder';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { useAuth } from '../../contexts/AuthContext';
import { useEmotion } from '../../contexts/EmotionContext';
import { useOffline } from '../../contexts/OfflineContext';
import { toast } from 'react-hot-toast';
import './ConversationUI.css';

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
  isTyping?: boolean;
}

interface ConversationUIProps {
  className?: string;
}

const ConversationUI: React.FC<ConversationUIProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  
  const { user } = useAuth();
  const { currentEmotion } = useEmotion();
  const { isOnline } = useOffline();

  useEffect(() => {
    synthRef.current = window.speechSynthesis;
    
    // Initialize with welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'ai',
      content: 'Hello! I\'m here to listen and support you. You can speak to me or type your message. How are you feeling today?',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (message: Omit<Message, 'id'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const sendMessage = async (content: string, audioBlob?: Blob) => {
    if (!content.trim() && !audioBlob) return;

    setIsProcessing(true);

    try {
      // Add user message
      const userMessage: Message = {
        type: 'user',
        content: content || '[Voice message]',
        timestamp: new Date(),
        audioUrl: audioBlob ? URL.createObjectURL(audioBlob) : undefined,
        emotion: currentEmotion ? {
          emotion: currentEmotion.emotion,
          confidence: currentEmotion.confidence
        } : undefined
      };
      
      addMessage(userMessage);
      setInputText('');
      setIsTyping(true);

      // Prepare request data
      const formData = new FormData();
      if (audioBlob) {
        formData.append('audio_file', audioBlob, 'message.wav');
      }
      formData.append('text', content);
      formData.append('emotion_context', JSON.stringify(currentEmotion));
      formData.append('conversation_history', JSON.stringify(messages.slice(-5))); // Last 5 messages

      // Send to conversation engine
      const response = await fetch('/api/conversation/chat', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const result = await response.json();
      
      setIsTyping(false);

      // Add AI response
      const aiMessage: Message = {
        type: 'ai',
        content: result.response,
        timestamp: new Date(),
        emotion: result.emotion_detected ? {
          emotion: result.emotion_detected.emotion,
          confidence: result.emotion_detected.confidence
        } : undefined
      };
      
      addMessage(aiMessage);

      // Auto-play AI response if TTS is enabled
      if (result.should_speak && !isSpeaking) {
        speakText(result.response);
      }

      // Check for crisis detection
      if (result.crisis_detected) {
        toast.error('We detected you might be in crisis. Please consider reaching out for immediate help.');
        // Navigate to crisis page or show crisis resources
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message. Please try again.');
      setIsTyping(false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !isProcessing) {
      sendMessage(inputText.trim());
    }
  };

  const handleVoiceRecording = (audioBlob: Blob) => {
    sendMessage('', audioBlob);
  };

  const handleTranscriptionComplete = (text: string) => {
    setInputText(text);
  };

  const speakText = (text: string) => {
    if (!synthRef.current) return;

    setIsSpeaking(true);
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;
    
    // Try to use a more natural voice
    const voices = synthRef.current.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.lang.startsWith('en') && voice.name.includes('Natural')
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'ai',
      content: 'Hello! I\'m here to listen and support you. You can speak to me or type your message. How are you feeling today?',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  };

  return (
    <div className={`conversation-ui ${className}`}>
      {/* Header */}
      <div className="conversation-header">
        <div className="header-info">
          <h2>Mental Health Support</h2>
          <p>AI-powered emotional support available 24/7</p>
        </div>
        <div className="header-actions">
          <button
            onClick={isSpeaking ? stopSpeaking : () => {}}
            disabled={!isSpeaking}
            className="speech-button"
            aria-label={isSpeaking ? 'Stop speaking' : 'Speech disabled'}
          >
            {isSpeaking ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
          <button
            onClick={clearConversation}
            className="more-button"
            aria-label="Clear conversation"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MessageBubble
                message={message}
                onSpeak={() => speakText(message.content)}
                onStopSpeaking={stopSpeaking}
                isSpeaking={isSpeaking}
              />
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <form onSubmit={handleTextSubmit} className="input-form">
          <div className="input-container">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message or use voice..."
              disabled={isProcessing}
              className="text-input"
            />
            
            <div className="input-actions">
              <VoiceRecorder
                onRecordingComplete={handleVoiceRecording}
                onTranscriptionComplete={handleTranscriptionComplete}
                disabled={!isOnline || isProcessing}
                className="voice-recorder-inline"
              />
              
              <button
                type="submit"
                disabled={!inputText.trim() || isProcessing}
                className="send-button"
                aria-label="Send message"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </form>
        
        {/* Offline indicator */}
        {!isOnline && (
          <div className="offline-notice">
            <p>You're offline. Messages will be sent when connection is restored.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationUI;
