/**
 * UI Configuration Service
 * 
 * Fetches encrypted UI configurations from the backend and decrypts them
 * for personalized interface rendering.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface UIConfig {
  theme: string;
  layout: string;
  components: Array<{
    type: string;
    visible: boolean;
    prominence: string;
    props: any;
  }>;
  metadata?: {
    risk_level: string;
    trajectory: string;
    changes_count: number;
  };
}

export interface UIConfigResponse {
  status: string;
  config_id?: string;
  version?: string;
  generated_at?: string;
  encrypted_config?: string;
  theme?: string;
  primary_components?: string[];
  hidden_components?: string[];
  default_config?: UIConfig;
  message?: string;
}

/**
 * Fetch UI configuration from backend
 */
export async function fetchUIConfig(token: string): Promise<UIConfigResponse> {
  try {
    const response = await axios.get<UIConfigResponse>(`${API_BASE_URL}/api/ui-config`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
  } catch (error: any) {
    console.error('Failed to fetch UI config:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch UI configuration');
  }
}

/**
 * Decrypt UI configuration
 * 
 * Note: In a real implementation, this would use the Web Crypto API
 * to decrypt the configuration using a user-derived key.
 * 
 * For now, we're returning a mock decrypted config since the encryption
 * key management needs to be set up properly.
 */
export async function decryptUIConfig(encryptedConfig: string, userKey: string): Promise<UIConfig> {
  try {
    // TODO: Implement actual decryption using Web Crypto API
    // For now, return a default config as the encryption is handled server-side
    console.warn('Decryption not fully implemented - using default config');
    
    return {
      theme: 'calm',
      layout: 'standard',
      components: [
        {
          type: 'EmotionalCheckIn',
          visible: true,
          prominence: 'high',
          props: {
            frequency: 'daily',
            prompts: ['How are you feeling today?', 'What\'s on your mind?']
          }
        },
        {
          type: 'CopingStrategies',
          visible: true,
          prominence: 'medium',
          props: {
            suggested_strategies: ['Deep breathing', 'Journaling', 'Talk to someone']
          }
        },
        {
          type: 'CrisisResources',
          visible: true,
          prominence: 'low',
          props: {
            risk_level: 'low',
            resources: [
              {
                name: 'Crisis Helpline',
                contact: '0800-XXX-XXX',
                available: '24/7'
              }
            ]
          }
        }
      ]
    };
  } catch (error) {
    console.error('Failed to decrypt UI config:', error);
    throw new Error('Failed to decrypt UI configuration');
  }
}

/**
 * Get UI configuration with decryption
 */
export async function getUIConfig(token: string, userKey?: string): Promise<UIConfig> {
  const configResponse = await fetchUIConfig(token);
  
  // If no config generated yet, return default
  if (configResponse.status === 'no_config' && configResponse.default_config) {
    return configResponse.default_config;
  }
  
  // If encrypted config exists, decrypt it
  if (configResponse.encrypted_config && userKey) {
    return await decryptUIConfig(configResponse.encrypted_config, userKey);
  }
  
  // Fallback to a basic config
  return {
    theme: configResponse.theme || 'calm',
    layout: 'standard',
    components: []
  };
}
