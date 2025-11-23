/**
 * Crisis Resources Component
 *
 * Shows crisis support resources based on risk level
 * Prominence and urgency adapted to user's current risk
 */

import React from 'react';
import { CrisisResourcesProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function CrisisResources({
  risk_level,
  resources,
  tone,
  prominence,
  urgency
}: CrisisResourcesProps) {
  // Get styling based on tone
  const isUrgent = tone === 'urgent';

  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className={`space-y-4 ${isUrgent ? 'bg-red-50 p-6 rounded-lg' : ''}`}>
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="text-3xl">{isUrgent ? '🚨' : '💙'}</div>
          <div>
            <h3
              className={`font-bold ${isUrgent ? 'text-red-900' : 'text-gray-900'}`}
              style={{ fontSize: 'calc(1.5rem * var(--font-scale))' }}
            >
              {isUrgent ? 'We\'re concerned about you' : 'Support is available'}
            </h3>
            {isUrgent && (
              <p className="text-red-700 text-sm mt-1">
                You don't have to face this alone. Help is available 24/7.
              </p>
            )}
          </div>
        </div>

        {/* Message based on risk level */}
        <div className={`${isUrgent ? 'bg-white' : 'bg-blue-50'} p-4 rounded-lg`}>
          <p
            className="text-gray-700 leading-relaxed"
            style={{ fontSize: 'calc(1rem * var(--font-scale))' }}
          >
            {getMessage(risk_level, isUrgent)}
          </p>
        </div>

        {/* Resources */}
        <div className="space-y-3">
          <div className={`text-sm font-semibold ${isUrgent ? 'text-red-900' : 'text-gray-700'}`}>
            {isUrgent ? 'Call now - 24/7 support' : 'Available support:'}
          </div>

          {resources.map((resource, index) => (
            <div
              key={index}
              className={`${isUrgent ? 'bg-white border-2 border-red-200' : 'bg-white border border-gray-200'}
                         rounded-lg p-4 hover:shadow-md transition-shadow`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className={`font-semibold ${isUrgent ? 'text-red-900' : 'text-gray-900'}`}>
                    {resource.name}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Available: {resource.available}
                  </div>
                </div>

                <a
                  href={`tel:${resource.phone}`}
                  className={`${isUrgent ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}
                             text-white px-6 py-3 rounded-lg font-semibold text-lg
                             transition-colors duration-200 shadow-lg hover:shadow-xl
                             flex items-center gap-2`}
                  style={{ fontSize: 'calc(1.125rem * var(--font-scale))' }}
                >
                  <span>📞</span>
                  <span>{resource.phone}</span>
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Additional support */}
        {isUrgent && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
            <p className="text-sm text-yellow-900 leading-relaxed">
              <strong>If you're in immediate danger:</strong> Call emergency services (999 in Kenya, 911 in US, 112 in EU)
            </p>
          </div>
        )}

        {/* Reassurance */}
        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 italic text-center">
            {isUrgent
              ? 'Reaching out is a sign of strength, not weakness. Please call.'
              : 'These resources are here whenever you need them. You deserve support.'}
          </p>
        </div>
      </div>
    </ComponentWrapper>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getMessage(risk_level: string, isUrgent: boolean): string {
  if (risk_level === 'critical') {
    return "Based on patterns in your voice, we're very concerned about your safety. " +
           "Please reach out to one of these crisis resources immediately. " +
           "You matter, and people are ready to help right now.";
  }

  if (risk_level === 'high') {
    return "We've noticed concerning patterns in your voice over the last few sessions. " +
           "These resources can provide support 24/7. You don't have to handle everything alone.";
  }

  // Medium risk
  return "Mental health support is available if you need it. " +
         "Sometimes it helps to talk to someone trained to listen. " +
         "These resources are confidential and available 24/7.";
}
