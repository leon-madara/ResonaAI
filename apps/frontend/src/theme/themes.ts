/**
 * Theme Definitions
 * 
 * Complete theme system with support for:
 * - Emotional state themes (Anxiety, Depression, Crisis, Stable)
 * - Cultural themes (East African)
 * - Light and dark mode variants
 * - Typography, spacing, and animation scales
 */

export type ThemeName = 'anxiety' | 'depression' | 'crisis' | 'stable' | 'east-african' | 'neutral';
export type ColorMode = 'light' | 'dark';

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    tertiary: string;
  };
  accent: string;
  success: string;
  warning: string;
  danger: string;
}

export interface ThemeTypography {
  fontFamily: {
    primary: string;
    secondary: string;
  };
  scale: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
  };
  weight: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  lineHeight: number;
  letterSpacing: string;
}

export interface ThemeSpacing {
  unit: number;
  scale: 'compressed' | 'comfortable' | 'spacious' | 'standard' | 'generous';
  containerPadding: number;
  componentGap: number;
}

export interface ThemeBorderRadius {
  sm: string;
  md: string;
  lg: string;
  xl: string;
  round: string;
}

export interface ThemeShadows {
  sm: string;
  md: string;
  lg: string;
  none: string;
}

export interface ThemeAnimations {
  duration: {
    fast: string;
    normal: string;
    slow: string;
  };
  easing: string;
  preference: 'none' | 'gentle' | 'moderate' | 'standard' | 'reduced-motion';
}

export interface ThemeLayout {
  maxWidth: string;
  density: 'compact' | 'standard' | 'comfortable' | 'spacious';
}

export interface CompleteTheme {
  name: string;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  borderRadius: ThemeBorderRadius;
  shadows: ThemeShadows;
  animations: ThemeAnimations;
  layout: ThemeLayout;
}

// ============================================================================
// ANXIETY THEME
// ============================================================================

const anxietyThemeLight: CompleteTheme = {
  name: 'Calm',
  colors: {
    primary: '#4A90A4',
    secondary: '#7FB685',
    background: '#F5F9FA',
    surface: '#FFFFFF',
    text: {
      primary: '#2C3E50',
      secondary: '#7F8C8D',
      tertiary: '#BDC3C7',
    },
    accent: '#81C784',
    success: '#81C784',
    warning: '#FFA726',
    danger: '#EF5350',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: 1.6,
    letterSpacing: '0.01em',
  },
  spacing: {
    unit: 8,
    scale: 'generous',
    containerPadding: 24,
    componentGap: 24,
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    round: '50%',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.05)',
    md: '0 4px 8px rgba(0,0,0,0.08)',
    lg: '0 8px 16px rgba(0,0,0,0.12)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '200ms',
      normal: '400ms',
      slow: '600ms',
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'reduced-motion',
  },
  layout: {
    maxWidth: '800px',
    density: 'spacious',
  },
};

const anxietyThemeDark: CompleteTheme = {
  ...anxietyThemeLight,
  colors: {
    primary: '#6BB6C7',
    secondary: '#9FD4A5',
    background: '#1A1F24',
    surface: '#252B32',
    text: {
      primary: '#E8EAED',
      secondary: '#B0B5BA',
      tertiary: '#7F8C8D',
    },
    accent: '#A5D6A7',
    success: '#A5D6A7',
    warning: '#FFB74D',
    danger: '#EF5350',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.3)',
    md: '0 4px 8px rgba(0,0,0,0.4)',
    lg: '0 8px 16px rgba(0,0,0,0.5)',
    none: 'none',
  },
};

// ============================================================================
// DEPRESSION THEME
// ============================================================================

const depressionThemeLight: CompleteTheme = {
  name: 'Warmth',
  colors: {
    primary: '#E07A5F',
    secondary: '#F2CC8F',
    background: '#FFF9F5',
    surface: '#FFFFFF',
    text: {
      primary: '#3D2817',
      secondary: '#8B6F47',
      tertiary: '#C9B189',
    },
    accent: '#F4A261',
    success: '#E9C46A',
    warning: '#E76F51',
    danger: '#D62828',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: 1.5,
    letterSpacing: 'normal',
  },
  spacing: {
    unit: 8,
    scale: 'comfortable',
    containerPadding: 20,
    componentGap: 20,
  },
  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px',
    round: '50%',
  },
  shadows: {
    sm: '0 2px 6px rgba(224, 122, 95, 0.1)',
    md: '0 4px 12px rgba(224, 122, 95, 0.15)',
    lg: '0 8px 20px rgba(224, 122, 95, 0.2)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms',
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'gentle',
  },
  layout: {
    maxWidth: '900px',
    density: 'comfortable',
  },
};

