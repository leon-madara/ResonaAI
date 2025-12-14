/**
 * Spacing System Utilities
 * 
 * Provides responsive spacing utilities based on theme spacing scale
 * Supports compressed, comfortable, spacious, standard, and generous scales
 */

import { useTheme } from '../contexts/ThemeContext';

/**
 * Get spacing multiplier based on theme scale
 */
export function getSpacingMultiplier(scale: string): number {
  switch (scale) {
    case 'compressed':
      return 0.75;
    case 'comfortable':
      return 1.0;
    case 'spacious':
      return 1.5;
    case 'generous':
      return 2.0;
    case 'standard':
    default:
      return 1.0;
  }
}

/**
 * Get responsive spacing value
 * @param baseSize Base size in pixels (typically 4px, 8px, 16px, etc.)
 * @param scale Theme spacing scale
 * @returns CSS calc expression for responsive spacing
 */
export function getResponsiveSpacing(baseSize: number, scale: string = 'standard'): string {
  const multiplier = getSpacingMultiplier(scale);
  return `calc(${baseSize}px * ${multiplier})`;
}

/**
 * Get spacing scale CSS variable value
 */
export function getSpacingScale(scale: string): string {
  return getSpacingMultiplier(scale).toString();
}

/**
 * Predefined spacing values based on 8px unit system
 */
export const spacing = {
  xs: 4,    // 4px
  sm: 8,    // 8px
  md: 16,   // 16px
  lg: 24,   // 24px
  xl: 32,   // 32px
  '2xl': 48, // 48px
  '3xl': 64, // 64px
} as const;

/**
 * Hook to get spacing utilities with current theme
 */
export function useSpacing() {
  const { currentTheme } = useTheme();
  const scale = currentTheme.spacing.scale;
  
  return {
    /**
     * Get spacing value with theme scale applied
     */
    get: (size: keyof typeof spacing | number): string => {
      const baseSize = typeof size === 'number' ? size : spacing[size];
      return getResponsiveSpacing(baseSize, scale);
    },
    
    /**
     * Get container padding
     */
    container: getResponsiveSpacing(currentTheme.spacing.containerPadding, scale),
    
    /**
     * Get component gap
     */
    gap: getResponsiveSpacing(currentTheme.spacing.componentGap, scale),
    
    /**
     * Get spacing unit
     */
    unit: currentTheme.spacing.unit,
    
    /**
     * Get scale multiplier
     */
    scale: getSpacingMultiplier(scale),
  };
}

