/**
 * Interface Renderer
 *
 * Takes UIConfig and renders the complete personalized interface
 * - Applies theme
 * - Renders layout sections (hero, primary, sidebar, footer)
 * - Dynamically loads components from registry
 * - Handles mobile vs desktop layouts
 * - Implements prominence-based rendering (modal, top, card, sidebar, minimal)
 * - Implements priority-based layout with risk-based component ordering
 */

import React, { Suspense, useState, useEffect, useMemo } from 'react';
import { UIConfig, ComponentConfig } from '../../types';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { getComponentWrapperClasses, shouldRenderComponent } from '../../utils/prominence';
import { prioritizeComponents, getRiskBasedLayout } from '../../utils/layoutPrioritizer';

interface InterfaceRendererProps {
  config: UIConfig;
}

export function InterfaceRenderer({ config }: InterfaceRendererProps) {
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text-primary)] transition-colors duration-[var(--animation-duration-normal)]">
        {/* Change notification (if any unacknowledged changes) */}
        {config.changes.length > 0 && (
          <ChangeNotification changes={config.changes} />
        )}

        {/* Main content */}
        <div className="max-w-7xl mx-auto px-[var(--spacing-container-padding)] py-[var(--spacing-component-gap)]">
          {isMobile ? (
            // Mobile layout (single column, top 5-7 components)
            <MobileLayout config={config} />
          ) : (
            // Desktop layout (hero + 2-column primary/sidebar)
            <DesktopLayout config={config} />
          )}
        </div>

        {/* Privacy footer */}
        <PrivacyFooter />
      </div>
    </ThemeProvider>
  );
}

// ============================================================================
// DESKTOP LAYOUT
// ============================================================================

interface DesktopLayoutProps {
  config: UIConfig;
}

function DesktopLayout({ config }: DesktopLayoutProps) {
  const { components, metadata } = config;
  
  // Prioritize components based on risk level and urgency
  const prioritizedLayout = useMemo(() => {
    return prioritizeComponents(config);
  }, [config]);

  // Get risk-based layout adjustments
  const layoutAdjustments = useMemo(() => {
    return getRiskBasedLayout(metadata.risk_level);
  }, [metadata.risk_level]);

  // Apply risk-based filtering
  const hero = layoutAdjustments.compactMode 
    ? prioritizedLayout.hero.slice(0, 1)
    : prioritizedLayout.hero;
  const primary = prioritizedLayout.primary.slice(0, layoutAdjustments.maxComponents);
  const sidebar = layoutAdjustments.showSidebar 
    ? prioritizedLayout.sidebar.slice(0, 3)
    : [];
  const footer = layoutAdjustments.showFooter 
    ? prioritizedLayout.footer.slice(0, 2)
    : [];

  return (
    <div className="space-y-[var(--spacing-component-gap)]">
      {/* Hero section (full width) */}
      {hero.length > 0 && (
        <section className="w-full mb-[var(--spacing-component-gap)]">
          {hero.map(componentName => (
            <ComponentRenderer
              key={componentName}
              componentName={componentName}
              config={components[componentName]}
            />
          ))}
        </section>
      )}

      {/* Primary + Sidebar (2-column) */}
      <div className="flex flex-col lg:flex-row gap-[var(--spacing-component-gap)]">
        {/* Primary section */}
        {primary.length > 0 && (
          <section className="w-full lg:w-2/3 lg:pr-[calc(var(--spacing-component-gap)*0.5)]">
            {primary.map(componentName => (
              <ComponentRenderer
                key={componentName}
                componentName={componentName}
                config={components[componentName]}
              />
            ))}
          </section>
        )}

        {/* Sidebar section */}
        {sidebar.length > 0 && (
          <aside className="w-full lg:w-1/3 lg:pl-[calc(var(--spacing-component-gap)*0.5)] mt-[var(--spacing-component-gap)] lg:mt-0">
            {sidebar.map(componentName => (
              <ComponentRenderer
                key={componentName}
                componentName={componentName}
                config={components[componentName]}
              />
            ))}
          </aside>
        )}
      </div>

      {/* Footer section */}
      {footer.length > 0 && (
        <footer className="w-full mt-[calc(var(--spacing-component-gap)*2)]">
          {footer.map(componentName => (
            <ComponentRenderer
              key={componentName}
              componentName={componentName}
              config={components[componentName]}
            />
          ))}
        </footer>
      )}
    </div>
  );
}

// ============================================================================
// MOBILE LAYOUT
// ============================================================================

interface MobileLayoutProps {
  config: UIConfig;
}

