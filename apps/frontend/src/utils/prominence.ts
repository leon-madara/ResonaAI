/**
 * Prominence-Based Rendering Utilities
 * 
 * Provides utilities for rendering components based on prominence levels:
 * - modal: Full-screen overlay, blocks interaction
 * - top: Hero section, full width
 * - card: Primary section, elevated card
 * - sidebar: Sidebar, less prominent
 * - minimal: Footer, subtle
 * - hidden: Not rendered
 */

import { Prominence, Urgency } from '../types';
import { useTheme } from '../contexts/ThemeContext';

/**
 * Get CSS classes for component prominence
 */
export function getProminenceClasses(prominence: Prominence, urgency: Urgency = 'none'): string {
  const baseClasses = 'transition-all';
  
  // Get animation duration from CSS variable
  const animationClass = 'duration-[var(--animation-duration-normal)]';
  
  switch (prominence) {
    case 'modal':
      return `${baseClasses} ${animationClass} fixed inset-0 z-50 bg-[var(--color-background)] overflow-y-auto backdrop-blur-sm`;
    
    case 'top':
      return `${baseClasses} ${animationClass} w-full mb-[var(--spacing-component-gap)]`;
    
    case 'card':
      return `${baseClasses} ${animationClass} bg-[var(--color-surface)] rounded-[var(--border-radius-lg)] shadow-[var(--shadow-md)]
              p-[var(--spacing-container-padding)]
              mb-[var(--spacing-component-gap)]
              border border-[var(--color-text-tertiary)]/20`;
    
    case 'sidebar':
      return `${baseClasses} ${animationClass} bg-[var(--color-surface)]/50 rounded-[var(--border-radius-md)]
              p-[calc(var(--spacing-container-padding)*0.75)]
              mb-[calc(var(--spacing-component-gap)*0.75)]`;
    
    case 'minimal':
      return `${baseClasses} ${animationClass} text-[var(--font-size-sm)] text-[var(--color-text-secondary)]
              mb-[calc(var(--spacing-component-gap)*0.5)]`;
    
    case 'hidden':
      return 'hidden';
    
    default:
      return `${baseClasses} ${animationClass}`;
  }
}

/**
 * Get urgency-based styling classes
 */
export function getUrgencyClasses(urgency: Urgency): string {
  switch (urgency) {
    case 'critical':
      return 'border-l-4 border-[var(--color-danger)] bg-[var(--color-danger)]/10 animate-pulse';
    
    case 'high':
      return 'border-l-4 border-[var(--color-warning)] bg-[var(--color-warning)]/5';
    
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
  urgency: Urgency = 'none'
): string {
  const prominenceClasses = getProminenceClasses(prominence, urgency);
  const urgencyClasses = getUrgencyClasses(urgency);
  
  return `${prominenceClasses} ${urgencyClasses}`.trim();
}

/**
 * Check if component should be rendered based on prominence
 */
export function shouldRenderComponent(prominence: Prominence, visible: boolean = true): boolean {
  return visible && prominence !== 'hidden';
}

/**
 * Get prominence-specific container styles
 */
export function getProminenceContainerStyles(prominence: Prominence): React.CSSProperties {
  switch (prominence) {
    case 'modal':
      return {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--spacing-container-padding)',
      };
    
    case 'top':
      return {
        width: '100%',
        marginBottom: 'var(--spacing-component-gap)',
      };
    
    case 'card':
      return {
        width: '100%',
        marginBottom: 'var(--spacing-component-gap)',
      };
    
    case 'sidebar':
      return {
        width: '100%',
        marginBottom: 'calc(var(--spacing-component-gap) * 0.75)',
      };
    
    case 'minimal':
      return {
        width: '100%',
        marginBottom: 'calc(var(--spacing-component-gap) * 0.5)',
      };
    
    case 'hidden':
    default:
      return {
        display: 'none',
      };
  }
}

/**
 * Hook to get prominence utilities with current theme
 */
export function useProminence() {
  const { currentTheme } = useTheme();
  
  return {
    /**
     * Get prominence classes
     */
    getClasses: (prominence: Prominence, urgency: Urgency = 'none') => {
      return getComponentWrapperClasses(prominence, urgency);
    },
    
    /**
     * Get prominence container styles
     */
    getStyles: (prominence: Prominence) => {
      return getProminenceContainerStyles(prominence);
    },
    
    /**
     * Check if should render
     */
    shouldRender: (prominence: Prominence, visible: boolean = true) => {
      return shouldRenderComponent(prominence, visible);
    },
  };
}

