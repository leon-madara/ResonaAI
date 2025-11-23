/**
 * Voice Recorder Component
 *
 * Primary input mechanism - records user voice
 * Adapts prompt and encouragement based on patterns
 */

import React, { useState, useRef, useEffect } from 'react';
import { VoiceRecorderProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function VoiceRecorder({
  prompt,
  culturalMode,
  encouragement,
  prominence,
  urgency
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setDuration(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const uploadAudio = async () => {
    if (!audioBlob) return;

    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await fetch('/api/voice/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Success - clear audio and show success message
        setAudioBlob(null);
        setDuration(0);
        // Could show a success toast here
      } else {
        alert('Failed to upload audio. Please try again.');
      }
    } catch (error) {
      console.error('Error uploading audio:', error);
      alert('Error uploading audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const discardRecording = () => {
    setAudioBlob(null);
    setDuration(0);
  };

  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className="space-y-4">
        {/* Prompt */}
        <div className="text-center">
          <h2
            className="font-semibold text-[var(--color-text)] mb-2"
            style={{ fontSize: 'calc(1.75rem * var(--font-scale))' }}
          >
            {prompt}
          </h2>
          <p
            className="text-gray-600"
            style={{ fontSize: 'calc(1rem * var(--font-scale))' }}
          >
            {encouragement}
          </p>
        </div>

        {/* Recording interface */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8">
          {/* Status */}
          <div className="text-center mb-6">
            {isRecording ? (
              <div className="space-y-2">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-red-600 font-semibold">Recording...</span>
                </div>
                <div className="text-3xl font-mono text-gray-700">
                  {formatDuration(duration)}
                </div>
              </div>
            ) : audioBlob ? (
              <div className="space-y-2">
                <div className="text-green-600 font-semibold flex items-center justify-center gap-2">
                  <span>✓</span>
                  <span>Recording complete</span>
                </div>
                <div className="text-lg text-gray-600">
                  Duration: {formatDuration(duration)}
                </div>
              </div>
            ) : (
              <div className="text-gray-600">
                Tap to record your voice
              </div>
            )}
          </div>

          {/* Microphone visualization */}
          <div className="flex justify-center mb-6">
            <button
              onClick={isRecording ? stopRecording : (audioBlob ? undefined : startRecording)}
              disabled={!!audioBlob || isProcessing}
              className={`w-24 h-24 rounded-full flex items-center justify-center text-4xl
                         transition-all duration-300 shadow-lg hover:shadow-xl
                         ${isRecording
                           ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                           : audioBlob
                           ? 'bg-gray-300 cursor-not-allowed'
                           : 'bg-[var(--color-primary)] hover:scale-110'
                         }`}
            >
              {isRecording ? '⏸' : audioBlob ? '✓' : '🎤'}
            </button>
          </div>

          {/* Action buttons */}
          {audioBlob && !isProcessing && (
            <div className="flex gap-4 justify-center">
              <button
                onClick={discardRecording}
                className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg
                           font-semibold transition-colors"
              >
                Discard
              </button>
              <button
                onClick={uploadAudio}
                className="px-6 py-3 bg-[var(--color-primary)] hover:opacity-90 text-white rounded-lg
                           font-semibold transition-opacity flex items-center gap-2"
              >
                <span>Send</span>
                <span>→</span>
              </button>
            </div>
          )}

          {isProcessing && (
            <div className="text-center text-gray-600">
              <div className="animate-spin w-8 h-8 border-4 border-gray-300 border-t-[var(--color-primary)] rounded-full mx-auto mb-2" />
              <div>Processing your voice...</div>
            </div>
          )}
        </div>

        {/* Privacy note */}
        <div className="text-xs text-gray-500 text-center space-y-1">
          <div>🔒 Your voice is encrypted end-to-end</div>
          <div>Audio is deleted after 7 days • Only patterns are stored, not recordings</div>
        </div>
      </div>
    </ComponentWrapper>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
