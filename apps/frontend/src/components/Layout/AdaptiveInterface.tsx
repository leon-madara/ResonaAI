/**
 * Adaptive Interface Component
 * 
 * Main component that fetches UIConfig and renders the personalized interface
 * Integrates with overnight builder API and handles change notifications
 */

import React, { useState, useEffect } from 'react';
import { InterfaceRenderer } from '../../components/Layout/InterfaceRenderer';
import { useUIConfig } from '../../hooks/useUIConfig';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../UI/LoadingSpinner';
import ErrorBoundary from '../UI/ErrorBoundary';

interface AdaptiveInterfaceProps {
  userKey: string | null; // User's encryption key
  onConfigUpdate?: (config: any) => void; // Callback when config updates
}

export function AdaptiveInterface({ userKey, onConfigUpdate }: AdaptiveInterfaceProps) {
  const { user } = useAuth();
  const { config, loading, error, refetch, hasUpdate } = useUIConfig(userKey, true);
  const [showUpdateNotification, setShowUpdateNotification] = useState(false);

  // Notify parent of config updates
  useEffect(() => {
    if (config && onConfigUpdate) {
      onConfigUpdate(config);
    }
  }, [config, onConfigUpdate]);

  // Show update notification when available
  useEffect(() => {
    if (hasUpdate) {
      setShowUpdateNotification(true);
    }
  }, [hasUpdate]);

  const handleUpdate = async () => {
    setShowUpdateNotification(false);
    await refetch();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
        <p className="ml-4 text-gray-600">Loading your personalized interface...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Failed to Load Interface</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={refetch}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">No Interface Configuration</h2>
          <p className="text-gray-600">
            Your personalized interface is being prepared. Please check back later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      {/* Update notification banner */}
      {showUpdateNotification && (
        <div className="bg-blue-600 text-white p-4 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex-1">
              <div className="font-semibold mb-1">Interface Update Available</div>
              <div className="text-sm text-blue-100">
                Your interface has been updated with new insights. Refresh to see changes.
              </div>
            </div>
            <div className="flex gap-2 ml-4">
              <button
                onClick={handleUpdate}
                className="px-4 py-2 bg-white text-blue-600 rounded hover:bg-blue-50 transition-colors"
              >
                Update Now
              </button>
              <button
                onClick={() => setShowUpdateNotification(false)}
                className="px-4 py-2 text-white hover:text-blue-200 transition-colors"
              >
                Later
              </button>
            </div>
          </div>
        </div>
      )}

      <InterfaceRenderer config={config} />
    </ErrorBoundary>
  );
}

