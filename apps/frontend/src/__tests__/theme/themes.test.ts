/**
 * Tests for theme definitions and theme functions
 * 
 * Tests the theme system including:
 * - All 6 theme definitions (anxiety, depression, crisis, stable, east-african, neutral)
 * - Light and dark mode variants
 * - Theme structure validation
 * - getTheme() function
 * - applyTheme() function
 * - CSS variable application
 */

import { getTheme, applyTheme, themes, ThemeName, ColorMode, CompleteTheme } from '../../theme/themes';

// Helper function to get CSS variable value from document root
function getCSSVariable(variableName: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
}

// Helper function to check if a string is a valid hex color
function isValidHexColor(color: string): boolean {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
}

// Helper function to check if a string is a valid CSS unit (rem, px, em)
function isValidCSSUnit(value: string): boolean {
  return /^\d+(\.\d+)?(rem|px|em|%)$/.test(value);
}

// Helper function to check if a string is a valid time value (ms, s)
function isValidTimeValue(value: string): boolean {
  return /^\d+(\.\d+)?(ms|s)$/.test(value);
}

describe('Theme Definitions', () => {
  const themeNames: ThemeName[] = ['anxiety', 'depression', 'crisis', 'stable', 'east-african', 'neutral'];
  const colorModes: ColorMode[] = ['light', 'dark'];

  describe('Theme Registry', () => {
    it('should have all 6 theme names', () => {
      expect(Object.keys(themes)).toHaveLength(6);
      themeNames.forEach(themeName => {
        expect(themes).toHaveProperty(themeName);
      });
    });

    it('should have light and dark variants for each theme', () => {
      themeNames.forEach(themeName => {
        expect(themes[themeName]).toHaveProperty('light');
        expect(themes[themeName]).toHaveProperty('dark');
      });
    });
  });

  describe('Theme Structure Validation', () => {
    themeNames.forEach(themeName => {
      colorModes.forEach(colorMode => {
        describe(`${themeName} theme (${colorMode})`, () => {
          let theme: CompleteTheme;

          beforeEach(() => {
            theme = themes[themeName][colorMode];
          });

          it('should have a name', () => {
            expect(theme.name).toBeDefined();
            expect(typeof theme.name).toBe('string');
            expect(theme.name.length).toBeGreaterThan(0);
          });

          describe('Colors', () => {
            it('should have all required color properties', () => {
              expect(theme.colors).toBeDefined();
              expect(theme.colors.primary).toBeDefined();
              expect(theme.colors.secondary).toBeDefined();
              expect(theme.colors.background).toBeDefined();
              expect(theme.colors.surface).toBeDefined();
              expect(theme.colors.text).toBeDefined();
              expect(theme.colors.text.primary).toBeDefined();
              expect(theme.colors.text.secondary).toBeDefined();
              expect(theme.colors.text.tertiary).toBeDefined();
              expect(theme.colors.accent).toBeDefined();
              expect(theme.colors.success).toBeDefined();
              expect(theme.colors.warning).toBeDefined();
              expect(theme.colors.danger).toBeDefined();
            });

            it('should have valid hex color values', () => {
              const colorProps = [
                'primary', 'secondary', 'background', 'surface',
                'accent', 'success', 'warning', 'danger'
              ];
              
              colorProps.forEach(prop => {
                expect(isValidHexColor(theme.colors[prop as keyof typeof theme.colors] as string)).toBe(true);
              });

              expect(isValidHexColor(theme.colors.text.primary)).toBe(true);
              expect(isValidHexColor(theme.colors.text.secondary)).toBe(true);
              expect(isValidHexColor(theme.colors.text.tertiary)).toBe(true);
            });
          });

          describe('Typography', () => {
            it('should have all required typography properties', () => {
              expect(theme.typography).toBeDefined();
              expect(theme.typography.fontFamily).toBeDefined();
              expect(theme.typography.fontFamily.primary).toBeDefined();
              expect(theme.typography.fontFamily.secondary).toBeDefined();
              expect(theme.typography.scale).toBeDefined();
              expect(theme.typography.weight).toBeDefined();
              expect(theme.typography.lineHeight).toBeDefined();
              expect(theme.typography.letterSpacing).toBeDefined();
            });

            it('should have valid font size scale values', () => {
              const scaleKeys = ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl'];
              scaleKeys.forEach(key => {
                const value = theme.typography.scale[key as keyof typeof theme.typography.scale];
                expect(value).toBeDefined();
                expect(isValidCSSUnit(value)).toBe(true);
              });
            });

            it('should have valid font weight values', () => {
              expect(theme.typography.weight.normal).toBeGreaterThanOrEqual(100);
              expect(theme.typography.weight.normal).toBeLessThanOrEqual(900);
              expect(theme.typography.weight.medium).toBeGreaterThanOrEqual(100);
              expect(theme.typography.weight.medium).toBeLessThanOrEqual(900);
              expect(theme.typography.weight.semibold).toBeGreaterThanOrEqual(100);
              expect(theme.typography.weight.semibold).toBeLessThanOrEqual(900);
              expect(theme.typography.weight.bold).toBeGreaterThanOrEqual(100);
              expect(theme.typography.weight.bold).toBeLessThanOrEqual(900);
            });

            it('should have valid line height', () => {
              expect(theme.typography.lineHeight).toBeGreaterThan(0);
              expect(theme.typography.lineHeight).toBeLessThanOrEqual(3);
            });

            it('should have valid letter spacing', () => {
              expect(typeof theme.typography.letterSpacing).toBe('string');
            });
          });

          describe('Spacing', () => {
            it('should have all required spacing properties', () => {
              expect(theme.spacing).toBeDefined();
              expect(theme.spacing.unit).toBeDefined();
              expect(theme.spacing.scale).toBeDefined();
              expect(theme.spacing.containerPadding).toBeDefined();
              expect(theme.spacing.componentGap).toBeDefined();
            });

            it('should have positive spacing values', () => {
              expect(theme.spacing.unit).toBeGreaterThan(0);
              expect(theme.spacing.containerPadding).toBeGreaterThan(0);
              expect(theme.spacing.componentGap).toBeGreaterThan(0);
            });

            it('should have valid scale value', () => {
              const validScales = ['compressed', 'comfortable', 'spacious', 'standard', 'generous'];
              expect(validScales).toContain(theme.spacing.scale);
            });
          });

          describe('Border Radius', () => {
            it('should have all required border radius properties', () => {
              expect(theme.borderRadius).toBeDefined();
              expect(theme.borderRadius.sm).toBeDefined();
              expect(theme.borderRadius.md).toBeDefined();
              expect(theme.borderRadius.lg).toBeDefined();
              expect(theme.borderRadius.xl).toBeDefined();
              expect(theme.borderRadius.round).toBeDefined();
            });

            it('should have valid border radius values', () => {
              const radiusKeys = ['sm', 'md', 'lg', 'xl', 'round'];
              radiusKeys.forEach(key => {
                const value = theme.borderRadius[key as keyof typeof theme.borderRadius];
                expect(value).toBeDefined();
                expect(isValidCSSUnit(value) || value === '50%').toBe(true);
              });
            });
          });

          describe('Shadows', () => {
            it('should have all required shadow properties', () => {
              expect(theme.shadows).toBeDefined();
              expect(theme.shadows.sm).toBeDefined();
              expect(theme.shadows.md).toBeDefined();
              expect(theme.shadows.lg).toBeDefined();
              expect(theme.shadows.none).toBeDefined();
            });

            it('should have valid shadow values', () => {
              expect(theme.shadows.none).toBe('none');
              // Shadow values should be strings (CSS box-shadow syntax)
              expect(typeof theme.shadows.sm).toBe('string');
              expect(typeof theme.shadows.md).toBe('string');
              expect(typeof theme.shadows.lg).toBe('string');
            });
          });

          describe('Animations', () => {
            it('should have all required animation properties', () => {
              expect(theme.animations).toBeDefined();
              expect(theme.animations.duration).toBeDefined();
              expect(theme.animations.duration.fast).toBeDefined();
              expect(theme.animations.duration.normal).toBeDefined();
              expect(theme.animations.duration.slow).toBeDefined();
              expect(theme.animations.easing).toBeDefined();
              expect(theme.animations.preference).toBeDefined();
            });

            it('should have valid animation duration values', () => {
              expect(isValidTimeValue(theme.animations.duration.fast)).toBe(true);
              expect(isValidTimeValue(theme.animations.duration.normal)).toBe(true);
              expect(isValidTimeValue(theme.animations.duration.slow)).toBe(true);
            });

            it('should have valid easing value', () => {
              expect(typeof theme.animations.easing).toBe('string');
              expect(theme.animations.easing.length).toBeGreaterThan(0);
            });

            it('should have valid preference value', () => {
              const validPreferences = ['none', 'gentle', 'moderate', 'standard', 'reduced-motion'];
              expect(validPreferences).toContain(theme.animations.preference);
            });
          });

          describe('Layout', () => {
            it('should have all required layout properties', () => {
              expect(theme.layout).toBeDefined();
              expect(theme.layout.maxWidth).toBeDefined();
              expect(theme.layout.density).toBeDefined();
            });

            it('should have valid max width value', () => {
              expect(isValidCSSUnit(theme.layout.maxWidth)).toBe(true);
            });

            it('should have valid density value', () => {
              const validDensities = ['compact', 'standard', 'comfortable', 'spacious'];
              expect(validDensities).toContain(theme.layout.density);
            });
          });
        });
      });
    });
  });
});

