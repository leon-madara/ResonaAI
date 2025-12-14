/**
 * Layout Prioritizer
 * 
 * Implements priority-based layout system with risk-based component ordering
 * Components are ordered by urgency, risk level, and prominence
 */

import { UIConfig, ComponentConfig, Prominence, Urgency } from '../types';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

interface ComponentPriority {
  componentName: string;
  config: ComponentConfig;
  priority: number;
  riskLevel: RiskLevel;
  urgency: Urgency;
  prominence: Prominence;
}

/**
 * Calculate priority score for a component
 * Higher score = higher priority (rendered first)
 */
function calculatePriorityScore(
  component: ComponentConfig,
  riskLevel: RiskLevel,
  metadata: UIConfig['metadata']
): number {
  let score = 0;

  // Base score from urgency (0-100)
  const urgencyScores: Record<Urgency, number> = {
    none: 0,
    low: 25,
    medium: 50,
    high: 75,
    critical: 100,
  };
  score += urgencyScores[component.urgency] || 0;

  // Risk level multiplier (0.5x to 2x)
  const riskMultipliers: Record<RiskLevel, number> = {
    low: 0.5,
    medium: 1.0,
    high: 1.5,
    critical: 2.0,
  };
  score *= riskMultipliers[riskLevel] || 1.0;

  // Prominence bonus (0-50)
  const prominenceBonuses: Record<Prominence, number> = {
    hidden: 0,
    minimal: 10,
    sidebar: 20,
    card: 30,
    top: 40,
    modal: 50,
  };
  score += prominenceBonuses[component.prominence] || 0;

  // Crisis components get extra boost
  if (component.component_name === 'CrisisResources' || component.component_name === 'SafetyCheck') {
    score += 50;
  }

  // Dissonance indicator gets boost if dissonance score is high
  if (component.component_name === 'DissonanceIndicator' && metadata.dissonance_score > 0.7) {
    score += 30;
  }

  // Progress celebration gets boost if trajectory is improving
  if (component.component_name === 'ProgressCelebration' && metadata.trajectory === 'improving') {
    score += 20;
  }

  return score;
}

/**
 * Sort components by priority (highest first)
 */
function sortByPriority(components: ComponentPriority[]): ComponentPriority[] {
  return [...components].sort((a, b) => b.priority - a.priority);
}

/**
 * Prioritize components based on risk level and urgency
 */
export function prioritizeComponents(
  config: UIConfig
): {
  hero: string[];
  primary: string[];
  sidebar: string[];
  footer: string[];
  mobile: string[];
} {
  const { components, layout, metadata } = config;
  const riskLevel: RiskLevel = metadata.risk_level;

  // Calculate priority for each component
  const componentPriorities: ComponentPriority[] = Object.entries(components)
    .filter(([_, component]) => component.visible && component.prominence !== 'hidden')
    .map(([componentName, component]) => ({
      componentName,
      config: component,
      priority: calculatePriorityScore(component, riskLevel, metadata),
      riskLevel,
      urgency: component.urgency,
      prominence: component.prominence,
    }));

  // Sort by priority
  const sorted = sortByPriority(componentPriorities);

  // Distribute components across layout sections based on priority and prominence
  const hero: string[] = [];
  const primary: string[] = [];
  const sidebar: string[] = [];
  const footer: string[] = [];
  const mobile: string[] = [];

  for (const { componentName, prominence, priority } of sorted) {
    // Modal prominence always goes to hero (full-width)
    if (prominence === 'modal') {
      hero.push(componentName);
      mobile.push(componentName);
      continue;
    }

    // Top prominence goes to hero
    if (prominence === 'top') {
      hero.push(componentName);
      mobile.push(componentName);
      continue;
    }

    // High priority components go to primary section
    if (priority >= 100 || prominence === 'card') {
      primary.push(componentName);
      mobile.push(componentName);
      continue;
    }

    // Medium priority goes to sidebar
    if (priority >= 50 || prominence === 'sidebar') {
      sidebar.push(componentName);
      // Only top 3 sidebar items on mobile
      if (sidebar.length <= 3) {
        mobile.push(componentName);
      }
      continue;
    }

    // Low priority goes to footer
    footer.push(componentName);
    // Footer items not shown on mobile (or only last 2)
    if (footer.length <= 2) {
      mobile.push(componentName);
    }
  }

  // Ensure critical components are always visible
  const criticalComponents = sorted
    .filter(c => c.urgency === 'critical' || c.config.component_name === 'CrisisResources')
    .map(c => c.componentName);

  // Add critical components to mobile if not already present
  for (const componentName of criticalComponents) {
    if (!mobile.includes(componentName)) {
      mobile.unshift(componentName); // Add to beginning
    }
  }

  // Limit mobile layout to top 7 components for performance
  const mobileLimited = mobile.slice(0, 7);

  return {
    hero: hero.length > 0 ? hero : layout.hero,
    primary: primary.length > 0 ? primary : layout.primary,
    sidebar: sidebar.length > 0 ? sidebar : layout.sidebar,
    footer: footer.length > 0 ? footer : layout.footer,
    mobile: mobileLimited.length > 0 ? mobileLimited : config.mobile_layout,
  };
}

/**
 * Get risk-based layout adjustments
 */
export function getRiskBasedLayout(riskLevel: RiskLevel): {
  maxComponents: number;
  showSidebar: boolean;
  showFooter: boolean;
  compactMode: boolean;
} {
  switch (riskLevel) {
    case 'critical':
      return {
        maxComponents: 3, // Only show most critical
        showSidebar: false,
        showFooter: false,
        compactMode: true,
      };
    case 'high':
      return {
        maxComponents: 5,
        showSidebar: true,
        showFooter: false,
        compactMode: true,
      };
    case 'medium':
      return {
        maxComponents: 8,
        showSidebar: true,
        showFooter: true,
        compactMode: false,
      };
    case 'low':
    default:
      return {
        maxComponents: 12,
        showSidebar: true,
        showFooter: true,
        compactMode: false,
      };
  }
}