const depressionThemeDark: CompleteTheme = {
  ...depressionThemeLight,
  colors: {
    primary: '#F4A261',
    secondary: '#F9D5A7',
    background: '#2A1F17',
    surface: '#3D2B1F',
    text: {
      primary: '#F5E6D3',
      secondary: '#D4B896',
      tertiary: '#B89A7A',
    },
    accent: '#F6B85A',
    success: '#F2C94C',
    warning: '#F17A5A',
    danger: '#E63946',
  },
  shadows: {
    sm: '0 2px 6px rgba(0,0,0,0.3)',
    md: '0 4px 12px rgba(0,0,0,0.4)',
    lg: '0 8px 20px rgba(0,0,0,0.5)',
    none: 'none',
  },
};

// ============================================================================
// CRISIS THEME
// ============================================================================

const crisisThemeLight: CompleteTheme = {
  name: 'Clarity',
  colors: {
    primary: '#D62828',
    secondary: '#003049',
    background: '#FFFFFF',
    surface: '#F8F9FA',
    text: {
      primary: '#000000',
      secondary: '#495057',
      tertiary: '#6C757D',
    },
    accent: '#F77F00',
    success: '#06A77D',
    warning: '#E76F51',
    danger: '#D62828',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Inter, sans-serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.25rem',
      xl: '1.5rem',
      '2xl': '2rem',
      '3xl': '2.5rem',
    },
    weight: {
      normal: 400,
      medium: 600,
      semibold: 700,
      bold: 800,
    },
    lineHeight: 1.4,
    letterSpacing: 'normal',
  },
  spacing: {
    unit: 8,
    scale: 'compressed',
    containerPadding: 16,
    componentGap: 16,
  },
  borderRadius: {
    sm: '4px',
    md: '6px',
    lg: '8px',
    xl: '12px',
    round: '50%',
  },
  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.12)',
    md: '0 2px 6px rgba(0,0,0,0.16)',
    lg: '0 4px 12px rgba(0,0,0,0.2)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '100ms',
      normal: '200ms',
      slow: '300ms',
    },
    easing: 'ease-out',
    preference: 'none',
  },
  layout: {
    maxWidth: '700px',
    density: 'compact',
  },
};

const crisisThemeDark: CompleteTheme = {
  ...crisisThemeLight,
  colors: {
    primary: '#FF4444',
    secondary: '#004D73',
    background: '#0A0A0A',
    surface: '#1A1A1A',
    text: {
      primary: '#FFFFFF',
      secondary: '#CCCCCC',
      tertiary: '#999999',
    },
    accent: '#FF8800',
    success: '#00D9A5',
    warning: '#FF6B4A',
    danger: '#FF4444',
  },
  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.5)',
    md: '0 2px 6px rgba(0,0,0,0.6)',
    lg: '0 4px 12px rgba(0,0,0,0.7)',
    none: 'none',
  },
};

// ============================================================================
// STABLE THEME
// ============================================================================

const stableThemeLight: CompleteTheme = {
  name: 'Balance',
  colors: {
    primary: '#2A9D8F',
    secondary: '#264653',
    background: '#F8F9FA',
    surface: '#FFFFFF',
    text: {
      primary: '#212529',
      secondary: '#495057',
      tertiary: '#6C757D',
    },
    accent: '#E76F51',
    success: '#06A77D',
    warning: '#F4A261',
    danger: '#E63946',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: 1.5,
    letterSpacing: 'normal',
  },
  spacing: {
    unit: 8,
    scale: 'standard',
    containerPadding: 20,
    componentGap: 20,
  },
  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px',
    round: '50%',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.06)',
    md: '0 4px 8px rgba(0,0,0,0.1)',
    lg: '0 8px 16px rgba(0,0,0,0.15)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms',
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'standard',
  },
  layout: {
    maxWidth: '1000px',
    density: 'standard',
  },
};

