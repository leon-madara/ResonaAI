/**
 * Safety Check Component
 *
 * Direct safety assessment for CRITICAL risk
 * Modal prominence - takes over full screen
 */

import React, { useState } from 'react';
import { SafetyCheckProps } from '../../types';
import { ComponentWrapper } from '../layout/ComponentWrapper';

export function SafetyCheck({
  questions,
  resources_immediate,
  prominence,
  urgency
}: SafetyCheckProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});

  const handleAnswer = (answer: 'yes' | 'no' | 'unsure') => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion]: answer
    }));

    // If answered "yes" to safety concern or last question, show resources
    if (answer === 'yes' || currentQuestion === questions.length - 1) {
      // Show crisis resources immediately
      return;
    }

    // Move to next question
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const answeredAll = currentQuestion === questions.length - 1 && answers[currentQuestion];

  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl mx-auto p-8 space-y-6">
        {/* Urgent header */}
        <div className="text-center space-y-4">
          <div className="text-6xl">🆘</div>
          <h2
            className="font-bold text-gray-900"
            style={{ fontSize: 'calc(2rem * var(--font-scale))' }}
          >
            We need to check in with you
          </h2>
          <p className="text-gray-600 text-lg">
            Your voice shows patterns that concern us. Please answer honestly.
          </p>
        </div>

        {/* Safety questions */}
        <div className="bg-red-50 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-red-600 font-semibold">
              Question {currentQuestion + 1} of {questions.length}
            </div>
            <div className="flex gap-1">
              {questions.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index <= currentQuestion ? 'bg-red-500' : 'bg-red-200'
                  }`}
                />
              ))}
            </div>
          </div>

          <h3
            className="font-semibold text-red-900"
            style={{ fontSize: 'calc(1.5rem * var(--font-scale))' }}
          >
            {questions[currentQuestion]}
          </h3>

          {/* Answer buttons */}
          <div className="grid grid-cols-3 gap-3 pt-4">
            <button
              onClick={() => handleAnswer('yes')}
              className="py-4 px-6 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold
                         transition-colors shadow-lg hover:shadow-xl"
            >
              Yes
            </button>
            <button
              onClick={() => handleAnswer('unsure')}
              className="py-4 px-6 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-semibold
                         transition-colors shadow-lg hover:shadow-xl"
            >
              Unsure
            </button>
            <button
              onClick={() => handleAnswer('no')}
              className="py-4 px-6 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-semibold
                         transition-colors shadow-lg hover:shadow-xl"
            >
              No
            </button>
          </div>
        </div>

        {/* Crisis resources (always visible) */}
        {resources_immediate && (
          <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="text-3xl">📞</div>
              <div>
                <div className="font-bold text-gray-900 text-lg">
                  Need immediate help?
                </div>
                <div className="text-sm text-gray-600">
                  These crisis lines are available 24/7
                </div>
              </div>
            </div>

            {/* Kenya crisis lines */}
            <div className="space-y-2">
              <a
                href="tel:1199"
                className="block bg-red-600 hover:bg-red-700 text-white rounded-lg p-4
                           font-semibold text-center transition-colors shadow-lg hover:shadow-xl"
              >
                <div className="text-xl">Kenya Red Cross: 1199</div>
                <div className="text-sm opacity-90">24/7 Counseling</div>
              </a>

              <a
                href="tel:+254722178177"
                className="block bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-4
                           font-semibold text-center transition-colors shadow-lg hover:shadow-xl"
              >
                <div className="text-xl">Befrienders Kenya: +254 722 178 177</div>
                <div className="text-sm opacity-90">24/7 Emotional Support</div>
              </a>
            </div>

            <div className="text-xs text-gray-600 text-center pt-2 border-t border-yellow-200">
              <strong>Emergency:</strong> If in immediate danger, call 999 (Kenya) or your local emergency number
            </div>
          </div>
        )}

        {/* Reassurance */}
        <div className="text-center text-sm text-gray-600 space-y-2">
          <p className="font-semibold">You are not alone.</p>
          <p>
            Reaching out for help is one of the bravest things you can do.
            These resources are confidential and here to support you.
          </p>
        </div>
      </div>
    </ComponentWrapper>
  );
}
