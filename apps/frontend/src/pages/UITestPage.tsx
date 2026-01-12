/**
 * UI Test Page
 * 
 * Test page to demonstrate personalized UI configuration loading
 */

import React, { useEffect, useState } from 'react';
import { getUIConfig } from '../services/uiConfigService';
import './UITestPage.css';

const UITestPage: React.FC = () => {
  const [uiConfig, setUiConfig] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string>('');

  const loadUIConfig = async () => {
    if (!token || token.trim() === '') {
      setError('Please enter an authentication token');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setUiConfig(null); // Clear previous config
      
      const config = await getUIConfig(token);
      setUiConfig(config);
    } catch (err: any) {
      setError(err.message || 'Failed to load UI configuration');
      setUiConfig(null);
    } finally {
      setLoading(false);
    }
  };

  // Auto-load when token is pasted (if it looks like a JWT)
  useEffect(() => {
    if (token && token.includes('.') && token.split('.').length === 3 && !loading && !uiConfig) {
      // Token looks valid, but don't auto-load - let user click button
    }
  }, [token]);

  return (
    <div className="ui-test-page">
      <header className="test-header">
        <h1>🎨 Personalized UI Configuration Test</h1>
        <p>Enter your authentication token to load your personalized interface</p>
      </header>

      <div className="test-controls">
        <div className="token-input-group">
          <label htmlFor="token">Authentication Token:</label>
          <input
            id="token"
            type="text"
            placeholder="Enter your JWT token..."
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="token-input"
          />
          <button 
            onClick={loadUIConfig}
            disabled={loading || !token || token.trim() === ''}
            className="load-button"
          >
            {loading ? 'Loading...' : 'Load UI Config'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && !uiConfig && (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your personalized UI configuration...</p>
        </div>
      )}

      {uiConfig && !loading && (
        <div className="config-display">
          <h2>✅ UI Configuration Loaded</h2>
          
          <div className="config-section">
            <h3>Theme</h3>
            <div className="theme-preview" style={{ backgroundColor: getThemeColor(uiConfig.theme) }}>
              {uiConfig.theme}
            </div>
          </div>

          <div className="config-section">
            <h3>Layout</h3>
            <p className="layout-name">{uiConfig.layout}</p>
          </div>

          <div className="config-section">
            <h3>Components ({uiConfig.components?.length || 0})</h3>
            <div className="components-grid">
              {uiConfig.components?.map((component: any, index: number) => (
                <div key={index} className="component-card">
                  <div className="component-header">
                    <span className="component-type">{component.type}</span>
                    <span className={`component-visibility ${component.visible ? 'visible' : 'hidden'}`}>
                      {component.visible ? '👁️ Visible' : '👁️‍🗨️ Hidden'}
                    </span>
                  </div>
                  <div className="component-prominence">
                    Prominence: <strong>{component.prominence}</strong>
                  </div>
                  {component.props && (
                    <details className="component-props">
                      <summary>Props</summary>
                      <pre>{JSON.stringify(component.props, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="config-section">
            <h3>Full Configuration (JSON)</h3>
            <pre className="json-display">{JSON.stringify(uiConfig, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

function getThemeColor(theme: string): string {
  const themeColors: Record<string, string> = {
    calm: '#E8F5E9',
    warm: '#FFF3E0',
    cool: '#E3F2FD',
    neutral: '#F5F5F5',
    energizing: '#FFF9C4'
  };
  return themeColors[theme] || '#F5F5F5';
}

export default UITestPage;
