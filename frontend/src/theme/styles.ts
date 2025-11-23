/**
 * Style utilities for component prominence and urgency
 */

import { Prominence, Urgency } from '../types';

/**
 * Get CSS classes for component prominence
 */
export function getProminenceClasses(prominence: Prominence): string {
  const baseClasses = 'transition-all duration-[var(--animation-duration)]';

  switch (prominence) {
    case 'modal':
      return `${baseClasses} fixed inset-0 z-50 bg-[var(--color-background)] overflow-y-auto`;

    case 'top':
      return `${baseClasses} w-full mb-[calc(2rem*var(--spacing-scale))]`;

    case 'card':
      return `${baseClasses} bg-white rounded-lg shadow-md
              p-[calc(1.5rem*var(--spacing-scale))]
              mb-[calc(1rem*var(--spacing-scale))]
              border border-gray-200/[var(--contrast-level)]`;

    case 'sidebar':
      return `${baseClasses} bg-gray-50 rounded
              p-[calc(1rem*var(--spacing-scale))]
              mb-[calc(0.75rem*var(--spacing-scale))]`;

    case 'minimal':
      return `${baseClasses} text-sm text-gray-600
              mb-[calc(0.5rem*var(--spacing-scale))]`;

    case 'hidden':
      return 'hidden';

    default:
      return baseClasses;
  }
}

/**
 * Get CSS classes for urgency level
 */
export function getUrgencyClasses(urgency: Urgency): string {
  switch (urgency) {
    case 'critical':
      return 'border-l-4 border-[var(--color-warning)] bg-red-50/50 animate-pulse-slow';

    case 'high':
      return 'border-l-4 border-[var(--color-warning)]';

    case 'medium':
      return 'border-l-2 border-[var(--color-accent)]';

    case 'low':
    case 'none':
    default:
      return '';
  }
}

/**
 * Get combined classes for component wrapper
 */
export function getComponentWrapperClasses(
  prominence: Prominence,
  urgency: Urgency
): string {
  return `${getProminenceClasses(prominence)} ${getUrgencyClasses(urgency)}`.trim();
}

/**
 * Get spacing based on theme spacing scale
 */
export function getSpacing(baseSize: number): string {
  return `calc(${baseSize}rem * var(--spacing-scale))`;
}

/**
 * Get font size based on theme font scale
 */
export function getFontSize(baseSize: number): string {
  return `calc(${baseSize}rem * var(--font-scale))`;
}

/**
 * Get animation classes based on theme animations setting
 */
export function getAnimationClasses(animationType: 'fade' | 'slide' | 'scale' = 'fade'): string {
  const base = 'transition-all duration-[var(--animation-duration)] ease-[var(--animation-easing)]';

  switch (animationType) {
    case 'fade':
      return `${base} opacity-100 data-[entering]:opacity-0`;

    case 'slide':
      return `${base} translate-y-0 data-[entering]:translate-y-4`;

    case 'scale':
      return `${base} scale-100 data-[entering]:scale-95`;

    default:
      return base;
  }
}

/**
 * Get color based on urgency
 */
export function getUrgencyColor(urgency: Urgency): string {
  switch (urgency) {
    case 'critical':
      return 'var(--color-warning)';

    case 'high':
      return 'var(--color-secondary)';

    case 'medium':
      return 'var(--color-accent)';

    case 'low':
    case 'none':
    default:
      return 'var(--color-primary)';
  }
}

/**
 * Get responsive layout classes
 */
export function getResponsiveLayoutClasses(): {
  hero: string;
  primary: string;
  sidebar: string;
  footer: string;
} {
  return {
    hero: 'w-full mb-[calc(2rem*var(--spacing-scale))]',

    primary: `w-full lg:w-2/3 lg:pr-[calc(1rem*var(--spacing-scale))]`,

    sidebar: `w-full lg:w-1/3 lg:pl-[calc(1rem*var(--spacing-scale))]
              mt-[calc(1rem*var(--spacing-scale))] lg:mt-0`,

    footer: 'w-full mt-[calc(2rem*var(--spacing-scale))]'
  };
}
