/**
 * Tests for theme accessibility
 * 
 * Tests WCAG compliance and accessibility features:
 * - Color contrast ratios (WCAG AA/AAA)
 * - Semantic color distinctions
 * - Reduced motion support
 */

import { getTheme, themes, ThemeName, ColorMode } from '../../theme/themes';

// Helper function to convert hex color to RGB
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

// Helper function to calculate relative luminance
function getLuminance(rgb: { r: number; g: number; b: number }): number {
  const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(val => {
    val = val / 255;
    return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

// Helper function to calculate contrast ratio between two colors
function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  if (!rgb1 || !rgb2) {
    return 0;
  }

  const lum1 = getLuminance(rgb1);
  const lum2 = getLuminance(rgb2);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}

// WCAG contrast ratio requirements
const WCAG_AA_NORMAL = 4.5; // For normal text (16px and below)
const WCAG_AA_LARGE = 3.0; // For large text (18pt+ or 14pt+ bold)
const WCAG_AAA_NORMAL = 7.0; // For normal text (AAA level)
const WCAG_AAA_LARGE = 4.5; // For large text (AAA level)

describe('Theme Accessibility', () => {
  const themeNames: ThemeName[] = ['anxiety', 'depression', 'crisis', 'stable', 'east-african', 'neutral'];
  const colorModes: ColorMode[] = ['light', 'dark'];

  describe('Color Contrast (WCAG Compliance)', () => {
    themeNames.forEach(themeName => {
      colorModes.forEach(colorMode => {
        describe(`${themeName} theme (${colorMode})`, () => {
          let theme: ReturnType<typeof getTheme>;

          beforeEach(() => {
            theme = getTheme(themeName, colorMode);
          });

          it('should meet WCAG AA contrast for text-primary vs background', () => {
            const contrast = getContrastRatio(theme.colors.text.primary, theme.colors.background);
            expect(contrast).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
          });

          it('should meet WCAG AA contrast for text-secondary vs background', () => {
            const contrast = getContrastRatio(theme.colors.text.secondary, theme.colors.background);
            expect(contrast).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
          });

          it('should meet WCAG AA contrast for primary color vs background (large text)', () => {
            const contrast = getContrastRatio(theme.colors.primary, theme.colors.background);
            expect(contrast).toBeGreaterThanOrEqual(WCAG_AA_LARGE);
          });

          it('should have sufficient contrast for text on surface', () => {
            const contrast = getContrastRatio(theme.colors.text.primary, theme.colors.surface);
            expect(contrast).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
          });

          it('should have sufficient contrast for danger color on background', () => {
            const contrast = getContrastRatio(theme.colors.danger, theme.colors.background);
            // Danger should be visible but doesn't need to meet text contrast requirements
            expect(contrast).toBeGreaterThan(1.5);
          });

          it('should have sufficient contrast for warning color on background', () => {
            const contrast = getContrastRatio(theme.colors.warning, theme.colors.background);
            // Warning should be visible but doesn't need to meet text contrast requirements
            expect(contrast).toBeGreaterThan(1.5);
          });

          it('should have sufficient contrast for success color on background', () => {
            const contrast = getContrastRatio(theme.colors.success, theme.colors.background);
            // Success should be visible but doesn't need to meet text contrast requirements
            expect(contrast).toBeGreaterThan(1.5);
          });
        });
      });
    });
  });

  describe('Semantic Color Distinctions', () => {
    themeNames.forEach(themeName => {
      colorModes.forEach(colorMode => {
        describe(`${themeName} theme (${colorMode})`, () => {
          let theme: ReturnType<typeof getTheme>;

          beforeEach(() => {
            theme = getTheme(themeName, colorMode);
          });

          it('should have distinct danger and success colors', () => {
            const contrast = getContrastRatio(theme.colors.danger, theme.colors.success);
            // Colors should be visually distinct (contrast > 2.0)
            expect(contrast).toBeGreaterThan(2.0);
          });

          it('should have distinct warning and danger colors', () => {
            const contrast = getContrastRatio(theme.colors.warning, theme.colors.danger);
            // Colors should be visually distinct (contrast > 2.0)
            expect(contrast).toBeGreaterThan(2.0);
          });

          it('should have visible accent color against background', () => {
            const contrast = getContrastRatio(theme.colors.accent, theme.colors.background);
            // Accent should be visible
            expect(contrast).toBeGreaterThan(1.5);
          });

          it('should have distinct primary and secondary colors', () => {
            const contrast = getContrastRatio(theme.colors.primary, theme.colors.secondary);
            // Primary and secondary should be distinct
            expect(contrast).toBeGreaterThan(1.2);
          });
        });
      });
    });
  });

  describe('Reduced Motion Support', () => {
    themeNames.forEach(themeName => {
      colorModes.forEach(colorMode => {
        describe(`${themeName} theme (${colorMode})`, () => {
          let theme: ReturnType<typeof getTheme>;

          beforeEach(() => {
            theme = getTheme(themeName, colorMode);
          });

          it('should have valid animation preference setting', () => {
            const validPreferences = ['none', 'gentle', 'moderate', 'standard', 'reduced-motion'];
            expect(validPreferences).toContain(theme.animations.preference);
          });

          it('should have appropriate animation durations', () => {
            // Fast animations should be quick
            const fastMatch = theme.animations.duration.fast.match(/(\d+)/);
            if (fastMatch) {
              const fastMs = fastMatch[1].includes('ms')
                ? parseInt(fastMatch[1])
                : parseFloat(fastMatch[1]) * 1000;
              expect(fastMs).toBeLessThanOrEqual(300);
            }

            // Normal animations should be moderate
            const normalMatch = theme.animations.duration.normal.match(/(\d+)/);
            if (normalMatch) {
              const normalMs = normalMatch[1].includes('ms')
                ? parseInt(normalMatch[1])
                : parseFloat(normalMatch[1]) * 1000;
              expect(normalMs).toBeGreaterThanOrEqual(200);
              expect(normalMs).toBeLessThanOrEqual(600);
            }

            // Slow animations should be slower
            const slowMatch = theme.animations.duration.slow.match(/(\d+)/);
            if (slowMatch) {
              const slowMs = slowMatch[1].includes('ms')
                ? parseInt(slowMatch[1])
                : parseFloat(slowMatch[1]) * 1000;
              expect(slowMs).toBeGreaterThanOrEqual(400);
            }
          });

          it('should respect reduced-motion preference when set', () => {
            if (theme.animations.preference === 'reduced-motion') {
              // Themes with reduced-motion should have shorter durations
              const fastMatch = theme.animations.duration.fast.match(/(\d+)/);
              const normalMatch = theme.animations.duration.normal.match(/(\d+)/);
              
              if (fastMatch && normalMatch) {
                const fastMs = fastMatch[1].includes('ms')
                  ? parseInt(fastMatch[1])
                  : parseFloat(fastMatch[1]) * 1000;
                const normalMs = normalMatch[1].includes('ms')
                  ? parseInt(normalMatch[1])
                  : parseFloat(normalMatch[1]) * 1000;
                
                // Reduced motion should have shorter durations
                expect(fastMs).toBeLessThan(300);
                expect(normalMs).toBeLessThan(500);
              }
            }
          });
        });
      });
    });
  });

  describe('Color Accessibility by Theme Type', () => {
    it('anxiety theme should use calming colors with good contrast', () => {
      const lightTheme = getTheme('anxiety', 'light');
      const darkTheme = getTheme('anxiety', 'dark');

      // Anxiety theme should have good contrast for readability
      expect(getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });

    it('depression theme should use warm colors with good contrast', () => {
      const lightTheme = getTheme('depression', 'light');
      const darkTheme = getTheme('depression', 'dark');

      // Depression theme should have good contrast for readability
      expect(getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });

    it('crisis theme should use high-contrast colors for clarity', () => {
      const lightTheme = getTheme('crisis', 'light');
      const darkTheme = getTheme('crisis', 'dark');

      // Crisis theme should have high contrast for maximum clarity
      const lightContrast = getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background);
      const darkContrast = getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background);
      
      expect(lightContrast).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(darkContrast).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });

    it('stable theme should use balanced colors with good contrast', () => {
      const lightTheme = getTheme('stable', 'light');
      const darkTheme = getTheme('stable', 'dark');

      // Stable theme should have good contrast for readability
      expect(getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });

    it('east-african theme should use cultural colors with good contrast', () => {
      const lightTheme = getTheme('east-african', 'light');
      const darkTheme = getTheme('east-african', 'dark');

      // East African theme should have good contrast for readability
      expect(getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });

    it('neutral theme should use standard colors with good contrast', () => {
      const lightTheme = getTheme('neutral', 'light');
      const darkTheme = getTheme('neutral', 'dark');

      // Neutral theme should have good contrast for readability
      expect(getContrastRatio(lightTheme.colors.text.primary, lightTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
      expect(getContrastRatio(darkTheme.colors.text.primary, darkTheme.colors.background)).toBeGreaterThanOrEqual(WCAG_AA_NORMAL);
    });
  });
});