const stableThemeDark: CompleteTheme = {
  ...stableThemeLight,
  colors: {
    primary: '#4ECDC4',
    secondary: '#3A5F6F',
    background: '#1A1F24',
    surface: '#252B32',
    text: {
      primary: '#E8EAED',
      secondary: '#B0B5BA',
      tertiary: '#7F8C8D',
    },
    accent: '#F17A5A',
    success: '#00D9A5',
    warning: '#F6B85A',
    danger: '#FF6B6B',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.3)',
    md: '0 4px 8px rgba(0,0,0,0.4)',
    lg: '0 8px 16px rgba(0,0,0,0.5)',
    none: 'none',
  },
};

// ============================================================================
// EAST AFRICAN THEME
// ============================================================================

const eastAfricanThemeLight: CompleteTheme = {
  name: 'East African Context',
  colors: {
    primary: '#E07A5F',
    secondary: '#F2CC8F',
    background: '#FFF9F5',
    surface: '#FFFFFF',
    text: {
      primary: '#3D2817',
      secondary: '#8B6F47',
      tertiary: '#C9B189',
    },
    accent: '#F4A261',
    success: '#81B29A',
    warning: '#E76F51',
    danger: '#D62828',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: 1.5,
    letterSpacing: 'normal',
  },
  spacing: {
    unit: 8,
    scale: 'comfortable',
    containerPadding: 20,
    componentGap: 20,
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    round: '50%',
  },
  shadows: {
    sm: '0 2px 6px rgba(224, 122, 95, 0.1)',
    md: '0 4px 12px rgba(224, 122, 95, 0.15)',
    lg: '0 8px 20px rgba(224, 122, 95, 0.2)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms',
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'gentle',
  },
  layout: {
    maxWidth: '900px',
    density: 'comfortable',
  },
};

const eastAfricanThemeDark: CompleteTheme = {
  ...eastAfricanThemeLight,
  colors: {
    primary: '#F4A261',
    secondary: '#F9D5A7',
    background: '#2A1F17',
    surface: '#3D2B1F',
    text: {
      primary: '#F5E6D3',
      secondary: '#D4B896',
      tertiary: '#B89A7A',
    },
    accent: '#F6B85A',
    success: '#A5D6A7',
    warning: '#F17A5A',
    danger: '#E63946',
  },
  shadows: {
    sm: '0 2px 6px rgba(0,0,0,0.3)',
    md: '0 4px 12px rgba(0,0,0,0.4)',
    lg: '0 8px 20px rgba(0,0,0,0.5)',
    none: 'none',
  },
};

// ============================================================================
// NEUTRAL THEME (Default)
// ============================================================================

const neutralThemeLight: CompleteTheme = {
  name: 'Neutral',
  colors: {
    primary: '#6366F1',
    secondary: '#8B5CF6',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: {
      primary: '#111827',
      secondary: '#6B7280',
      tertiary: '#9CA3AF',
    },
    accent: '#10B981',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Inter, sans-serif',
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: 1.5,
    letterSpacing: 'normal',
  },
  spacing: {
    unit: 8,
    scale: 'standard',
    containerPadding: 20,
    componentGap: 20,
  },
  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px',
    round: '50%',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.06)',
    md: '0 4px 8px rgba(0,0,0,0.1)',
    lg: '0 8px 16px rgba(0,0,0,0.15)',
    none: 'none',
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms',
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'standard',
  },
  layout: {
    maxWidth: '1000px',
    density: 'standard',
  },
};

const neutralThemeDark: CompleteTheme = {
  ...neutralThemeLight,
  colors: {
    primary: '#818CF8',
    secondary: '#A78BFA',
    background: '#111827',
    surface: '#1F2937',
    text: {
      primary: '#F9FAFB',
      secondary: '#D1D5DB',
      tertiary: '#9CA3AF',
    },
    accent: '#34D399',
    success: '#34D399',
    warning: '#FBBF24',
    danger: '#F87171',
  },
  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.3)',
    md: '0 4px 8px rgba(0,0,0,0.4)',
    lg: '0 8px 16px rgba(0,0,0,0.5)',
    none: 'none',
  },
};

// ============================================================================
// THEME REGISTRY
// ============================================================================

export const themes: Record<ThemeName, Record<ColorMode, CompleteTheme>> = {
  anxiety: {
    light: anxietyThemeLight,
    dark: anxietyThemeDark,
  },
  depression: {
    light: depressionThemeLight,
    dark: depressionThemeDark,
  },
  crisis: {
    light: crisisThemeLight,
    dark: crisisThemeDark,
  },
  stable: {
    light: stableThemeLight,
    dark: stableThemeDark,
  },
  'east-african': {
    light: eastAfricanThemeLight,
    dark: eastAfricanThemeDark,
  },
  neutral: {
    light: neutralThemeLight,
    dark: neutralThemeDark,
  },
};

