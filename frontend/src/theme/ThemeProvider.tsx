/**
 * Theme Provider
 *
 * Provides theme context to all components
 * Theme is dynamically loaded from UIConfig (not hardcoded)
 */

import React, { createContext, useContext, useMemo } from 'react';
import { ThemeConfig } from '../types';

interface ThemeContextValue {
  theme: ThemeConfig;
  cssVariables: React.CSSProperties;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

interface ThemeProviderProps {
  theme: ThemeConfig;
  children: React.ReactNode;
}

export function ThemeProvider({ theme, children }: ThemeProviderProps) {
  // Convert theme to CSS variables
  const cssVariables = useMemo(() => {
    return {
      // Colors
      '--color-primary': theme.colors.primary,
      '--color-secondary': theme.colors.secondary,
      '--color-background': theme.colors.background,
      '--color-text': theme.colors.text,
      '--color-accent': theme.colors.accent,
      '--color-warning': theme.colors.warning,

      // Spacing
      '--spacing-scale': theme.spacing === 'spacious' ? '1.5' :
                         theme.spacing === 'compressed' ? '0.75' : '1',

      // Animations
      '--animation-duration': theme.animations === 'none' ? '0s' :
                              theme.animations === 'gentle' ? '0.8s' : '0.4s',
      '--animation-easing': theme.animations === 'gentle' ? 'ease-out' : 'ease-in-out',

      // Typography
      '--font-scale': theme.fontScale.toString(),

      // Contrast (for borders, shadows)
      '--contrast-level': theme.contrast === 'high' ? '1' :
                          theme.contrast === 'low' ? '0.3' : '0.6',

    } as React.CSSProperties;
  }, [theme]);

  const contextValue = useMemo(() => ({
    theme,
    cssVariables
  }), [theme, cssVariables]);

  return (
    <ThemeContext.Provider value={contextValue}>
      <div
        className="app-root"
        style={cssVariables}
        data-theme={theme.base}
        data-contrast={theme.contrast}
      >
        {children}
      </div>
    </ThemeContext.Provider>
  );
}
