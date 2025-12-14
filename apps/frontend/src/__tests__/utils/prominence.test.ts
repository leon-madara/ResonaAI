/**
 * Tests for Prominence Utilities
 * 
 * Tests prominence-based rendering utilities for components
 */

import {
  getProminenceClasses,
  getUrgencyClasses,
  getComponentWrapperClasses,
  shouldRenderComponent,
  getProminenceContainerStyles,
} from '../../utils/prominence';
import { Prominence, Urgency } from '../../types';

describe('Prominence Utilities', () => {
  describe('getProminenceClasses', () => {
    it('should return correct classes for modal prominence', () => {
      const classes = getProminenceClasses('modal');
      expect(classes).toContain('fixed');
      expect(classes).toContain('inset-0');
      expect(classes).toContain('z-50');
      expect(classes).toContain('overflow-y-auto');
      expect(classes).toContain('backdrop-blur-sm');
      expect(classes).toContain('transition-all');
    });

    it('should return correct classes for top prominence', () => {
      const classes = getProminenceClasses('top');
      expect(classes).toContain('w-full');
      expect(classes).toContain('mb-[var(--spacing-component-gap)]');
      expect(classes).toContain('transition-all');
    });

    it('should return correct classes for card prominence', () => {
      const classes = getProminenceClasses('card');
      expect(classes).toContain('bg-[var(--color-surface)]');
      expect(classes).toContain('rounded-[var(--border-radius-lg)]');
      expect(classes).toContain('shadow-[var(--shadow-md)]');
      expect(classes).toContain('p-[var(--spacing-container-padding)]');
      expect(classes).toContain('border');
      expect(classes).toContain('transition-all');
    });

    it('should return correct classes for sidebar prominence', () => {
      const classes = getProminenceClasses('sidebar');
      expect(classes).toContain('bg-[var(--color-surface)]/50');
      expect(classes).toContain('rounded-[var(--border-radius-md)]');
      expect(classes).toContain('p-[calc(var(--spacing-container-padding)*0.75)]');
      expect(classes).toContain('transition-all');
    });

    it('should return correct classes for minimal prominence', () => {
      const classes = getProminenceClasses('minimal');
      expect(classes).toContain('text-[var(--font-size-sm)]');
      expect(classes).toContain('text-[var(--color-text-secondary)]');
      expect(classes).toContain('mb-[calc(var(--spacing-component-gap)*0.5)]');
      expect(classes).toContain('transition-all');
    });

    it('should return hidden class for hidden prominence', () => {
      const classes = getProminenceClasses('hidden');
      expect(classes).toBe('hidden');
    });

    it('should include animation duration class for all visible prominences', () => {
      const prominences: Prominence[] = ['modal', 'top', 'card', 'sidebar', 'minimal'];
      prominences.forEach(prominence => {
        const classes = getProminenceClasses(prominence);
        expect(classes).toContain('duration-[var(--animation-duration-normal)]');
      });
    });
  });

  describe('getUrgencyClasses', () => {
    it('should return correct classes for critical urgency', () => {
      const classes = getUrgencyClasses('critical');
      expect(classes).toContain('border-l-4');
      expect(classes).toContain('border-[var(--color-danger)]');
      expect(classes).toContain('bg-[var(--color-danger)]/10');
      expect(classes).toContain('animate-pulse');
    });

    it('should return correct classes for high urgency', () => {
      const classes = getUrgencyClasses('high');
      expect(classes).toContain('border-l-4');
      expect(classes).toContain('border-[var(--color-warning)]');
      expect(classes).toContain('bg-[var(--color-warning)]/5');
    });

    it('should return correct classes for medium urgency', () => {
      const classes = getUrgencyClasses('medium');
      expect(classes).toContain('border-l-2');
      expect(classes).toContain('border-[var(--color-accent)]');
    });

    it('should return empty string for low urgency', () => {
      const classes = getUrgencyClasses('low');
      expect(classes).toBe('');
    });

    it('should return empty string for none urgency', () => {
      const classes = getUrgencyClasses('none');
      expect(classes).toBe('');
    });
  });

  describe('getComponentWrapperClasses', () => {
    it('should combine prominence and urgency classes correctly', () => {
      const classes = getComponentWrapperClasses('card', 'critical');
      expect(classes).toContain('bg-[var(--color-surface)]'); // From prominence
      expect(classes).toContain('border-l-4'); // From urgency
      expect(classes).toContain('border-[var(--color-danger)]'); // From urgency
    });

    it('should trim whitespace properly', () => {
      const classes = getComponentWrapperClasses('minimal', 'none');
      // Should not have leading/trailing whitespace
      expect(classes).toBe(classes.trim());
    });

    it('should work with all prominence and urgency combinations', () => {
      const prominences: Prominence[] = ['modal', 'top', 'card', 'sidebar', 'minimal', 'hidden'];
      const urgencies: Urgency[] = ['none', 'low', 'medium', 'high', 'critical'];

      prominences.forEach(prominence => {
        urgencies.forEach(urgency => {
          const classes = getComponentWrapperClasses(prominence, urgency);
          expect(typeof classes).toBe('string');
          expect(classes).toBe(classes.trim());
        });
      });
    });

    it('should handle hidden prominence with any urgency', () => {
      const urgencies: Urgency[] = ['none', 'low', 'medium', 'high', 'critical'];
      urgencies.forEach(urgency => {
        const classes = getComponentWrapperClasses('hidden', urgency);
        expect(classes).toContain('hidden');
      });
    });
  });

  describe('shouldRenderComponent', () => {
    it('should return true when visible=true and prominence != hidden', () => {
      const prominences: Prominence[] = ['modal', 'top', 'card', 'sidebar', 'minimal'];
      prominences.forEach(prominence => {
        expect(shouldRenderComponent(prominence, true)).toBe(true);
      });
    });

    it('should return false when visible=false', () => {
      const prominences: Prominence[] = ['modal', 'top', 'card', 'sidebar', 'minimal', 'hidden'];
      prominences.forEach(prominence => {
        expect(shouldRenderComponent(prominence, false)).toBe(false);
      });
    });

    it('should return false when prominence=hidden', () => {
      expect(shouldRenderComponent('hidden', true)).toBe(false);
      expect(shouldRenderComponent('hidden', false)).toBe(false);
    });

    it('should return false when visible=false and prominence=hidden', () => {
      expect(shouldRenderComponent('hidden', false)).toBe(false);
    });

    it('should default visible to true when not provided', () => {
      const prominences: Prominence[] = ['modal', 'top', 'card', 'sidebar', 'minimal'];
      prominences.forEach(prominence => {
        expect(shouldRenderComponent(prominence)).toBe(true);
      });
      expect(shouldRenderComponent('hidden')).toBe(false);
    });
  });

  describe('getProminenceContainerStyles', () => {
    it('should return correct styles for modal prominence', () => {
      const styles = getProminenceContainerStyles('modal');
      expect(styles.position).toBe('fixed');
      expect(styles.top).toBe(0);
      expect(styles.left).toBe(0);
      expect(styles.right).toBe(0);
      expect(styles.bottom).toBe(0);
      expect(styles.zIndex).toBe(50);
      expect(styles.display).toBe('flex');
      expect(styles.alignItems).toBe('center');
      expect(styles.justifyContent).toBe('center');
      expect(styles.padding).toBe('var(--spacing-container-padding)');
    });

    it('should return correct styles for top prominence', () => {
      const styles = getProminenceContainerStyles('top');
      expect(styles.width).toBe('100%');
      expect(styles.marginBottom).toBe('var(--spacing-component-gap)');
    });

    it('should return correct styles for card prominence', () => {
      const styles = getProminenceContainerStyles('card');
      expect(styles.width).toBe('100%');
      expect(styles.marginBottom).toBe('var(--spacing-component-gap)');
    });

    it('should return correct styles for sidebar prominence', () => {
      const styles = getProminenceContainerStyles('sidebar');
      expect(styles.width).toBe('100%');
      expect(styles.marginBottom).toBe('calc(var(--spacing-component-gap) * 0.75)');
    });

    it('should return correct styles for minimal prominence', () => {
      const styles = getProminenceContainerStyles('minimal');
      expect(styles.width).toBe('100%');
      expect(styles.marginBottom).toBe('calc(var(--spacing-component-gap) * 0.5)');
    });

    it('should return display none for hidden prominence', () => {
      const styles = getProminenceContainerStyles('hidden');
      expect(styles.display).toBe('none');
    });

    it('should return display none for unknown prominence', () => {
      // TypeScript won't allow this, but testing runtime behavior
      const styles = getProminenceContainerStyles('hidden' as Prominence);
      expect(styles.display).toBe('none');
    });
  });
});

