/**
 * VoiceRecorder Component (Design System)
 * 
 * Primary interaction—records user's voice with context-aware prompts.
 * Part of the ResonaAI Design System.
 */

import React, { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Square } from 'lucide-react';
import { motion } from 'framer-motion';
import './VoiceRecorder.css';

export interface VoiceRecorderProps {
  prompt: string;
  promptLanguage: 'swahili' | 'english' | 'mixed';
  visualFeedback: 'waveform' | 'ambient' | 'minimal';
  culturallyAdapted: boolean;
  urgency: 'low' | 'medium' | 'high';
  maxDuration?: number;
  onRecordingComplete?: (audioBlob: Blob) => void;
  onTranscriptionComplete?: (text: string) => void;
  disabled?: boolean;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  prompt,
  promptLanguage,
  visualFeedback,
  culturallyAdapted,
  urgency,
  maxDuration = 300,
  onRecordingComplete,
  onTranscriptionComplete,
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        onRecordingComplete?.(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  }, [maxDuration, onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording]);

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div 
      className={`voice-recorder-ds voice-recorder-ds--${visualFeedback} voice-recorder-ds--${urgency}`}
      data-culturally-adapted={culturallyAdapted}
    >
      <div className="voice-recorder-ds__prompt">
        <p className={`voice-recorder-ds__prompt-text voice-recorder-ds__prompt-text--${promptLanguage}`}>
          {prompt}
        </p>
      </div>

      <div className="voice-recorder-ds__controls">
        <motion.button
          className={`voice-recorder-ds__button voice-recorder-ds__button--${urgency}`}
          onClick={handleToggleRecording}
          disabled={disabled}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          animate={isRecording ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 1, repeat: isRecording ? Infinity : 0 }}
        >
          {isRecording ? (
            <>
              <Square className="voice-recorder-ds__icon" />
              <span className="voice-recorder-ds__button-text">Stop</span>
            </>
          ) : (
            <>
              <Mic className="voice-recorder-ds__icon" />
              <span className="voice-recorder-ds__button-text">Record</span>
            </>
          )}
        </motion.button>

        {isRecording && (
          <div className="voice-recorder-ds__timer">
            <div className="voice-recorder-ds__pulse" />
            <span>{formatTime(recordingTime)}</span>
          </div>
        )}
      </div>

      {visualFeedback === 'waveform' && isRecording && (
        <div className="voice-recorder-ds__waveform">
          {Array.from({ length: 20 }).map((_, i) => (
            <motion.div
              key={i}
              className="voice-recorder-ds__waveform-bar"
              animate={{
                height: [20, Math.random() * 60 + 20, 20],
              }}
              transition={{
                duration: 0.5,
                repeat: Infinity,
                delay: i * 0.05,
              }}
            />
          ))}
        </div>
      )}

      {visualFeedback === 'ambient' && isRecording && (
        <div className="voice-recorder-ds__ambient">
          <motion.div
            className="voice-recorder-ds__ambient-circle"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;

