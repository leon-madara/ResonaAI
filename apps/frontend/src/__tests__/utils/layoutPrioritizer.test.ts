/**
 * Tests for Layout Prioritizer Utilities
 * 
 * Tests priority-based layout system with risk-based component ordering
 */

import { prioritizeComponents, getRiskBasedLayout } from '../../utils/layoutPrioritizer';
import { UIConfig, ComponentConfig, RiskLevel } from '../../types';

// Helper function to create mock UIConfig
function createMockUIConfig(
  components: Record<string, ComponentConfig>,
  riskLevel: RiskLevel = 'medium',
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

describe('Layout Prioritizer Utilities', () => {
  describe('getRiskBasedLayout', () => {
    it('should return correct layout for critical risk', () => {
      const layout = getRiskBasedLayout('critical');
      expect(layout).toEqual({
        maxComponents: 3,
        showSidebar: false,
        showFooter: false,
        compactMode: true,
      });
    });

    it('should return correct layout for high risk', () => {
      const layout = getRiskBasedLayout('high');
      expect(layout).toEqual({
        maxComponents: 5,
        showSidebar: true,
        showFooter: false,
        compactMode: true,
      });
    });

    it('should return correct layout for medium risk', () => {
      const layout = getRiskBasedLayout('medium');
      expect(layout).toEqual({
        maxComponents: 8,
        showSidebar: true,
        showFooter: true,
        compactMode: false,
      });
    });

    it('should return correct layout for low risk', () => {
      const layout = getRiskBasedLayout('low');
      expect(layout).toEqual({
        maxComponents: 12,
        showSidebar: true,
        showFooter: true,
        compactMode: false,
      });
    });
  });

  describe('prioritizeComponents', () => {
    describe('Component distribution by prominence', () => {
      it('should place modal prominence components in hero section', () => {
        const config = createMockUIConfig({
          ModalComponent: {
            component_name: 'ModalComponent',
            visible: true,
            prominence: 'modal',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.hero).toContain('ModalComponent');
        expect(result.mobile).toContain('ModalComponent');
      });

      it('should place top prominence components in hero section', () => {
        const config = createMockUIConfig({
          TopComponent: {
            component_name: 'TopComponent',
            visible: true,
            prominence: 'top',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.hero).toContain('TopComponent');
        expect(result.mobile).toContain('TopComponent');
      });

      it('should place card prominence components in primary section', () => {
        const config = createMockUIConfig({
          CardComponent: {
            component_name: 'CardComponent',
            visible: true,
            prominence: 'card',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.primary).toContain('CardComponent');
        expect(result.mobile).toContain('CardComponent');
      });

      it('should place sidebar prominence components in sidebar section', () => {
        const config = createMockUIConfig({
          SidebarComponent: {
            component_name: 'SidebarComponent',
            visible: true,
            prominence: 'sidebar',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.sidebar).toContain('SidebarComponent');
        expect(result.mobile).toContain('SidebarComponent');
      });

      it('should place minimal prominence components in footer section', () => {
        const config = createMockUIConfig({
          MinimalComponent: {
            component_name: 'MinimalComponent',
            visible: true,
            prominence: 'minimal',
            urgency: 'low',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.footer).toContain('MinimalComponent');
      });

      it('should not include hidden components', () => {
        const config = createMockUIConfig({
          HiddenComponent: {
            component_name: 'HiddenComponent',
            visible: true,
            prominence: 'hidden',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.hero).not.toContain('HiddenComponent');
        expect(result.primary).not.toContain('HiddenComponent');
        expect(result.sidebar).not.toContain('HiddenComponent');
        expect(result.footer).not.toContain('HiddenComponent');
        expect(result.mobile).not.toContain('HiddenComponent');
      });

      it('should not include invisible components', () => {
        const config = createMockUIConfig({
          InvisibleComponent: {
            component_name: 'InvisibleComponent',
            visible: false,
            prominence: 'card',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.hero).not.toContain('InvisibleComponent');
        expect(result.primary).not.toContain('InvisibleComponent');
        expect(result.mobile).not.toContain('InvisibleComponent');
      });
    });

    describe('Priority-based ordering', () => {
      it('should sort components by priority score (highest first)', () => {
        const config = createMockUIConfig({
          LowPriority: {
            component_name: 'LowPriority',
            visible: true,
            prominence: 'minimal',
            urgency: 'low',
            props: {},
          },
          HighPriority: {
            component_name: 'HighPriority',
            visible: true,
            prominence: 'card',
            urgency: 'high',
            props: {},
          },
          MediumPriority: {
            component_name: 'MediumPriority',
            visible: true,
            prominence: 'sidebar',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        // High priority should be in primary (higher priority section)
        expect(result.primary).toContain('HighPriority');
        // Medium priority should be in sidebar
        expect(result.sidebar).toContain('MediumPriority');
        // Low priority should be in footer
        expect(result.footer).toContain('LowPriority');
      });

      it('should apply risk level multipliers correctly', () => {
        // Critical risk should boost priority scores (2x multiplier)
        const criticalConfig = createMockUIConfig(
          {
            TestComponent: {
              component_name: 'TestComponent',
              visible: true,
              prominence: 'card',
              urgency: 'high', // Base: 75
              props: {},
            },
          },
          'critical'
        );

        const criticalResult = prioritizeComponents(criticalConfig);
        // With critical risk (2x multiplier), score = 75 * 2 + 30 (card) = 180
        // This should go to primary (priority >= 100)
        expect(criticalResult.primary).toContain('TestComponent');

        // Low risk should reduce priority scores (0.5x multiplier)
        const lowConfig = createMockUIConfig(
          {
            TestComponent: {
              component_name: 'TestComponent',
              visible: true,
              prominence: 'card',
              urgency: 'high', // Base: 75
              props: {},
            },
          },
          'low'
        );

        const lowResult = prioritizeComponents(lowConfig);
        // With low risk (0.5x multiplier), score = 75 * 0.5 + 30 (card) = 67.5
        // This should still go to primary (card prominence always goes to primary)
        expect(lowResult.primary).toContain('TestComponent');
      });

      it('should apply urgency scores correctly', () => {
        const config = createMockUIConfig({
          NoneUrgency: {
            component_name: 'NoneUrgency',
            visible: true,
            prominence: 'minimal',
            urgency: 'none', // Base: 0
            props: {},
          },
          LowUrgency: {
            component_name: 'LowUrgency',
            visible: true,
            prominence: 'minimal',
            urgency: 'low', // Base: 25
            props: {},
          },
          MediumUrgency: {
            component_name: 'MediumUrgency',
            visible: true,
            prominence: 'minimal',
            urgency: 'medium', // Base: 50
            props: {},
          },
          HighUrgency: {
            component_name: 'HighUrgency',
            visible: true,
            prominence: 'minimal',
            urgency: 'high', // Base: 75
            props: {},
          },
          CriticalUrgency: {
            component_name: 'CriticalUrgency',
            visible: true,
            prominence: 'minimal',
            urgency: 'critical', // Base: 100
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        // Critical urgency should be in primary (score >= 100)
        expect(result.primary).toContain('CriticalUrgency');
        // High urgency should be in primary (score >= 100 with medium risk)
        expect(result.primary).toContain('HighUrgency');
        // Medium urgency should be in sidebar (score >= 50)
        expect(result.sidebar).toContain('MediumUrgency');
        // Low urgency should be in footer
        expect(result.footer).toContain('LowUrgency');
        // None urgency should be in footer
        expect(result.footer).toContain('NoneUrgency');
      });

      it('should apply prominence bonuses correctly', () => {
        const config = createMockUIConfig({
          ModalComp: {
            component_name: 'ModalComp',
            visible: true,
            prominence: 'modal', // +50 bonus
            urgency: 'none', // Base: 0
            props: {},
          },
          TopComp: {
            component_name: 'TopComp',
            visible: true,
            prominence: 'top', // +40 bonus
            urgency: 'none', // Base: 0
            props: {},
          },
          CardComp: {
            component_name: 'CardComp',
            visible: true,
            prominence: 'card', // +30 bonus
            urgency: 'none', // Base: 0
            props: {},
          },
          SidebarComp: {
            component_name: 'SidebarComp',
            visible: true,
            prominence: 'sidebar', // +20 bonus
            urgency: 'none', // Base: 0
            props: {},
          },
          MinimalComp: {
            component_name: 'MinimalComp',
            visible: true,
            prominence: 'minimal', // +10 bonus
            urgency: 'none', // Base: 0
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        // Modal and top go to hero by prominence
        expect(result.hero).toContain('ModalComp');
        expect(result.hero).toContain('TopComp');
        // Card goes to primary by prominence
        expect(result.primary).toContain('CardComp');
        // Sidebar goes to sidebar by prominence
        expect(result.sidebar).toContain('SidebarComp');
        // Minimal goes to footer
        expect(result.footer).toContain('MinimalComp');
      });
    });

    describe('Special component boosts', () => {
      it('should give crisis components extra boost', () => {
        const config = createMockUIConfig({
          CrisisResources: {
            component_name: 'CrisisResources',
            visible: true,
            prominence: 'card',
            urgency: 'medium', // Base: 50
            props: {},
          },
          SafetyCheck: {
            component_name: 'SafetyCheck',
            visible: true,
            prominence: 'card',
            urgency: 'medium', // Base: 50
            props: {},
          },
          RegularComponent: {
            component_name: 'RegularComponent',
            visible: true,
            prominence: 'card',
            urgency: 'high', // Base: 75 (higher than crisis components)
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        // Crisis components should be in primary (they get +50 boost)
        expect(result.primary).toContain('CrisisResources');
        expect(result.primary).toContain('SafetyCheck');
        // Regular component should also be in primary
        expect(result.primary).toContain('RegularComponent');
      });

      it('should boost dissonance indicator when score > 0.7', () => {
        const config = createMockUIConfig(
          {
            DissonanceIndicator: {
              component_name: 'DissonanceIndicator',
              visible: true,
              prominence: 'card',
              urgency: 'medium', // Base: 50
              props: {},
            },
          },
          'medium',
          { dissonance_score: 0.8 } // > 0.7
        );

        const result = prioritizeComponents(config);
        // Should be in primary due to boost (50 + 30 boost = 80, with card +30 = 110)
        expect(result.primary).toContain('DissonanceIndicator');
      });

      it('should not boost dissonance indicator when score <= 0.7', () => {
        const config = createMockUIConfig(
          {
            DissonanceIndicator: {
              component_name: 'DissonanceIndicator',
              visible: true,
              prominence: 'sidebar',
              urgency: 'low', // Base: 25
              props: {},
            },
          },
          'medium',
          { dissonance_score: 0.5 } // <= 0.7
        );

        const result = prioritizeComponents(config);
        // Should be in sidebar (no boost, score = 25 * 1.0 + 20 = 45)
        expect(result.sidebar).toContain('DissonanceIndicator');
      });

      it('should boost progress celebration when trajectory is improving', () => {
        const config = createMockUIConfig(
          {
            ProgressCelebration: {
              component_name: 'ProgressCelebration',
              visible: true,
              prominence: 'card',
              urgency: 'medium', // Base: 50
              props: {},
            },
          },
          'medium',
          { trajectory: 'improving' }
        );

        const result = prioritizeComponents(config);
        // Should be in primary due to boost (50 + 20 boost = 70, with card +30 = 100)
        expect(result.primary).toContain('ProgressCelebration');
      });

      it('should not boost progress celebration when trajectory is not improving', () => {
        const config = createMockUIConfig(
          {
            ProgressCelebration: {
              component_name: 'ProgressCelebration',
              visible: true,
              prominence: 'sidebar',
              urgency: 'low', // Base: 25
              props: {},
            },
          },
          'medium',
          { trajectory: 'stable' }
        );

        const result = prioritizeComponents(config);
        // Should be in sidebar (no boost, score = 25 * 1.0 + 20 = 45)
        expect(result.sidebar).toContain('ProgressCelebration');
      });
    });

    describe('Mobile layout', () => {
      it('should limit mobile layout to top 7 components', () => {
        const components: Record<string, ComponentConfig> = {};
        // Create 10 components
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
        const result = prioritizeComponents(config);
        expect(result.mobile.length).toBeLessThanOrEqual(7);
      });

      it('should always include critical components on mobile', () => {
        const config = createMockUIConfig({
          CriticalComponent: {
            component_name: 'CriticalComponent',
            visible: true,
            prominence: 'minimal', // Would normally go to footer
            urgency: 'critical',
            props: {},
          },
          CrisisResources: {
            component_name: 'CrisisResources',
            visible: true,
            prominence: 'minimal', // Would normally go to footer
            urgency: 'low',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        // Critical components should be in mobile even if they would go to footer
        expect(result.mobile).toContain('CriticalComponent');
        expect(result.mobile).toContain('CrisisResources');
        // Critical components should be at the beginning
        expect(result.mobile[0]).toBe('CriticalComponent');
        expect(result.mobile[1]).toBe('CrisisResources');
      });

      it('should include modal and top components in mobile', () => {
        const config = createMockUIConfig({
          ModalComponent: {
            component_name: 'ModalComponent',
            visible: true,
            prominence: 'modal',
            urgency: 'medium',
            props: {},
          },
          TopComponent: {
            component_name: 'TopComponent',
            visible: true,
            prominence: 'top',
            urgency: 'medium',
            props: {},
          },
        });

        const result = prioritizeComponents(config);
        expect(result.mobile).toContain('ModalComponent');
        expect(result.mobile).toContain('TopComponent');
      });

      it('should limit sidebar items to top 3 on mobile', () => {
        const components: Record<string, ComponentConfig> = {};
        // Create 5 sidebar components
        for (let i = 0; i < 5; i++) {
          components[`SidebarComponent${i}`] = {
            component_name: `SidebarComponent${i}`,
            visible: true,
            prominence: 'sidebar',
            urgency: 'medium',
            props: {},
          };
        }

        const config = createMockUIConfig(components);
        const result = prioritizeComponents(config);
        // Only first 3 sidebar items should be in mobile
        const sidebarInMobile = result.mobile.filter(name => 
          name.startsWith('SidebarComponent')
        );
        expect(sidebarInMobile.length).toBeLessThanOrEqual(3);
      });

      it('should limit footer items to top 2 on mobile', () => {
        const components: Record<string, ComponentConfig> = {};
        // Create 5 footer components
        for (let i = 0; i < 5; i++) {
          components[`FooterComponent${i}`] = {
            component_name: `FooterComponent${i}`,
            visible: true,
            prominence: 'minimal',
            urgency: 'low',
            props: {},
          };
        }

        const config = createMockUIConfig(components);
        const result = prioritizeComponents(config);
        // Only first 2 footer items should be in mobile
        const footerInMobile = result.mobile.filter(name => 
          name.startsWith('FooterComponent')
        );
        expect(footerInMobile.length).toBeLessThanOrEqual(2);
      });
    });

    describe('Edge cases', () => {
      it('should handle empty components object', () => {
        const config = createMockUIConfig({});
        const result = prioritizeComponents(config);
        expect(result.hero).toEqual([]);
        expect(result.primary).toEqual([]);
        expect(result.sidebar).toEqual([]);
        expect(result.footer).toEqual([]);
        expect(result.mobile).toEqual([]);
      });

      it('should use fallback layout when no components match', () => {
        const config = createMockUIConfig({});
        config.layout = {
          hero: ['fallback-hero'],
          primary: ['fallback-primary'],
          sidebar: ['fallback-sidebar'],
          footer: ['fallback-footer'],
        };
        config.mobile_layout = ['fallback-mobile'];

        const result = prioritizeComponents(config);
        expect(result.hero).toEqual(['fallback-hero']);
        expect(result.primary).toEqual(['fallback-primary']);
        expect(result.sidebar).toEqual(['fallback-sidebar']);
        expect(result.footer).toEqual(['fallback-footer']);
        expect(result.mobile).toEqual(['fallback-mobile']);
      });

      it('should handle components with priority >= 100 going to primary', () => {
        const config = createMockUIConfig(
          {
            HighPriorityComponent: {
              component_name: 'HighPriorityComponent',
              visible: true,
              prominence: 'minimal',
              urgency: 'critical', // Base: 100, with medium risk = 100
              props: {},
            },
          },
          'medium'
        );

        const result = prioritizeComponents(config);
        // Score = 100 * 1.0 + 10 (minimal) = 110, should go to primary
        expect(result.primary).toContain('HighPriorityComponent');
      });

      it('should handle components with priority >= 50 going to sidebar', () => {
        const config = createMockUIConfig(
          {
            MediumPriorityComponent: {
              component_name: 'MediumPriorityComponent',
              visible: true,
              prominence: 'minimal',
              urgency: 'medium', // Base: 50, with medium risk = 50
              props: {},
            },
          },
          'medium'
        );

        const result = prioritizeComponents(config);
        // Score = 50 * 1.0 + 10 (minimal) = 60, should go to sidebar
        expect(result.sidebar).toContain('MediumPriorityComponent');
      });
    });
  });
});

