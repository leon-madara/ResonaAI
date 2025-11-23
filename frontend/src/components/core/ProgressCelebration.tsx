/**
 * Progress Celebration Component
 *
 * Shows when user is improving - celebrates their progress
 * Only visible when trajectory = 'improving'
 */

import React from 'react';
import { ProgressCelebrationProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function ProgressCelebration({
  message,
  trajectory,
  show_chart,
  prominence,
  urgency
}: ProgressCelebrationProps) {
  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className="bg-gradient-to-br from-green-50 to-teal-50 rounded-lg p-6 space-y-4">
        {/* Header with celebration */}
        <div className="flex items-center gap-4">
          <div className="text-5xl animate-bounce">🌟</div>
          <div>
            <h3
              className="font-bold text-green-800"
              style={{ fontSize: 'calc(1.5rem * var(--font-scale))' }}
            >
              You're making progress
            </h3>
            <div className="text-sm text-green-600 font-medium mt-1">
              Your voice tells us you're doing better
            </div>
          </div>
        </div>

        {/* Message */}
        <div className="bg-white rounded-lg p-4">
          <p
            className="text-gray-700 leading-relaxed"
            style={{ fontSize: 'calc(1rem * var(--font-scale))' }}
          >
            {message}
          </p>
        </div>

        {/* Simple trajectory visualization */}
        {show_chart && (
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-700">Your trajectory:</div>
            <div className="flex items-end gap-1 h-20">
              {[40, 45, 55, 60, 70].map((height, index) => (
                <div
                  key={index}
                  className="flex-1 bg-gradient-to-t from-green-400 to-green-500 rounded-t transition-all duration-500"
                  style={{
                    height: `${height}%`,
                    animationDelay: `${index * 100}ms`
                  }}
                />
              ))}
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>Past</span>
              <span className="text-green-600 font-semibold">→ Improving</span>
            </div>
          </div>
        )}

        {/* Encouragement */}
        <div className="flex items-start gap-2 bg-green-100 rounded p-3">
          <div className="text-xl">💪</div>
          <p className="text-sm text-green-900">
            This progress is real. Whatever you're doing, keep going. We hear the strength in your voice.
          </p>
        </div>
      </div>
    </ComponentWrapper>
  );
}
