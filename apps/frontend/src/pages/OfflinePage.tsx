import React, { useState, useEffect } from 'react';
import { useOffline } from '../contexts/OfflineContext';
import { WifiOff, Wifi, RefreshCw, Download, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './OfflinePage.css';

const OfflinePage: React.FC = () => {
  const { isOnline, syncQueue, processSyncQueue } = useOffline();
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('lastSyncTime');
    if (stored) {
      setLastSyncTime(stored);
    }
  }, []);

  const handleRetry = () => {
    window.location.reload();
  };

  const handleManualSync = async () => {
    if (!isOnline) {
      toast.error('You are offline. Please connect to the internet to sync.');
      return;
    }

    setIsSyncing(true);
    try {
      await processSyncQueue();
      const now = new Date().toISOString();
      setLastSyncTime(now);
      localStorage.setItem('lastSyncTime', now);
      toast.success('Sync completed');
    } catch (error) {
      console.error('Sync error:', error);
      toast.error('Sync failed. Please try again.');
    } finally {
      setIsSyncing(false);
    }
  };

  const pendingItems = syncQueue.filter(item => item.retryCount < 3);
  const failedItems = syncQueue.filter(item => item.retryCount >= 3);
  const totalItems = syncQueue.length;

  return (
    <div className="offline-page">
      <div className="offline-container">
        {isOnline ? (
          <>
            <div className="offline-status online">
              <Wifi className="w-16 h-16 text-green-600 dark:text-green-400 mb-4" />
              <h1 className="offline-title">You're Back Online!</h1>
              <p className="offline-message">
                Your connection has been restored.
              </p>
            </div>

            {totalItems > 0 && (
              <div className="sync-status-section">
                <h2 className="sync-status-title">Sync Status</h2>
                <div className="sync-stats">
                  <div className="sync-stat">
                    <div className="stat-label">Pending</div>
                    <div className="stat-value pending">{pendingItems.length}</div>
                  </div>
                  <div className="sync-stat">
                    <div className="stat-label">Failed</div>
                    <div className="stat-value failed">{failedItems.length}</div>
                  </div>
                  <div className="sync-stat">
                    <div className="stat-label">Total</div>
                    <div className="stat-value">{totalItems}</div>
                  </div>
                </div>

                {pendingItems.length > 0 && (
                  <div className="sync-queue">
                    <h3 className="queue-title">Pending Items</h3>
                    <div className="queue-list">
                      {pendingItems.slice(0, 5).map((item) => (
                        <div key={item.id} className="queue-item">
                          <div className="queue-item-info">
                            <span className="queue-item-type">{item.type}</span>
                            <span className="queue-item-time">
                              {new Date(item.timestamp).toLocaleString()}
                            </span>
                          </div>
                          {item.retryCount > 0 && (
                            <span className="retry-count">Retry {item.retryCount}/3</span>
                          )}
                        </div>
                      ))}
                      {pendingItems.length > 5 && (
                        <p className="more-items">And {pendingItems.length - 5} more items...</p>
                      )}
                    </div>
                  </div>
                )}

                {failedItems.length > 0 && (
                  <div className="sync-queue failed-queue">
                    <h3 className="queue-title">Failed Items</h3>
                    <div className="queue-list">
                      {failedItems.map((item) => (
                        <div key={item.id} className="queue-item failed">
                          <div className="queue-item-info">
                            <span className="queue-item-type">{item.type}</span>
                            <span className="queue-item-time">
                              {new Date(item.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <XCircle className="w-4 h-4 text-red-600" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="sync-actions">
                  <button
                    onClick={handleManualSync}
                    disabled={isSyncing || totalItems === 0}
                    className="sync-button"
                  >
                    {isSyncing ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Syncing...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-5 h-5" />
                        Sync Now
                      </>
                    )}
                  </button>
                  {lastSyncTime && (
                    <p className="last-sync">
                      <Clock className="w-4 h-4" />
                      Last sync: {new Date(lastSyncTime).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
            )}

            {totalItems === 0 && (
              <div className="sync-complete">
                <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400 mb-2" />
                <p className="sync-complete-message">All data is synced!</p>
                {lastSyncTime && (
                  <p className="last-sync">
                    <Clock className="w-4 h-4" />
                    Last sync: {new Date(lastSyncTime).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </>
        ) : (
          <>
            <div className="offline-status offline">
              <WifiOff className="w-16 h-16 text-gray-400 mb-4" />
              <h1 className="offline-title">You're Offline</h1>
              <p className="offline-message">
                Don't worry! You can still use ResonaAI offline. Your conversations will be saved locally and synced when you're back online.
              </p>
            </div>

            <div className="offline-features">
              <h2 className="features-title">Available Offline</h2>
              <div className="features-list">
                <div className="feature-item">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <span>Voice recordings</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <span>Local conversation history</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <span>Basic emotion detection</span>
                </div>
                <div className="feature-item">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  <span>Crisis resources</span>
                </div>
              </div>
            </div>

            <div className="offline-actions">
              <button onClick={handleRetry} className="retry-button">
                <RefreshCw className="w-5 h-5" />
                Check Connection
              </button>
              <a href="/crisis" className="crisis-link">
                Need immediate help?
              </a>
            </div>

            <div className="offline-info">
              <Download className="w-5 h-5" />
              <div>
                <h3>Offline Mode</h3>
                <p>
                  ResonaAI works offline to ensure you always have access to support.
                  When you reconnect, all your data will automatically sync.
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default OfflinePage;

