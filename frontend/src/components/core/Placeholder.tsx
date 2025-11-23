/**
 * Placeholder Component
 *
 * Used for components not yet implemented
 * Shows component name and props for development
 */

import React from 'react';
import { ComponentWrapper } from '../layout/ComponentWrapper';

interface PlaceholderProps {
  component_name?: string;
  prominence: any;
  urgency: any;
  [key: string]: any;
}

export function Placeholder({ component_name, prominence, urgency, ...props }: PlaceholderProps) {
  return (
    <ComponentWrapper prominence={prominence} urgency={urgency}>
      <div className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-6">
        <div className="text-center space-y-2">
          <div className="text-2xl">🚧</div>
          <div className="font-semibold text-gray-700">
            {component_name || 'Component'} (Coming Soon)
          </div>
          <div className="text-sm text-gray-500">
            This component will be implemented soon
          </div>
        </div>

        {/* Show props for development */}
        {Object.keys(props).length > 0 && (
          <details className="mt-4">
            <summary className="text-xs text-gray-500 cursor-pointer">View Props</summary>
            <pre className="mt-2 text-xs bg-white p-2 rounded overflow-auto">
              {JSON.stringify(props, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </ComponentWrapper>
  );
}
