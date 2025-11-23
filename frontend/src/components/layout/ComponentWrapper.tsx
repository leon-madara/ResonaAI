/**
 * Component Wrapper
 *
 * Wraps all components with appropriate styling based on prominence and urgency
 */

import React from 'react';
import { Prominence, Urgency } from '../../types';
import { getComponentWrapperClasses } from '../../theme/styles';

interface ComponentWrapperProps {
  prominence: Prominence;
  urgency: Urgency;
  children: React.ReactNode;
  className?: string;
}

export function ComponentWrapper({
  prominence,
  urgency,
  children,
  className = ''
}: ComponentWrapperProps) {
  // Hidden components don't render
  if (prominence === 'hidden') {
    return null;
  }

  const wrapperClasses = getComponentWrapperClasses(prominence, urgency);

  // Modal components use a portal-like overlay
  if (prominence === 'modal') {
    return (
      <div className={`${wrapperClasses} ${className}`} role="dialog" aria-modal="true">
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            {children}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${wrapperClasses} ${className}`}>
      {children}
    </div>
  );
}
