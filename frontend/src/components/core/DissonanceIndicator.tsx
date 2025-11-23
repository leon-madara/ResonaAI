/**
 * Dissonance Indicator Component
 *
 * THE TRUTH DETECTOR VISUALIZATION
 *
 * Shows the gap between what user SAID (words) and what their VOICE showed (emotion)
 * This is the core innovation - catching concealed distress
 */

import React from 'react';
import { DissonanceIndicatorProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function DissonanceIndicator({
  dissonance_score,
  gap_explanation,
  truth_signal,
  example,
  prominence,
  urgency
}: DissonanceIndicatorProps) {
  // Calculate visual intensity based on score
  const intensity = Math.round(dissonance_score * 100);

  // Get color based on score
  const scoreColor = getScoreColor(dissonance_score);

  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3
            className="font-semibold text-[var(--color-text)]"
            style={{ fontSize: 'calc(1.25rem * var(--font-scale))' }}
          >
            We hear something different
          </h3>

          {/* Score indicator */}
          <div className="flex items-center gap-2">
            <div className="text-sm text-gray-600">Dissonance:</div>
            <div
              className="font-bold"
              style={{
                color: scoreColor,
                fontSize: 'calc(1.125rem * var(--font-scale))'
              }}
            >
              {intensity}%
            </div>
          </div>
        </div>

        {/* Visual representation */}
        <div className="space-y-2">
          {/* Progress bar */}
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-500"
              style={{
                width: `${intensity}%`,
                backgroundColor: scoreColor
              }}
            />
          </div>

          <div className="text-xs text-gray-500 flex justify-between">
            <span>Words match voice</span>
            <span>Words ≠ voice</span>
          </div>
        </div>

        {/* Gap explanation */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <p
            className="text-gray-700 leading-relaxed"
            style={{ fontSize: 'calc(0.9375rem * var(--font-scale))' }}
          >
            {gap_explanation}
          </p>
        </div>

        {/* Example (if provided) */}
        {example && (
          <div className="space-y-3">
            <div className="text-sm font-medium text-gray-700">For example:</div>

            {/* What you said */}
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-sm">💬</span>
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">You said:</div>
                <div className="text-gray-800 italic">"{example.stated}"</div>
              </div>
            </div>

            {/* What your voice showed */}
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center">
                <span className="text-sm">🎵</span>
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">Your voice showed:</div>
                <div className="text-gray-800 font-medium">{example.voice_showed}</div>
              </div>
            </div>
          </div>
        )}

        {/* Truth signal */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-start gap-2">
            <div className="flex-shrink-0 text-xl">💙</div>
            <p
              className="text-gray-700 leading-relaxed"
              style={{ fontSize: 'calc(0.9375rem * var(--font-scale))' }}
            >
              {truth_signal}
            </p>
          </div>
        </div>

        {/* Reassurance */}
        <div className="text-sm text-gray-600 italic">
          This is common. Many people find it easier to say they're "fine" than to express how they really feel.
          We're listening to the full truth.
        </div>
      </div>
    </ComponentWrapper>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getScoreColor(score: number): string {
  if (score >= 0.8) return '#DC2626'; // High dissonance - red
  if (score >= 0.6) return '#EA580C'; // Medium-high - orange
  if (score >= 0.4) return '#F59E0B'; // Medium - amber
  return '#10B981'; // Low - green
}
