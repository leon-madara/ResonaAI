/**
 * Interface Renderer
 *
 * Takes UIConfig and renders the complete personalized interface
 * - Applies theme
 * - Renders layout sections (hero, primary, sidebar, footer)
 * - Dynamically loads components from registry
 * - Handles mobile vs desktop layouts
 */

import React, { Suspense, useState, useEffect } from 'react';
import { UIConfig, ComponentConfig } from '../../types';
import { ThemeProvider } from '../../theme/ThemeProvider';
import { getComponent } from '../../registry/ComponentRegistry';
import { getResponsiveLayoutClasses } from '../../theme/styles';

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

  const layoutClasses = getResponsiveLayoutClasses();

  return (
    <ThemeProvider theme={config.theme}>
      <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)] transition-colors duration-500">
        {/* Change notification (if any unacknowledged changes) */}
        {config.changes.length > 0 && (
          <ChangeNotification changes={config.changes} />
        )}

        {/* Main content */}
        <div className="max-w-7xl mx-auto px-4 py-8">
          {isMobile ? (
            // Mobile layout (single column, top 5-7 components)
            <MobileLayout config={config} />
          ) : (
            // Desktop layout (hero + 2-column primary/sidebar)
            <DesktopLayout config={config} layoutClasses={layoutClasses} />
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
  layoutClasses: ReturnType<typeof getResponsiveLayoutClasses>;
}

function DesktopLayout({ config, layoutClasses }: DesktopLayoutProps) {
  const { layout, components } = config;

  return (
    <div className="space-y-8">
      {/* Hero section (full width) */}
      {layout.hero.length > 0 && (
        <section className={layoutClasses.hero}>
          {layout.hero.map(componentName => (
            <ComponentRenderer
              key={componentName}
              componentName={componentName}
              config={components[componentName]}
            />
          ))}
        </section>
      )}

      {/* Primary + Sidebar (2-column) */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Primary section */}
        {layout.primary.length > 0 && (
          <section className={layoutClasses.primary}>
            {layout.primary.map(componentName => (
              <ComponentRenderer
                key={componentName}
                componentName={componentName}
                config={components[componentName]}
              />
            ))}
          </section>
        )}

        {/* Sidebar section */}
        {layout.sidebar.length > 0 && (
          <aside className={layoutClasses.sidebar}>
            {layout.sidebar.map(componentName => (
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
      {layout.footer.length > 0 && (
        <footer className={layoutClasses.footer}>
          {layout.footer.map(componentName => (
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
  const { mobile_layout, components } = config;

  return (
    <div className="space-y-4">
      {mobile_layout.map(componentName => (
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
  const Component = getComponent(componentName);

  if (!Component) {
    console.warn(`Component "${componentName}" not found in registry`);
    return null;
  }

  if (!config.visible || config.prominence === 'hidden') {
    return null;
  }

  return (
    <Suspense fallback={<ComponentSkeleton prominence={config.prominence} />}>
      <Component
        {...config.props}
        prominence={config.prominence}
        urgency={config.urgency}
      />
    </Suspense>
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
    <div className="bg-blue-600 text-white p-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex-1">
          <div className="font-semibold mb-1">Your interface has been updated</div>
          <div className="text-sm text-blue-100">
            {importantChanges[0].reason}
          </div>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="ml-4 text-white hover:text-blue-200 transition-colors"
        >
          ✕
        </button>
      </div>
    </div>
  );
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
    <div className={`animate-pulse bg-gray-200 rounded-lg ${heights[prominence]}`} />
  );
}

// ============================================================================
// PRIVACY FOOTER
// ============================================================================

function PrivacyFooter() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 mt-16 border-t border-gray-200">
      <div className="text-center text-sm text-gray-500 space-y-2">
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
        <div className="text-xs text-gray-400">
          This interface is uniquely yours, built overnight based on your voice patterns.
        </div>
      </div>
    </div>
  );
}
