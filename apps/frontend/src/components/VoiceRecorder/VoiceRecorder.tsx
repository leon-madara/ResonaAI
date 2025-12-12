import React, { useState, useRef, useCallback } from 'react';
import { useAudioRecorder } from 'react-audio-voice-recorder';
import { Mic, MicOff, Square, Play, Pause, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEmotion } from '../../contexts/EmotionContext';
import { useOffline } from '../../contexts/OfflineContext';
import { toast } from 'react-hot-toast';
import './VoiceRecorder.css';
import { getApiBaseUrl, getAuthHeader } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';

interface VoiceRecorderProps {
  onRecordingComplete?: (audioBlob: Blob) => void;
  onTranscriptionComplete?: (text: string) => void;
  disabled?: boolean;
  maxDuration?: number;
  className?: string;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onRecordingComplete,
  onTranscriptionComplete,
  disabled = false,
  maxDuration = 300, // 5 minutes
  className = ''
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  const { isOnline } = useOffline();
  const { updateEmotionState } = useEmotion();
  const { token } = useAuth();
  const apiBaseUrl = getApiBaseUrl();

  const {
    startRecording,
    stopRecording,
    recordingBlob,
    isRecording: recorderIsRecording,
    recordingTime: recorderTime
  } = useAudioRecorder();

  const startRecordingHandler = useCallback(async () => {
    try {
      if (!isOnline && !navigator.onLine) {
        toast.error('Recording requires internet connection');
        return;
      }

      setIsRecording(true);
      setRecordingTime(0);
      setAudioBlob(null);
      setAudioUrl(null);
      
      await startRecording();
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= maxDuration) {
            stopRecordingHandler();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
      
      toast.success('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      toast.error('Failed to start recording');
      setIsRecording(false);
    }
  }, [startRecording, isOnline, maxDuration]);

  const stopRecordingHandler = useCallback(async () => {
    try {
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      const blob = await stopRecording();
      if (blob) {
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        
        // Process recording
        await processRecording(blob);
        
        toast.success('Recording completed');
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      toast.error('Failed to stop recording');
    }
  }, [stopRecording]);

  const processRecording = async (blob: Blob) => {
    setIsProcessing(true);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('audio_file', blob, 'recording.wav');
      formData.append('language', 'en');
      formData.append('accent', 'kenyan');
      formData.append('enable_emotion_detection', 'true');

      // Send to speech processing service
      const response = await fetch(`${apiBaseUrl}/speech/transcribe`, {
        method: 'POST',
        body: formData,
        headers: {
          ...getAuthHeader(token),
        }
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const result = await response.json();
      
      // Update emotion context
      if (result.emotion_data) {
        updateEmotionState({
          emotion: result.emotion_data.emotion,
          confidence: result.emotion_data.confidence,
          timestamp: new Date()
        });
      }
      
      // Call completion handlers
      onRecordingComplete?.(blob);
      onTranscriptionComplete?.(result.text);
      
    } catch (error) {
      console.error('Processing failed:', error);
      toast.error('Failed to process recording');
    } finally {
      setIsProcessing(false);
    }
  };

  const playRecording = useCallback(() => {
    if (audioRef.current && audioUrl) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  }, [audioUrl, isPlaying]);

  const deleteRecording = useCallback(() => {
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`voice-recorder ${className}`}>
      {/* Recording Controls */}
      <div className="recording-controls">
        <AnimatePresence>
          {!isRecording && !audioBlob && (
            <motion.button
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={startRecordingHandler}
              disabled={disabled || isProcessing}
              className="record-button"
              aria-label="Start recording"
            >
              <Mic className="w-6 h-6" />
            </motion.button>
          )}
        </AnimatePresence>

        {isRecording && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="recording-active"
          >
            <button
              onClick={stopRecordingHandler}
              className="stop-button"
              aria-label="Stop recording"
            >
              <Square className="w-6 h-6" />
            </button>
            <div className="recording-indicator">
              <div className="pulse-animation" />
              <span className="recording-time">{formatTime(recordingTime)}</span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Audio Playback */}
      <AnimatePresence>
        {audioBlob && audioUrl && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="audio-playback"
          >
            <div className="audio-controls">
              <button
                onClick={playRecording}
                disabled={isProcessing}
                className="play-button"
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              
              <button
                onClick={deleteRecording}
                disabled={isProcessing}
                className="delete-button"
                aria-label="Delete recording"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            
            <div className="audio-info">
              <span className="duration">{formatTime(recordingTime)}</span>
              {isProcessing && (
                <div className="processing-indicator">
                  <div className="spinner" />
                  <span>Processing...</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        src={audioUrl || undefined}
        onEnded={() => setIsPlaying(false)}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      {/* Offline indicator */}
      {!isOnline && (
        <div className="offline-indicator">
          <MicOff className="w-4 h-4" />
          <span>Offline - Recording not available</span>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
