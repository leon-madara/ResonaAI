/**
 * Component Registry
 *
 * Maps component names (from UIConfig) to React components
 * Enables dynamic component rendering based on overnight builds
 */

import { lazy } from 'react';

// Import core components (lazy for code splitting)
const VoiceRecorder = lazy(() => import('../components/core/VoiceRecorder').then(m => ({ default: m.VoiceRecorder })));
const CulturalGreeting = lazy(() => import('../components/core/CulturalGreeting').then(m => ({ default: m.CulturalGreeting })));
const DissonanceIndicator = lazy(() => import('../components/core/DissonanceIndicator').then(m => ({ default: m.DissonanceIndicator })));
const CrisisResources = lazy(() => import('../components/core/CrisisResources').then(m => ({ default: m.CrisisResources })));
const ProgressCelebration = lazy(() => import('../components/core/ProgressCelebration').then(m => ({ default: m.ProgressCelebration })));
const SafetyCheck = lazy(() => import('../components/core/SafetyCheck').then(m => ({ default: m.SafetyCheck })));

// Placeholder components for not-yet-implemented components
const GentleObservations = lazy(() => import('../components/core/Placeholder').then(m => ({ default: m.Placeholder })));
const WhatsWorking = lazy(() => import('../components/core/Placeholder').then(m => ({ default: m.Placeholder })));
const TriggerAwareness = lazy(() => import('../components/core/Placeholder').then(m => ({ default: m.Placeholder })));
const PersonalizedResources = lazy(() => import('../components/core/Placeholder').then(m => ({ default: m.Placeholder })));

/**
 * Component Registry
 * Maps component name (string) → React Component
 */
export const ComponentRegistry: Record<string, React.LazyExoticComponent<any>> = {
  VoiceRecorder,
  CulturalGreeting,
  DissonanceIndicator,
  CrisisResources,
  GentleObservations,
  WhatsWorking,
  ProgressCelebration,
  TriggerAwareness,
  SafetyCheck,
  PersonalizedResources,
};

/**
 * Check if a component exists in the registry
 */
export function hasComponent(componentName: string): boolean {
  return componentName in ComponentRegistry;
}

/**
 * Get component from registry
 */
export function getComponent(componentName: string): React.LazyExoticComponent<any> | null {
  return ComponentRegistry[componentName] || null;
}