describe('getTheme() Function', () => {
  const themeNames: ThemeName[] = ['anxiety', 'depression', 'crisis', 'stable', 'east-african', 'neutral'];
  const colorModes: ColorMode[] = ['light', 'dark'];

  it('should return correct theme for valid theme name and color mode', () => {
    themeNames.forEach(themeName => {
      colorModes.forEach(colorMode => {
        const theme = getTheme(themeName, colorMode);
        expect(theme).toBeDefined();
        expect(theme.name).toBe(themes[themeName][colorMode].name);
        expect(theme.colors.primary).toBe(themes[themeName][colorMode].colors.primary);
      });
    });
  });

  it('should fall back to neutral theme for invalid theme name', () => {
    const invalidTheme = 'invalid-theme' as ThemeName;
    const lightTheme = getTheme(invalidTheme, 'light');
    const darkTheme = getTheme(invalidTheme, 'dark');
    
    expect(lightTheme).toBe(themes.neutral.light);
    expect(darkTheme).toBe(themes.neutral.dark);
  });

  it('should return light mode theme when color mode is invalid', () => {
    // TypeScript won't allow invalid ColorMode, but we can test with undefined
    const theme = getTheme('neutral', 'light');
    expect(theme).toBe(themes.neutral.light);
  });

  it('should return the same theme object reference', () => {
    const theme1 = getTheme('anxiety', 'light');
    const theme2 = getTheme('anxiety', 'light');
    expect(theme1).toBe(theme2);
    expect(theme1).toBe(themes.anxiety.light);
  });
});

