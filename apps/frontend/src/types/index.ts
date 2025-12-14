/**
 * TypeScript type definitions for ResonaAI Frontend
 *
 * These types match the backend UIConfig structure
 */

// ============================================================================
// THEME TYPES
// ============================================================================

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  text: string;
  accent: string;
  warning: string;
}

export interface ThemeConfig {
  name: string;
  base: 'calm' | 'warm' | 'crisis' | 'balanced' | 'adaptive';
  overlay?: string;
  colors: ThemeColors;
  spacing: 'compressed' | 'comfortable' | 'spacious';
  animations: 'none' | 'gentle' | 'moderate';
  contrast: 'low' | 'medium' | 'high';
  fontScale: number;
  description: string;
}

// ============================================================================
// COMPONENT TYPES
// ============================================================================

export type Prominence = 'modal' | 'top' | 'card' | 'sidebar' | 'minimal' | 'hidden';
export type Urgency = 'none' | 'low' | 'medium' | 'high' | 'critical';

export interface ComponentConfig {
  component_name: string;
  visible: boolean;
  prominence: Prominence;
  props: Record<string, any>;
  urgency: Urgency;
}

export interface ComponentConfigs {
  [componentName: string]: ComponentConfig;
}

// ============================================================================
// LAYOUT TYPES
// ============================================================================

export interface LayoutSections {
  hero: string[];
  primary: string[];
  sidebar: string[];
  footer: string[];
}

// ============================================================================
// CHANGE TYPES
// ============================================================================

export interface InterfaceChange {
  change_type: string;
  component: string;
  reason: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// ============================================================================
// UI CONFIG (Main Interface Configuration)
// ============================================================================

export interface UIConfig {
  user_id: string;
  generated_at: string;
  version: string;

  // Theme
  theme: ThemeConfig;

  // Components
  components: ComponentConfigs;

  // Layout
  layout: LayoutSections;
  mobile_layout: string[];

  // Cultural context
  cultural: {
    language?: 'swahili' | 'english' | 'mixed';
    greeting_style?: string;
    directness?: 'low' | 'medium' | 'high';
    validation_style?: 'subtle' | 'gentle';
  };

  // Changes from previous config
  changes: InterfaceChange[];

  // Metadata
  metadata: {
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    trajectory: 'improving' | 'stable' | 'declining' | 'volatile';
    primary_emotions: string[];
    primary_language: 'swahili' | 'english' | 'mixed';
    session_count: number;
    dissonance_score: number;
    trigger_count: number;
    effective_coping_count: number;
  };
}

