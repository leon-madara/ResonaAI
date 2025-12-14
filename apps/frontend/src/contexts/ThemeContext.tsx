import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getTheme, applyTheme, ThemeName, ColorMode, CompleteTheme } from '../theme/themes';

type Theme = 'light' | 'dark' | 'system';
type AdaptiveTheme = 'stable' | 'anxiety' | 'depression' | 'crisis' | 'neutral' | 'east-african';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  actualTheme: 'light' | 'dark';
  adaptiveTheme: AdaptiveTheme;
  setAdaptiveTheme: (theme: AdaptiveTheme) => void;
  currentTheme: CompleteTheme;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('system');
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light');
  const [adaptiveTheme, setAdaptiveTheme] = useState<AdaptiveTheme>('neutral');

  useEffect(() => {
    // Load theme from localStorage
    const storedTheme = localStorage.getItem('theme') as Theme;
    if (storedTheme) {
      setTheme(storedTheme);
    }
    
    // Load adaptive theme from localStorage
    const storedAdaptiveTheme = localStorage.getItem('adaptiveTheme') as AdaptiveTheme;
    if (storedAdaptiveTheme) {
      setAdaptiveTheme(storedAdaptiveTheme);
    }
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    
    let resolvedTheme: 'light' | 'dark';
    
    if (theme === 'system') {
      resolvedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } else {
      resolvedTheme = theme;
    }
    
    setActualTheme(resolvedTheme);
    
    // Remove previous theme classes
    root.classList.remove('light', 'dark');
    
    // Add current theme class
    root.classList.add(resolvedTheme);
    
    // Add adaptive theme class
    root.classList.remove('theme-stable', 'theme-anxiety', 'theme-depression', 'theme-crisis', 'theme-neutral', 'theme-east-african');
    root.classList.add(`theme-${adaptiveTheme}`);
    
    // Store theme preference
    localStorage.setItem('theme', theme);
    localStorage.setItem('adaptiveTheme', adaptiveTheme);
    
    // Apply theme with typography, spacing, and animation systems
    const themeName: ThemeName = adaptiveTheme === 'east-african' ? 'east-african' : 
                                 adaptiveTheme === 'anxiety' ? 'anxiety' :
                                 adaptiveTheme === 'depression' ? 'depression' :
                                 adaptiveTheme === 'crisis' ? 'crisis' :
                                 adaptiveTheme === 'stable' ? 'stable' : 'neutral';
    const colorMode: ColorMode = resolvedTheme;
    const completeTheme = getTheme(themeName, colorMode);
    applyTheme(completeTheme, colorMode);
  }, [theme, adaptiveTheme]);

  useEffect(() => {
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      if (theme === 'system') {
        const newTheme = mediaQuery.matches ? 'dark' : 'light';
        setActualTheme(newTheme);
        
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');
        root.classList.add(newTheme);
        
        // Re-apply theme with new color mode
        const themeName: ThemeName = adaptiveTheme === 'east-african' ? 'east-african' : 
                                     adaptiveTheme === 'anxiety' ? 'anxiety' :
                                     adaptiveTheme === 'depression' ? 'depression' :
                                     adaptiveTheme === 'crisis' ? 'crisis' :
                                     adaptiveTheme === 'stable' ? 'stable' : 'neutral';
        const completeTheme = getTheme(themeName, newTheme);
        applyTheme(completeTheme, newTheme);
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [theme, adaptiveTheme]);

  // Get current theme for context
  const themeName: ThemeName = adaptiveTheme === 'east-african' ? 'east-african' : 
                               adaptiveTheme === 'anxiety' ? 'anxiety' :
                               adaptiveTheme === 'depression' ? 'depression' :
                               adaptiveTheme === 'crisis' ? 'crisis' :
                               adaptiveTheme === 'stable' ? 'stable' : 'neutral';
  const currentTheme = getTheme(themeName, actualTheme);

  const value: ThemeContextType = {
    theme,
    setTheme,
    actualTheme,
    adaptiveTheme,
    setAdaptiveTheme,
    currentTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
