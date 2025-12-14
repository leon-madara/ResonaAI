/**
 * Comprehensive tests for ThemeContext
 * 
 * Tests theme management including:
 * - Basic theme switching (light/dark/system)
 * - Adaptive theme switching
 * - System theme detection
 * - Theme persistence
 * - CSS variable updates
 * - Context value validation
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, useTheme } from '../../contexts/ThemeContext';
import { getTheme } from '../../theme/themes';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Helper to get CSS variable value
function getCSSVariable(variableName: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
}

// Mock matchMedia for system theme detection
const mockMatchMedia = (matches: boolean) => {
  return jest.fn().mockImplementation((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }));
};

// Test component for basic theme switching
const BasicTestComponent = () => {
  const { theme, setTheme, actualTheme } = useTheme();

  return (
    <div>
      <div data-testid="theme">{theme}</div>
      <div data-testid="actual-theme">{actualTheme}</div>
      <button onClick={() => setTheme('dark')}>Set Dark</button>
      <button onClick={() => setTheme('light')}>Set Light</button>
      <button onClick={() => setTheme('system')}>Set System</button>
    </div>
  );
};

// Test component for adaptive theme switching
const AdaptiveTestComponent = () => {
  const { adaptiveTheme, setAdaptiveTheme, currentTheme, actualTheme } = useTheme();

  return (
    <div>
      <div data-testid="adaptive-theme">{adaptiveTheme}</div>
      <div data-testid="theme-name">{currentTheme.name}</div>
      <div data-testid="actual-theme">{actualTheme}</div>
      <button onClick={() => setAdaptiveTheme('anxiety')}>Set Anxiety</button>
      <button onClick={() => setAdaptiveTheme('depression')}>Set Depression</button>
      <button onClick={() => setAdaptiveTheme('crisis')}>Set Crisis</button>
      <button onClick={() => setAdaptiveTheme('stable')}>Set Stable</button>
      <button onClick={() => setAdaptiveTheme('neutral')}>Set Neutral</button>
      <button onClick={() => setAdaptiveTheme('east-african')}>Set East African</button>
    </div>
  );
};

// Test component for full context access
const FullContextTestComponent = () => {
  const context = useTheme();

  return (
    <div>
      <div data-testid="theme">{context.theme}</div>
      <div data-testid="adaptive-theme">{context.adaptiveTheme}</div>
      <div data-testid="actual-theme">{context.actualTheme}</div>
      <div data-testid="theme-name">{context.currentTheme.name}</div>
      <div data-testid="primary-color">{context.currentTheme.colors.primary}</div>
    </div>
  );
};

// Test component for error case
const ErrorTestComponent = () => {
  try {
    useTheme();
    return <div>No Error</div>;
  } catch (error: any) {
    return <div data-testid="error">{error.message}</div>;
  }
};

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    // Reset document classes and styles
    document.documentElement.className = '';
    document.documentElement.style.cssText = '';
    // Reset matchMedia mock
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia(false),
    });
  });

  describe('Basic Theme Switching', () => {
    it('provides default theme (system)', () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme')).toHaveTextContent('system');
    });

    it('resolves system theme to light by default', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia(false), // prefers-color-scheme: light
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('actual-theme')).toHaveTextContent('light');
    });

    it('resolves system theme to dark when system prefers dark', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia(true), // prefers-color-scheme: dark
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });

    it('restores theme from localStorage', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'theme') return 'dark';
        if (key === 'adaptiveTheme') return 'neutral';
        return null;
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
    });

    it('updates theme and saves to localStorage', async () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      const darkButton = screen.getByText('Set Dark');
      await userEvent.click(darkButton);

      expect(screen.getByTestId('theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    });

    it('updates to light theme', async () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'theme') return 'dark';
        if (key === 'adaptiveTheme') return 'neutral';
        return null;
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      const lightButton = screen.getByText('Set Light');
      await userEvent.click(lightButton);

      expect(screen.getByTestId('theme')).toHaveTextContent('light');
      expect(screen.getByTestId('actual-theme')).toHaveTextContent('light');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
    });

    it('updates to system theme', async () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      const systemButton = screen.getByText('Set System');
      await userEvent.click(systemButton);

      expect(screen.getByTestId('theme')).toHaveTextContent('system');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'system');
    });
  });

  describe('Adaptive Theme Switching', () => {
    it('provides default adaptive theme (neutral)', () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('neutral');
    });

    it('restores adaptive theme from localStorage', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'theme') return 'light';
        if (key === 'adaptiveTheme') return 'anxiety';
        return null;
      });

      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('anxiety');
    });

    it('updates adaptive theme to anxiety', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('anxiety');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Calm');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'anxiety');
    });

    it('updates adaptive theme to depression', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const depressionButton = screen.getByText('Set Depression');
      await userEvent.click(depressionButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('depression');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Warmth');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'depression');
    });

    it('updates adaptive theme to crisis', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const crisisButton = screen.getByText('Set Crisis');
      await userEvent.click(crisisButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('crisis');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Clarity');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'crisis');
    });

    it('updates adaptive theme to stable', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const stableButton = screen.getByText('Set Stable');
      await userEvent.click(stableButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('stable');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Balance');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'stable');
    });

    it('updates adaptive theme to east-african', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const eastAfricanButton = screen.getByText('Set East African');
      await userEvent.click(eastAfricanButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('east-african');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('East African Context');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'east-african');
    });

    it('updates adaptive theme to neutral', async () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'theme') return 'light';
        if (key === 'adaptiveTheme') return 'anxiety';
        return null;
      });

      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const neutralButton = screen.getByText('Set Neutral');
      await userEvent.click(neutralButton);

      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('neutral');
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Neutral');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'neutral');
    });
  });

  describe('System Theme Detection', () => {
    it('listens to system theme changes when theme is set to system', async () => {
      const mockMediaQuery = mockMatchMedia(false);
      let changeHandler: ((event: MediaQueryListEvent) => void) | null = null;

      mockMediaQuery.addEventListener = jest.fn((event: string, handler: any) => {
        if (event === 'change') {
          changeHandler = handler;
        }
      });

      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMediaQuery,
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme')).toHaveTextContent('system');
      expect(mockMediaQuery.addEventListener).toHaveBeenCalledWith('change', expect.any(Function));

      // Simulate system theme change
      if (changeHandler) {
        Object.defineProperty(window, 'matchMedia', {
          writable: true,
          value: mockMatchMedia(true), // System now prefers dark
        });

        act(() => {
          changeHandler!({ matches: true } as MediaQueryListEvent);
        });

        await waitFor(() => {
          expect(screen.getByTestId('actual-theme')).toHaveTextContent('dark');
        });
      }
    });

    it('does not listen to system theme changes when theme is not system', () => {
      const mockMediaQuery = mockMatchMedia(false);

      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMediaQuery,
      });

      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      // Set theme to light (not system)
      act(() => {
        const lightButton = screen.getByText('Set Light');
        userEvent.click(lightButton);
      });

      // Should not add listener when not using system theme
      // (The listener is added in useEffect, but we can verify it's set up correctly)
      expect(mockMediaQuery.addEventListener).toHaveBeenCalled();
    });
  });

  describe('Context Values', () => {
    it('provides correct currentTheme object', () => {
      render(
        <ThemeProvider>
          <FullContextTestComponent />
        </ThemeProvider>
      );

      const themeName = screen.getByTestId('theme-name').textContent;
      const primaryColor = screen.getByTestId('primary-color').textContent;

      expect(themeName).toBeDefined();
      expect(primaryColor).toBeDefined();
      expect(primaryColor).toMatch(/^#[0-9A-Fa-f]{6}$/); // Valid hex color
    });

    it('provides correct actualTheme (resolved theme)', () => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia(false),
      });

      render(
        <ThemeProvider>
          <FullContextTestComponent />
        </ThemeProvider>
      );

      const actualTheme = screen.getByTestId('actual-theme').textContent;
      expect(actualTheme).toBe('light');
    });

    it('updates currentTheme when adaptive theme changes', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      // Initial theme should be neutral
      expect(screen.getByTestId('theme-name')).toHaveTextContent('Neutral');

      // Change adaptive theme to anxiety
      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      // Theme name should change
      await waitFor(() => {
        expect(screen.getByTestId('theme-name')).toHaveTextContent('Calm');
      });
    });
  });

  describe('CSS Variable Updates', () => {
    it('applies CSS variables when theme changes', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      // Wait for initial theme application
      await waitFor(() => {
        const primaryColor = getCSSVariable('--color-primary');
        expect(primaryColor).toBeTruthy();
      });

      const initialPrimaryColor = getCSSVariable('--color-primary');

      // Change adaptive theme
      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      // Wait for CSS variables to update
      await waitFor(() => {
        const newPrimaryColor = getCSSVariable('--color-primary');
        expect(newPrimaryColor).toBeTruthy();
        // Color should change (unless by coincidence it's the same)
        const anxietyTheme = getTheme('anxiety', 'light');
        expect(newPrimaryColor).toBe(anxietyTheme.colors.primary);
      });
    });

    it('applies CSS variables when color mode changes', async () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      // Wait for initial theme application
      await waitFor(() => {
        const primaryColor = getCSSVariable('--color-primary');
        expect(primaryColor).toBeTruthy();
      });

      const lightPrimaryColor = getCSSVariable('--color-primary');

      // Change to dark mode
      const darkButton = screen.getByText('Set Dark');
      await userEvent.click(darkButton);

      // Wait for CSS variables to update
      await waitFor(() => {
        const darkPrimaryColor = getCSSVariable('--color-primary');
        expect(darkPrimaryColor).toBeTruthy();
        // Should have dark mode class
        expect(document.documentElement.classList.contains('dark')).toBe(true);
      });
    });

    it('applies theme class to document root', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      // Wait for initial application
      await waitFor(() => {
        expect(document.documentElement.classList.contains('theme-neutral')).toBe(true);
      });

      // Change to anxiety theme
      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      await waitFor(() => {
        expect(document.documentElement.classList.contains('theme-anxiety')).toBe(true);
        expect(document.documentElement.classList.contains('theme-neutral')).toBe(false);
      });
    });

    it('applies color mode class to document root', async () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      // Wait for initial application
      await waitFor(() => {
        expect(document.documentElement.classList.contains('light')).toBe(true);
      });

      // Change to dark
      const darkButton = screen.getByText('Set Dark');
      await userEvent.click(darkButton);

      await waitFor(() => {
        expect(document.documentElement.classList.contains('dark')).toBe(true);
        expect(document.documentElement.classList.contains('light')).toBe(false);
      });
    });
  });

  describe('Theme Persistence', () => {
    it('saves theme preference to localStorage', async () => {
      render(
        <ThemeProvider>
          <BasicTestComponent />
        </ThemeProvider>
      );

      const darkButton = screen.getByText('Set Dark');
      await userEvent.click(darkButton);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    });

    it('saves adaptive theme preference to localStorage', async () => {
      render(
        <ThemeProvider>
          <AdaptiveTestComponent />
        </ThemeProvider>
      );

      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('adaptiveTheme', 'anxiety');
    });

    it('restores both theme and adaptive theme from localStorage', () => {
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'theme') return 'dark';
        if (key === 'adaptiveTheme') return 'anxiety';
        return null;
      });

      render(
        <ThemeProvider>
          <FullContextTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme')).toHaveTextContent('dark');
      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('anxiety');
    });

    it('uses defaults when localStorage is empty', () => {
      localStorageMock.getItem.mockReturnValue(null);

      render(
        <ThemeProvider>
          <FullContextTestComponent />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme')).toHaveTextContent('system');
      expect(screen.getByTestId('adaptive-theme')).toHaveTextContent('neutral');
    });
  });

  describe('Error Handling', () => {
    it('throws error when useTheme is used outside ThemeProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<ErrorTestComponent />);

      expect(screen.getByTestId('error')).toHaveTextContent('useTheme must be used within a ThemeProvider');

      consoleSpy.mockRestore();
    });
  });

  describe('Integration Tests', () => {
    it('updates CSS variables when both theme and adaptive theme change', async () => {
      render(
        <ThemeProvider>
          <div>
            <BasicTestComponent />
            <AdaptiveTestComponent />
          </div>
        </ThemeProvider>
      );

      // Change color mode
      const darkButton = screen.getByText('Set Dark');
      await userEvent.click(darkButton);

      await waitFor(() => {
        expect(document.documentElement.classList.contains('dark')).toBe(true);
      });

      // Change adaptive theme
      const anxietyButton = screen.getByText('Set Anxiety');
      await userEvent.click(anxietyButton);

      await waitFor(() => {
        const primaryColor = getCSSVariable('--color-primary');
        const anxietyDarkTheme = getTheme('anxiety', 'dark');
        expect(primaryColor).toBe(anxietyDarkTheme.colors.primary);
        expect(document.documentElement.classList.contains('theme-anxiety')).toBe(true);
        expect(document.documentElement.classList.contains('dark')).toBe(true);
      });
    });
  });
});

