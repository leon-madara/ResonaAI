import React from 'react';
import { useOffline } from '../contexts/OfflineContext';
import { WifiOff, Wifi, RefreshCw, Download, CheckCircle } from 'lucide-react';
import './OfflinePage.css';

const OfflinePage: React.FC = () => {
  const { isOnline, syncStatus } = useOffline();

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="offline-page">
      <div className="offline-container">
        {isOnline ? (
          <div className="offline-status online">
            <Wifi className="w-16 h-16 text-green-600 dark:text-green-400 mb-4" />
            <h1 className="offline-title">You're Back Online!</h1>
            <p className="offline-message">
              Your connection has been restored. Syncing your data...
            </p>
            {syncStatus && (
              <div className="sync-status">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>{syncStatus}</span>
              </div>
            )}
          </div>
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