/**
 * Get theme by name and color mode
 */
export function getTheme(themeName: ThemeName, colorMode: ColorMode): CompleteTheme {
  return themes[themeName]?.[colorMode] || themes.neutral[colorMode];
}

/**
 * Apply theme CSS variables to document root
 */
export function applyTheme(theme: CompleteTheme, colorMode: ColorMode): void {
  const root = document.documentElement;
  
  // Apply color variables
  root.style.setProperty('--color-primary', theme.colors.primary);
  root.style.setProperty('--color-secondary', theme.colors.secondary);
  root.style.setProperty('--color-background', theme.colors.background);
  root.style.setProperty('--color-surface', theme.colors.surface);
  root.style.setProperty('--color-text-primary', theme.colors.text.primary);
  root.style.setProperty('--color-text-secondary', theme.colors.text.secondary);
  root.style.setProperty('--color-text-tertiary', theme.colors.text.tertiary);
  root.style.setProperty('--color-accent', theme.colors.accent);
  root.style.setProperty('--color-success', theme.colors.success);
  root.style.setProperty('--color-warning', theme.colors.warning);
  root.style.setProperty('--color-danger', theme.colors.danger);
  
  // Apply typography variables
  root.style.setProperty('--font-family-primary', theme.typography.fontFamily.primary);
  root.style.setProperty('--font-family-secondary', theme.typography.fontFamily.secondary);
  root.style.setProperty('--font-size-xs', theme.typography.scale.xs);
  root.style.setProperty('--font-size-sm', theme.typography.scale.sm);
  root.style.setProperty('--font-size-base', theme.typography.scale.base);
  root.style.setProperty('--font-size-lg', theme.typography.scale.lg);
  root.style.setProperty('--font-size-xl', theme.typography.scale.xl);
  root.style.setProperty('--font-size-2xl', theme.typography.scale['2xl']);
  root.style.setProperty('--font-size-3xl', theme.typography.scale['3xl']);
  root.style.setProperty('--font-weight-normal', theme.typography.weight.normal.toString());
  root.style.setProperty('--font-weight-medium', theme.typography.weight.medium.toString());
  root.style.setProperty('--font-weight-semibold', theme.typography.weight.semibold.toString());
  root.style.setProperty('--font-weight-bold', theme.typography.weight.bold.toString());
  root.style.setProperty('--line-height', theme.typography.lineHeight.toString());
  root.style.setProperty('--letter-spacing', theme.typography.letterSpacing);
  
  // Apply spacing variables
  root.style.setProperty('--spacing-unit', `${theme.spacing.unit}px`);
  root.style.setProperty('--spacing-container-padding', `${theme.spacing.containerPadding}px`);
  root.style.setProperty('--spacing-component-gap', `${theme.spacing.componentGap}px`);
  
  // Apply border radius variables
  root.style.setProperty('--border-radius-sm', theme.borderRadius.sm);
  root.style.setProperty('--border-radius-md', theme.borderRadius.md);
  root.style.setProperty('--border-radius-lg', theme.borderRadius.lg);
  root.style.setProperty('--border-radius-xl', theme.borderRadius.xl);
  root.style.setProperty('--border-radius-round', theme.borderRadius.round);
  
  // Apply shadow variables
  root.style.setProperty('--shadow-sm', theme.shadows.sm);
  root.style.setProperty('--shadow-md', theme.shadows.md);
  root.style.setProperty('--shadow-lg', theme.shadows.lg);
  root.style.setProperty('--shadow-none', theme.shadows.none);
  
  // Apply animation variables
  root.style.setProperty('--animation-duration-fast', theme.animations.duration.fast);
  root.style.setProperty('--animation-duration-normal', theme.animations.duration.normal);
  root.style.setProperty('--animation-duration-slow', theme.animations.duration.slow);
  root.style.setProperty('--animation-easing', theme.animations.easing);
  
  // Apply layout variables
  root.style.setProperty('--layout-max-width', theme.layout.maxWidth);
  
  // Add theme class
  root.classList.remove('theme-anxiety', 'theme-depression', 'theme-crisis', 'theme-stable', 'theme-east-african', 'theme-neutral');
  root.classList.add(`theme-${theme.name.toLowerCase().replace(/\s+/g, '-')}`);
  
  // Add color mode class
  root.classList.remove('light', 'dark');
  root.classList.add(colorMode);
}

