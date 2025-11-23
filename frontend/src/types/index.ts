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
// COMPONENT PROP TYPES
// ============================================================================

export interface VoiceRecorderProps {
  prompt: string;
  culturalMode: 'swahili' | 'english' | 'mixed';
  encouragement: string;
  prominence: Prominence;
  urgency: Urgency;
}

export interface CulturalGreetingProps {
  language: 'swahili' | 'english' | 'mixed';
  timeOfDay?: 'morning' | 'afternoon' | 'evening' | 'night';
  mood: 'warm' | 'gentle' | 'concerned' | 'celebratory';
  personalization: string;
  userName?: string;
  prominence: Prominence;
  urgency: Urgency;
}

export interface DissonanceIndicatorProps {
  dissonance_score: number;
  gap_explanation: string;
  truth_signal: string;
  example?: {
    stated: string;
    voice_showed: string;
  };
  prominence: Prominence;
  urgency: Urgency;
}

export interface CrisisResourcesProps {
  risk_level: 'medium' | 'high' | 'critical';
  resources: Array<{
    name: string;
    phone: string;
    available: string;
  }>;
  tone: 'supportive' | 'urgent';
  prominence: Prominence;
  urgency: Urgency;
}

export interface GentleObservationsProps {
  observations: string[];
  tone: 'gentle';
  culturalSensitivity: 'low' | 'medium' | 'high';
  prominence: Prominence;
  urgency: Urgency;
}

export interface WhatsWorkingProps {
  strategies: string[];
  effectiveness: number[];
  encouragement: string;
  prominence: Prominence;
  urgency: Urgency;
}

export interface ProgressCelebrationProps {
  message: string;
  trajectory: 'improving' | 'stable' | 'declining' | 'volatile';
  show_chart: boolean;
  prominence: Prominence;
  urgency: Urgency;
}

export interface TriggerAwarenessProps {
  triggers: string[];
  most_severe?: string;
  educational: boolean;
  prominence: Prominence;
  urgency: Urgency;
}

export interface SafetyCheckProps {
  questions: string[];
  resources_immediate: boolean;
  prominence: Prominence;
  urgency: Urgency;
}

export interface PersonalizedResourcesProps {
  resources: string[];
  language: 'swahili' | 'english' | 'mixed';
  prominence: Prominence;
  urgency: Urgency;
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

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface EncryptedUIConfigResponse {
  encrypted_config: string;
  salt: string;
  version: number;
}

export interface VoiceUploadResponse {
  session_id: string;
  processed: boolean;
  voice_emotion?: string;
  dissonance_detected?: boolean;
}

// ============================================================================
// STORE TYPES
// ============================================================================

export interface ConfigStore {
  config: UIConfig | null;
  loading: boolean;
  error: string | null;

  setConfig: (config: UIConfig) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearConfig: () => void;
}

export interface AudioStore {
  isRecording: boolean;
  audioBlob: Blob | null;
  duration: number;

  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  clearAudio: () => void;
}