function MobileLayout({ config }: MobileLayoutProps) {
  const { components, metadata } = config;
  
  // Prioritize components for mobile
  const prioritizedLayout = useMemo(() => {
    return prioritizeComponents(config);
  }, [config]);

  // Mobile layout uses prioritized order, limited to top 7 components
  const mobileComponents = prioritizedLayout.mobile.slice(0, 7);

  return (
    <div className="space-y-[calc(var(--spacing-component-gap)*0.75)]">
      {mobileComponents.map(componentName => (
        <ComponentRenderer
          key={componentName}
          componentName={componentName}
          config={components[componentName]}
        />
      ))}
    </div>
  );
}

// ============================================================================
// COMPONENT RENDERER
// ============================================================================

interface ComponentRendererProps {
  componentName: string;
  config: ComponentConfig;
}

function ComponentRenderer({ componentName, config }: ComponentRendererProps) {
  // Check if component should be rendered
  if (!shouldRenderComponent(config.prominence, config.visible)) {
    return null;
  }

  // Get component from registry (placeholder - needs actual component registry)
  const Component = getComponent(componentName);

  if (!Component) {
    console.warn(`Component "${componentName}" not found in registry`);
    return null;
  }

  // Get prominence-based wrapper classes
  const wrapperClasses = getComponentWrapperClasses(config.prominence, config.urgency);

  // Modal components need special handling
  if (config.prominence === 'modal') {
    return (
      <div className={wrapperClasses} role="dialog" aria-modal="true">
        <div className="min-h-screen flex items-center justify-center p-[var(--spacing-container-padding)]">
          <div className="max-w-2xl w-full">
            <Suspense fallback={<ComponentSkeleton prominence={config.prominence} />}>
              <Component
                {...config.props}
                prominence={config.prominence}
                urgency={config.urgency}
              />
            </Suspense>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={wrapperClasses}>
      <Suspense fallback={<ComponentSkeleton prominence={config.prominence} />}>
        <Component
          {...config.props}
          prominence={config.prominence}
          urgency={config.urgency}
        />
      </Suspense>
    </div>
  );
}

// ============================================================================
// COMPONENT REGISTRY (Placeholder - needs actual implementation)
// ============================================================================

function getComponent(componentName: string): React.ComponentType<any> | null {
  // This is a placeholder - actual implementation would use a component registry
  // For now, return null to avoid errors
  console.warn(`Component registry not implemented. Component: ${componentName}`);
  return null;
}

// ============================================================================
// COMPONENT SKELETON (Loading state)
// ============================================================================

interface ComponentSkeletonProps {
  prominence: ComponentConfig['prominence'];
}

function ComponentSkeleton({ prominence }: ComponentSkeletonProps) {
  const heights = {
    modal: 'h-screen',
    top: 'h-48',
    card: 'h-32',
    sidebar: 'h-24',
    minimal: 'h-12',
    hidden: 'h-0'
  };

  return (
    <div className={`animate-pulse bg-[var(--color-surface)] rounded-[var(--border-radius-md)] ${heights[prominence]}`} />
  );
}

// ============================================================================
// CHANGE NOTIFICATION
// ============================================================================

interface ChangeNotificationProps {
  changes: UIConfig['changes'];
}

function ChangeNotification({ changes }: ChangeNotificationProps) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  // Only show high severity changes in notification
  const importantChanges = changes.filter(c => ['high', 'critical'].includes(c.severity));

  if (importantChanges.length === 0) return null;

  return (
    <div className="bg-[var(--color-primary)] text-white p-[var(--spacing-container-padding)]">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex-1">
          <div className="font-semibold mb-1">Your interface has been updated</div>
          <div className="text-sm opacity-90">
            {importantChanges[0].reason}
          </div>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="ml-4 text-white hover:opacity-80 transition-opacity"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// PRIVACY FOOTER
// ============================================================================

function PrivacyFooter() {
  return (
    <div className="max-w-7xl mx-auto px-[var(--spacing-container-padding)] py-[var(--spacing-component-gap)] mt-[calc(var(--spacing-component-gap)*2)] border-t border-[var(--color-text-tertiary)]/20">
      <div className="text-center text-[var(--font-size-sm)] text-[var(--color-text-secondary)] space-y-2">
        <div className="flex items-center justify-center gap-4">
          <span className="flex items-center gap-1">
            <span>🔒</span>
            <span>End-to-end encrypted</span>
          </span>
          <span className="flex items-center gap-1">
            <span>🗑️</span>
            <span>Audio deleted after 7 days</span>
          </span>
          <span className="flex items-center gap-1">
            <span>🔐</span>
            <span>Anonymized patterns only</span>
          </span>
        </div>
        <div className="text-xs opacity-75">
          This interface is uniquely yours, built overnight based on your voice patterns.
        </div>
      </div>
    </div>
  );
}

