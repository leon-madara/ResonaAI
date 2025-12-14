/**
 * UIConfig API Client
 * 
 * Handles fetching, caching, and decrypting UIConfig from the backend
 */

import { getApiBaseUrl, getAuthHeader, readJsonOrText } from './api';
import { decryptObject, EncryptedData } from './encryption';
import { UIConfig } from '../types';

/**
 * Encrypted UIConfig response from backend
 */
export interface EncryptedUIConfigResponse {
  encrypted_config: string; // Base64-encoded encrypted UIConfig
  salt: string; // Base64-encoded salt for key derivation
  version: string;
  generated_at: string;
  user_id: string;
}

/**
 * Fetch encrypted UIConfig for a user
 * @param token Authentication token
 * @param userId User ID
 * @returns Encrypted UIConfig response
 */
export async function fetchEncryptedUIConfig(
  token: string | null,
  userId: string
): Promise<EncryptedUIConfigResponse> {
  const apiBaseUrl = getApiBaseUrl();
  const cacheKey = `uiconfig_${userId}`;
  const cacheTimestampKey = `uiconfig_${userId}_timestamp`;
  
  // Check cache (5 minute TTL)
  const cached = localStorage.getItem(cacheKey);
  const cachedTimestamp = localStorage.getItem(cacheTimestampKey);
  if (cached && cachedTimestamp) {
    const age = Date.now() - parseInt(cachedTimestamp, 10);
    if (age < 5 * 60 * 1000) { // 5 minutes
      try {
        return JSON.parse(cached);
      } catch (e) {
        // Cache corrupted, continue to fetch
      }
    }
  }

  const response = await fetch(`${apiBaseUrl}/users/${userId}/interface/current`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('No interface configuration found');
    }
    const errorData = await readJsonOrText(response);
    throw new Error(errorData?.detail || errorData?.error || 'Failed to fetch interface configuration');
  }

  const data = await response.json();
  
  // Cache the response
  localStorage.setItem(cacheKey, JSON.stringify(data));
  localStorage.setItem(cacheTimestampKey, Date.now().toString());
  
  return data;
}

/**
 * Decrypt UIConfig on client side
 * The backend uses AES-256-GCM with the structure: [IV (16 bytes)][Tag (16 bytes)][Ciphertext]
 * The backend expects a 32-byte key, which may be derived from a passphrase using PBKDF2
 * @param encryptedResponse Encrypted UIConfig response
 * @param userKey User's encryption key (passphrase or 32-byte key as base64)
 * @returns Decrypted UIConfig
 */
export async function decryptUIConfig(
  encryptedResponse: EncryptedUIConfigResponse,
  userKey: string
): Promise<UIConfig> {
  try {
    // Backend format: base64 string containing [IV][Tag][Ciphertext]
    const encryptedBytes = base64ToArrayBuffer(encryptedResponse.encrypted_config);
    const bytes = new Uint8Array(encryptedBytes);
    
    // Extract IV (first 16 bytes), Tag (next 16 bytes), and Ciphertext (rest)
    const iv = bytes.slice(0, 16);
    const tag = bytes.slice(16, 32);
    const ciphertext = bytes.slice(32);
    
    // If salt is provided, use it; otherwise derive from userKey directly
    let saltArray: Uint8Array;
    if (encryptedResponse.salt && encryptedResponse.salt.length > 0) {
      const salt = base64ToArrayBuffer(encryptedResponse.salt);
      saltArray = new Uint8Array(salt);
    } else {
      // If no salt provided, use a default salt derived from userKey hash
      // This is a fallback - ideally salt should be provided
      const saltHash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(userKey));
      saltArray = new Uint8Array(saltHash).slice(0, 16); // Use first 16 bytes as salt
    }
    
    // Derive key from user key (passphrase) and salt using PBKDF2
    // This matches the backend's derive_key_from_passphrase method
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(userKey),
      'PBKDF2',
      false,
      ['deriveKey']
    );
    
    const derivedKey = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: saltArray,
        iterations: 100000, // Matches backend PBKDF2_ITERATIONS
        hash: 'SHA-256',
      },
      keyMaterial,
      {
        name: 'AES-GCM',
        length: 256,
      },
      false,
      ['decrypt']
    );
    
    // Decrypt using AES-GCM
    // Web Crypto API expects ciphertext and tag concatenated
    const decrypted = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv,
        tagLength: 128, // 16 bytes = 128 bits
      },
      derivedKey,
      new Uint8Array([...ciphertext, ...tag]) // Concatenate ciphertext + tag
    );
    
    // Parse JSON
    const jsonString = new TextDecoder().decode(decrypted);
    return JSON.parse(jsonString) as UIConfig;
  } catch (error) {
    console.error('Failed to decrypt UIConfig:', error);
    throw new Error('Failed to decrypt interface configuration. Please check your encryption key.');
  }
}

/**
 * Helper function to convert base64 to ArrayBuffer
 */
function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Fetch and decrypt UIConfig for a user
 * @param token Authentication token
 * @param userId User ID
 * @param userKey User's encryption key
 * @returns Decrypted UIConfig
 */
export async function fetchAndDecryptUIConfig(
  token: string | null,
  userId: string,
  userKey: string
): Promise<UIConfig> {
  const encrypted = await fetchEncryptedUIConfig(token, userId);
  return decryptUIConfig(encrypted, userKey);
}

/**
 * Check for UIConfig updates
 * @param token Authentication token
 * @param userId User ID
 * @param currentVersion Current UIConfig version
 * @returns True if update available
 */
export async function checkUIConfigUpdate(
  token: string | null,
  userId: string,
  currentVersion: string
): Promise<boolean> {
  const apiBaseUrl = getApiBaseUrl();
  
  try {
    const response = await fetch(`${apiBaseUrl}/users/${userId}/interface/version`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(token),
      },
    });

    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    return data.version !== currentVersion;
  } catch (error) {
    console.error('Failed to check UIConfig version:', error);
    return false;
  }
}

/**
 * Clear UIConfig cache for a user
 * @param userId User ID
 */
export function clearUIConfigCache(userId: string): void {
  localStorage.removeItem(`uiconfig_${userId}`);
  localStorage.removeItem(`uiconfig_${userId}_timestamp`);
}

/**
 * Setup polling for UIConfig updates
 * @param token Authentication token
 * @param userId User ID
 * @param currentVersion Current UIConfig version
 * @param onUpdate Callback when update is detected
 * @param intervalMs Polling interval in milliseconds (default: 5 minutes)
 * @returns Function to stop polling
 */
export function setupUIConfigPolling(
  token: string | null,
  userId: string,
  currentVersion: string,
  onUpdate: () => void,
  intervalMs: number = 5 * 60 * 1000
): () => void {
  const intervalId = setInterval(async () => {
    try {
      const hasUpdate = await checkUIConfigUpdate(token, userId, currentVersion);
      if (hasUpdate) {
        clearUIConfigCache(userId);
        onUpdate();
      }
    } catch (error) {
      console.error('Error checking for UIConfig updates:', error);
    }
  }, intervalMs);

  return () => clearInterval(intervalId);
}