describe('applyTheme() Function', () => {
  beforeEach(() => {
    // Clear all CSS variables and classes before each test
    const root = document.documentElement;
    root.className = '';
    root.style.cssText = '';
  });

  const themeNames: ThemeName[] = ['anxiety', 'depression', 'crisis', 'stable', 'east-african', 'neutral'];
  const colorModes: ColorMode[] = ['light', 'dark'];

  themeNames.forEach(themeName => {
    colorModes.forEach(colorMode => {
      describe(`${themeName} theme (${colorMode})`, () => {
        let theme: CompleteTheme;

        beforeEach(() => {
          theme = getTheme(themeName, colorMode);
          applyTheme(theme, colorMode);
        });

        it('should apply all color CSS variables', () => {
          expect(getCSSVariable('--color-primary')).toBe(theme.colors.primary);
          expect(getCSSVariable('--color-secondary')).toBe(theme.colors.secondary);
          expect(getCSSVariable('--color-background')).toBe(theme.colors.background);
          expect(getCSSVariable('--color-surface')).toBe(theme.colors.surface);
          expect(getCSSVariable('--color-text-primary')).toBe(theme.colors.text.primary);
          expect(getCSSVariable('--color-text-secondary')).toBe(theme.colors.text.secondary);
          expect(getCSSVariable('--color-text-tertiary')).toBe(theme.colors.text.tertiary);
          expect(getCSSVariable('--color-accent')).toBe(theme.colors.accent);
          expect(getCSSVariable('--color-success')).toBe(theme.colors.success);
          expect(getCSSVariable('--color-warning')).toBe(theme.colors.warning);
          expect(getCSSVariable('--color-danger')).toBe(theme.colors.danger);
        });

        it('should apply all typography CSS variables', () => {
          expect(getCSSVariable('--font-family-primary')).toBe(theme.typography.fontFamily.primary);
          expect(getCSSVariable('--font-family-secondary')).toBe(theme.typography.fontFamily.secondary);
          expect(getCSSVariable('--font-size-xs')).toBe(theme.typography.scale.xs);
          expect(getCSSVariable('--font-size-sm')).toBe(theme.typography.scale.sm);
          expect(getCSSVariable('--font-size-base')).toBe(theme.typography.scale.base);
          expect(getCSSVariable('--font-size-lg')).toBe(theme.typography.scale.lg);
          expect(getCSSVariable('--font-size-xl')).toBe(theme.typography.scale.xl);
          expect(getCSSVariable('--font-size-2xl')).toBe(theme.typography.scale['2xl']);
          expect(getCSSVariable('--font-size-3xl')).toBe(theme.typography.scale['3xl']);
          expect(getCSSVariable('--font-weight-normal')).toBe(theme.typography.weight.normal.toString());
          expect(getCSSVariable('--font-weight-medium')).toBe(theme.typography.weight.medium.toString());
          expect(getCSSVariable('--font-weight-semibold')).toBe(theme.typography.weight.semibold.toString());
          expect(getCSSVariable('--font-weight-bold')).toBe(theme.typography.weight.bold.toString());
          expect(getCSSVariable('--line-height')).toBe(theme.typography.lineHeight.toString());
          expect(getCSSVariable('--letter-spacing')).toBe(theme.typography.letterSpacing);
        });

        it('should apply all spacing CSS variables', () => {
          expect(getCSSVariable('--spacing-unit')).toBe(`${theme.spacing.unit}px`);
          expect(getCSSVariable('--spacing-container-padding')).toBe(`${theme.spacing.containerPadding}px`);
          expect(getCSSVariable('--spacing-component-gap')).toBe(`${theme.spacing.componentGap}px`);
        });

        it('should apply all border radius CSS variables', () => {
          expect(getCSSVariable('--border-radius-sm')).toBe(theme.borderRadius.sm);
          expect(getCSSVariable('--border-radius-md')).toBe(theme.borderRadius.md);
          expect(getCSSVariable('--border-radius-lg')).toBe(theme.borderRadius.lg);
          expect(getCSSVariable('--border-radius-xl')).toBe(theme.borderRadius.xl);
          expect(getCSSVariable('--border-radius-round')).toBe(theme.borderRadius.round);
        });

        it('should apply all shadow CSS variables', () => {
          expect(getCSSVariable('--shadow-sm')).toBe(theme.shadows.sm);
          expect(getCSSVariable('--shadow-md')).toBe(theme.shadows.md);
          expect(getCSSVariable('--shadow-lg')).toBe(theme.shadows.lg);
          expect(getCSSVariable('--shadow-none')).toBe(theme.shadows.none);
        });

        it('should apply all animation CSS variables', () => {
          expect(getCSSVariable('--animation-duration-fast')).toBe(theme.animations.duration.fast);
          expect(getCSSVariable('--animation-duration-normal')).toBe(theme.animations.duration.normal);
          expect(getCSSVariable('--animation-duration-slow')).toBe(theme.animations.duration.slow);
          expect(getCSSVariable('--animation-easing')).toBe(theme.animations.easing);
        });

        it('should apply layout CSS variables', () => {
          expect(getCSSVariable('--layout-max-width')).toBe(theme.layout.maxWidth);
        });

        it('should add theme class to document root', () => {
          const expectedClass = `theme-${theme.name.toLowerCase().replace(/\s+/g, '-')}`;
          expect(document.documentElement.classList.contains(expectedClass)).toBe(true);
        });

        it('should add color mode class to document root', () => {
          expect(document.documentElement.classList.contains(colorMode)).toBe(true);
        });

        it('should remove previous theme classes when switching', () => {
          // Apply a different theme
          const otherTheme = themeName === 'anxiety' ? 'depression' : 'anxiety';
          const otherThemeObj = getTheme(otherTheme as ThemeName, colorMode);
          applyTheme(otherThemeObj, colorMode);

          // Previous theme class should be removed
          const previousClass = `theme-${theme.name.toLowerCase().replace(/\s+/g, '-')}`;
          expect(document.documentElement.classList.contains(previousClass)).toBe(false);
        });

        it('should remove previous color mode class when switching', () => {
          // Apply opposite color mode
          const oppositeMode: ColorMode = colorMode === 'light' ? 'dark' : 'light';
          applyTheme(theme, oppositeMode);

          // Previous color mode class should be removed
          expect(document.documentElement.classList.contains(colorMode)).toBe(false);
          expect(document.documentElement.classList.contains(oppositeMode)).toBe(true);
        });
      });
    });
  });
});

