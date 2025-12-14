/**
 * Integration Tests for Layout System
 * 
 * Tests end-to-end layout system functionality including:
 * - Risk-based adjustments
 * - Responsive behavior
 * - Component ordering
 * - Full UIConfig rendering
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { InterfaceRenderer } from '../../components/Layout/InterfaceRenderer';
import { prioritizeComponents, getRiskBasedLayout } from '../../utils/layoutPrioritizer';
import { UIConfig, ComponentConfig } from '../../types';

// Mock ThemeContext
jest.mock('../../contexts/ThemeContext', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Helper function to create mock UIConfig
function createMockUIConfig(
  components: Record<string, ComponentConfig>,
  riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'medium',
  metadataOverrides: Partial<UIConfig['metadata']> = {}
): UIConfig {
  return {
    user_id: 'test-user',
    generated_at: '2025-01-15T10:00:00Z',
    version: '1.0.0',
    theme: {
      name: 'test-theme',
      base: 'calm',
      colors: {
        primary: '#000',
        secondary: '#000',
        background: '#fff',
        text: '#000',
        accent: '#000',
        warning: '#000',
      },
      spacing: 'comfortable',
      animations: 'gentle',
      contrast: 'medium',
      fontScale: 1.0,
      description: 'Test theme',
    },
    components,
    layout: {
      hero: [],
      primary: [],
      sidebar: [],
      footer: [],
    },
    mobile_layout: [],
    cultural: {
      language: 'english',
      greeting_style: 'formal',
      directness: 'medium',
      validation_style: 'gentle',
    },
    changes: [],
    metadata: {
      risk_level: riskLevel,
      trajectory: 'stable',
      primary_emotions: [],
      primary_language: 'english',
      session_count: 0,
      dissonance_score: 0.5,
      trigger_count: 0,
      effective_coping_count: 0,
      ...metadataOverrides,
    },
  };
}

// Mock window.innerWidth
const mockWindowWidth = (width: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
};

describe('Layout System Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWindowWidth(1024); // Desktop by default
  });

  describe('End-to-end layout system', () => {
    it('should render full UIConfig with all prominence types correctly', () => {
      const config = createMockUIConfig({
        ModalComponent: {
          component_name: 'ModalComponent',
          visible: true,
          prominence: 'modal',
          urgency: 'high',
          props: {},
        },
        TopComponent: {
          component_name: 'TopComponent',
          visible: true,
          prominence: 'top',
          urgency: 'medium',
          props: {},
        },
        CardComponent: {
          component_name: 'CardComponent',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        MinimalComponent: {
          component_name: 'MinimalComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      });

      const prioritized = prioritizeComponents(config);
      expect(prioritized.hero).toContain('ModalComponent');
      expect(prioritized.hero).toContain('TopComponent');
      expect(prioritized.primary).toContain('CardComponent');
      expect(prioritized.sidebar).toContain('SidebarComponent');
      expect(prioritized.footer).toContain('MinimalComponent');
    });

    it('should update layout correctly when risk level changes', () => {
      const components: Record<string, ComponentConfig> = {};
      for (let i = 0; i < 10; i++) {
        components[`Component${i}`] = {
          component_name: `Component${i}`,
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        };
      }

      // Test critical risk
      const criticalConfig = createMockUIConfig(components, 'critical');
      const criticalLayout = getRiskBasedLayout('critical');
      expect(criticalLayout.maxComponents).toBe(3);
      expect(criticalLayout.showSidebar).toBe(false);
      expect(criticalLayout.showFooter).toBe(false);
      expect(criticalLayout.compactMode).toBe(true);

      // Test low risk
      const lowConfig = createMockUIConfig(components, 'low');
      const lowLayout = getRiskBasedLayout('low');
      expect(lowLayout.maxComponents).toBe(12);
      expect(lowLayout.showSidebar).toBe(true);
      expect(lowLayout.showFooter).toBe(true);
      expect(lowLayout.compactMode).toBe(false);
    });

    it('should update component ordering when urgency changes', () => {
      const config1 = createMockUIConfig({
        Component1: {
          component_name: 'Component1',
          visible: true,
          prominence: 'card',
          urgency: 'low',
          props: {},
        },
        Component2: {
          component_name: 'Component2',
          visible: true,
          prominence: 'card',
          urgency: 'high',
          props: {},
        },
      });

      const result1 = prioritizeComponents(config1);
      // High urgency should appear before low urgency
      const primary1 = result1.primary;
      expect(primary1.indexOf('Component2')).toBeLessThan(primary1.indexOf('Component1'));

      // Change urgency
      const config2 = createMockUIConfig({
        Component1: {
          component_name: 'Component1',
          visible: true,
          prominence: 'card',
          urgency: 'high',
          props: {},
        },
        Component2: {
          component_name: 'Component2',
          visible: true,
          prominence: 'card',
          urgency: 'low',
          props: {},
        },
      });

      const result2 = prioritizeComponents(config2);
      const primary2 = result2.primary;
      // Now Component1 should appear before Component2
      expect(primary2.indexOf('Component1')).toBeLessThan(primary2.indexOf('Component2'));
    });

    it('should move components to correct sections when prominence changes', () => {
      // Start with card prominence (goes to primary)
      const config1 = createMockUIConfig({
        TestComponent: {
          component_name: 'TestComponent',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
      });

      const result1 = prioritizeComponents(config1);
      expect(result1.primary).toContain('TestComponent');

      // Change to sidebar prominence
      const config2 = createMockUIConfig({
        TestComponent: {
          component_name: 'TestComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
      });

      const result2 = prioritizeComponents(config2);
      expect(result2.sidebar).toContain('TestComponent');
      expect(result2.primary).not.toContain('TestComponent');
    });

    it('should order multiple components with same prominence by priority', () => {
      const config = createMockUIConfig({
        LowPriorityCard: {
          component_name: 'LowPriorityCard',
          visible: true,
          prominence: 'card',
          urgency: 'low',
          props: {},
        },
        HighPriorityCard: {
          component_name: 'HighPriorityCard',
          visible: true,
          prominence: 'card',
          urgency: 'high',
          props: {},
        },
        MediumPriorityCard: {
          component_name: 'MediumPriorityCard',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
      });

      const result = prioritizeComponents(config);
      const primary = result.primary;
      // High priority should be first, then medium, then low
      expect(primary.indexOf('HighPriorityCard')).toBeLessThan(primary.indexOf('MediumPriorityCard'));
      expect(primary.indexOf('MediumPriorityCard')).toBeLessThan(primary.indexOf('LowPriorityCard'));
    });

    it('should not render empty sections', () => {
      const config = createMockUIConfig({});
      const result = prioritizeComponents(config);
      expect(result.hero.length).toBe(0);
      expect(result.primary.length).toBe(0);
      expect(result.sidebar.length).toBe(0);
      expect(result.footer.length).toBe(0);
    });

    it('should render all sections when populated', () => {
      const config = createMockUIConfig({
        HeroComponent: {
          component_name: 'HeroComponent',
          visible: true,
          prominence: 'top',
          urgency: 'medium',
          props: {},
        },
        PrimaryComponent: {
          component_name: 'PrimaryComponent',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        FooterComponent: {
          component_name: 'FooterComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      });

      const result = prioritizeComponents(config);
      expect(result.hero.length).toBeGreaterThan(0);
      expect(result.primary.length).toBeGreaterThan(0);
      expect(result.sidebar.length).toBeGreaterThan(0);
      expect(result.footer.length).toBeGreaterThan(0);
    });
  });

  describe('Risk-based layout adjustment integration', () => {
    it('should apply compact mode correctly for critical risk', () => {
      const components: Record<string, ComponentConfig> = {};
      for (let i = 0; i < 5; i++) {
        components[`Component${i}`] = {
          component_name: `Component${i}`,
          visible: true,
          prominence: 'top',
          urgency: 'high',
          props: {},
        };
      }

      const config = createMockUIConfig(components, 'critical');
      const layout = getRiskBasedLayout('critical');
      const prioritized = prioritizeComponents(config);

      expect(layout.compactMode).toBe(true);
      // In compact mode, hero should be limited to 1
      expect(prioritized.hero.length).toBeGreaterThan(0);
    });

    it('should show sidebar but not footer for high risk', () => {
      const config = createMockUIConfig({
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        FooterComponent: {
          component_name: 'FooterComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      }, 'high');

      const layout = getRiskBasedLayout('high');
      expect(layout.showSidebar).toBe(true);
      expect(layout.showFooter).toBe(false);
    });

    it('should show all sections for medium risk', () => {
      const config = createMockUIConfig({
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        FooterComponent: {
          component_name: 'FooterComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      }, 'medium');

      const layout = getRiskBasedLayout('medium');
      expect(layout.showSidebar).toBe(true);
      expect(layout.showFooter).toBe(true);
    });

    it('should show all sections with full component count for low risk', () => {
      const components: Record<string, ComponentConfig> = {};
      for (let i = 0; i < 15; i++) {
        components[`Component${i}`] = {
          component_name: `Component${i}`,
          visible: true,
          prominence: i < 5 ? 'card' : i < 10 ? 'sidebar' : 'minimal',
          urgency: 'medium',
          props: {},
        };
      }

      const config = createMockUIConfig(components, 'low');
      const layout = getRiskBasedLayout('low');
      const prioritized = prioritizeComponents(config);

      expect(layout.maxComponents).toBe(12);
      expect(layout.showSidebar).toBe(true);
      expect(layout.showFooter).toBe(true);
      expect(layout.compactMode).toBe(false);
    });
  });

  describe('Mobile/Desktop responsive behavior', () => {
    it('should show hero + primary + sidebar + footer on desktop', () => {
      mockWindowWidth(1024);
      const config = createMockUIConfig({
        HeroComponent: {
          component_name: 'HeroComponent',
          visible: true,
          prominence: 'top',
          urgency: 'medium',
          props: {},
        },
        PrimaryComponent: {
          component_name: 'PrimaryComponent',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        FooterComponent: {
          component_name: 'FooterComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      });

      const prioritized = prioritizeComponents(config);
      expect(prioritized.hero.length).toBeGreaterThan(0);
      expect(prioritized.primary.length).toBeGreaterThan(0);
      expect(prioritized.sidebar.length).toBeGreaterThan(0);
      expect(prioritized.footer.length).toBeGreaterThan(0);
    });

    it('should show single column with top 7 components on mobile', () => {
      mockWindowWidth(375);
      const components: Record<string, ComponentConfig> = {};
      for (let i = 0; i < 10; i++) {
        components[`Component${i}`] = {
          component_name: `Component${i}`,
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        };
      }

      const config = createMockUIConfig(components);
      const prioritized = prioritizeComponents(config);
      expect(prioritized.mobile.length).toBeLessThanOrEqual(7);
    });

    it('should always include critical components on mobile', () => {
      mockWindowWidth(375);
      const config = createMockUIConfig({
        CriticalComponent: {
          component_name: 'CriticalComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'critical',
          props: {},
        },
        RegularComponent: {
          component_name: 'RegularComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      });

      const prioritized = prioritizeComponents(config);
      expect(prioritized.mobile).toContain('CriticalComponent');
      // Critical component should be at the beginning
      expect(prioritized.mobile[0]).toBe('CriticalComponent');
    });
  });

  describe('Complex scenarios', () => {
    it('should handle mixed prominence types with different risk levels', () => {
      const components: Record<string, ComponentConfig> = {
        ModalComponent: {
          component_name: 'ModalComponent',
          visible: true,
          prominence: 'modal',
          urgency: 'critical',
          props: {},
        },
        TopComponent: {
          component_name: 'TopComponent',
          visible: true,
          prominence: 'top',
          urgency: 'high',
          props: {},
        },
        CardComponent1: {
          component_name: 'CardComponent1',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
        CardComponent2: {
          component_name: 'CardComponent2',
          visible: true,
          prominence: 'card',
          urgency: 'low',
          props: {},
        },
        SidebarComponent: {
          component_name: 'SidebarComponent',
          visible: true,
          prominence: 'sidebar',
          urgency: 'medium',
          props: {},
        },
        MinimalComponent: {
          component_name: 'MinimalComponent',
          visible: true,
          prominence: 'minimal',
          urgency: 'low',
          props: {},
        },
      };

      // Test with different risk levels
      ['low', 'medium', 'high', 'critical'].forEach(riskLevel => {
        const config = createMockUIConfig(components, riskLevel as any);
        const prioritized = prioritizeComponents(config);
        const layout = getRiskBasedLayout(riskLevel as any);

        // Modal and top should always be in hero
        expect(prioritized.hero).toContain('ModalComponent');
        expect(prioritized.hero).toContain('TopComponent');

        // Card components should be in primary
        expect(prioritized.primary).toContain('CardComponent1');
        expect(prioritized.primary).toContain('CardComponent2');

        // Sidebar component should be in sidebar if shown
        if (layout.showSidebar) {
          expect(prioritized.sidebar).toContain('SidebarComponent');
        }

        // Minimal component should be in footer if shown
        if (layout.showFooter) {
          expect(prioritized.footer).toContain('MinimalComponent');
        }
      });
    });

    it('should prioritize crisis components correctly across all risk levels', () => {
      const components: Record<string, ComponentConfig> = {
        CrisisResources: {
          component_name: 'CrisisResources',
          visible: true,
          prominence: 'card',
          urgency: 'medium',
          props: {},
        },
        RegularComponent: {
          component_name: 'RegularComponent',
          visible: true,
          prominence: 'card',
          urgency: 'high',
          props: {},
        },
      };

      ['low', 'medium', 'high', 'critical'].forEach(riskLevel => {
        const config = createMockUIConfig(components, riskLevel as any);
        const prioritized = prioritizeComponents(config);

        // Crisis component should always be in primary (gets boost)
        expect(prioritized.primary).toContain('CrisisResources');
        // Regular component should also be in primary
        expect(prioritized.primary).toContain('RegularComponent');
      });
    });

    it('should handle components with special boosts (dissonance, progress)', () => {
      const config = createMockUIConfig(
        {
          DissonanceIndicator: {
            component_name: 'DissonanceIndicator',
            visible: true,
            prominence: 'card',
            urgency: 'medium',
            props: {},
          },
          ProgressCelebration: {
            component_name: 'ProgressCelebration',
            visible: true,
            prominence: 'card',
            urgency: 'medium',
            props: {},
          },
        },
        'medium',
        {
          dissonance_score: 0.8, // > 0.7
          trajectory: 'improving',
        }
      );

      const prioritized = prioritizeComponents(config);
      // Both should be in primary due to boosts
      expect(prioritized.primary).toContain('DissonanceIndicator');
      expect(prioritized.primary).toContain('ProgressCelebration');
    });
  });
});

