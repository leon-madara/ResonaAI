/**
 * useUIConfig Hook
 * 
 * Fetches, decrypts, and manages UIConfig state with automatic updates
 */

import { useState, useEffect, useCallback } from 'react';
import { UIConfig } from '../types';
import {
  fetchAndDecryptUIConfig,
  checkUIConfigUpdate,
  setupUIConfigPolling,
  clearUIConfigCache,
} from '../utils/uiconfig';
import { useAuth } from '../contexts/AuthContext';

interface UseUIConfigResult {
  config: UIConfig | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  hasUpdate: boolean;
}

/**
 * Hook to fetch and manage UIConfig
 * @param userKey User's encryption key (derived from password or device)
 * @param autoPoll Whether to automatically poll for updates (default: true)
 * @param pollInterval Polling interval in milliseconds (default: 5 minutes)
 */
export function useUIConfig(
  userKey: string | null,
  autoPoll: boolean = true,
  pollInterval: number = 5 * 60 * 1000
): UseUIConfigResult {
  const { user, token } = useAuth();
  const [config, setConfig] = useState<UIConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasUpdate, setHasUpdate] = useState(false);

  const fetchConfig = useCallback(async () => {
    if (!user?.id || !userKey || !token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const decryptedConfig = await fetchAndDecryptUIConfig(token, user.id, userKey);
      setConfig(decryptedConfig);
      setHasUpdate(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load interface configuration';
      setError(errorMessage);
      console.error('Failed to fetch UIConfig:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id, userKey, token]);

  // Initial fetch
  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Setup polling for updates
  useEffect(() => {
    if (!autoPoll || !user?.id || !config || !token) {
      return;
    }

    const stopPolling = setupUIConfigPolling(
      token,
      user.id,
      config.version,
      async () => {
        // Update detected, check if user wants to refresh
        setHasUpdate(true);
      },
      pollInterval
    );

    return () => {
      stopPolling();
    };
  }, [autoPoll, user?.id, config?.version, token, pollInterval]);

  const refetch = useCallback(async () => {
    if (user?.id) {
      clearUIConfigCache(user.id);
    }
    await fetchConfig();
  }, [fetchConfig, user?.id]);

  return {
    config,
    loading,
    error,
    refetch,
    hasUpdate,
  };
}

