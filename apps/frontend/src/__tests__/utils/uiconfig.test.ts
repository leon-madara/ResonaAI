/**
 * Tests for UIConfig utility functions
 * 
 * Tests the integration with the overnight builder API endpoints:
 * - /users/{userId}/interface/current
 * - /users/{userId}/interface/version
 */

import {
  fetchEncryptedUIConfig,
  decryptUIConfig,
  fetchAndDecryptUIConfig,
  checkUIConfigUpdate,
  clearUIConfigCache,
  setupUIConfigPolling,
  EncryptedUIConfigResponse,
} from '../../utils/uiconfig';
import { getApiBaseUrl, getAuthHeader } from '../../utils/api';

// Mock dependencies
jest.mock('../../utils/api', () => ({
  getApiBaseUrl: jest.fn(() => 'http://localhost:8000'),
  getAuthHeader: jest.fn((token) => (token ? { Authorization: `Bearer ${token}` } : {})),
  readJsonOrText: jest.fn(async (response) => {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) return await response.json();
    return await response.text();
  }),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock fetch
global.fetch = jest.fn();

// Mock Web Crypto API for decryption tests
const mockCrypto = {
  subtle: {
    digest: jest.fn(),
    importKey: jest.fn(),
    deriveKey: jest.fn(),
    decrypt: jest.fn(),
  },
};
global.crypto = mockCrypto as any;

describe('UIConfig Utilities', () => {
  const mockUserId = 'test-user-id';
  const mockToken = 'test-token';
  const mockUserKey = 'test-user-key';
  const mockApiBaseUrl = 'http://localhost:8000';

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    (getApiBaseUrl as jest.Mock).mockReturnValue(mockApiBaseUrl);
  });

  describe('fetchEncryptedUIConfig', () => {
    const mockEncryptedResponse: EncryptedUIConfigResponse = {
      encrypted_config: 'base64-encrypted-data',
      salt: '',
      version: '1.0.0',
      generated_at: '2025-01-15T10:00:00Z',
      user_id: mockUserId,
    };

    it('should fetch encrypted config from API', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockEncryptedResponse,
      });

      const result = await fetchEncryptedUIConfig(mockToken, mockUserId);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/users/${mockUserId}/interface/current`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${mockToken}`,
          },
        }
      );
      expect(result).toEqual(mockEncryptedResponse);
    });

    it('should use cached config if available and not expired', async () => {
      const cacheKey = `uiconfig_${mockUserId}`;
      const cacheTimestampKey = `uiconfig_${mockUserId}_timestamp`;
      const cachedTimestamp = Date.now() - 2 * 60 * 1000; // 2 minutes ago

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === cacheKey) return JSON.stringify(mockEncryptedResponse);
        if (key === cacheTimestampKey) return cachedTimestamp.toString();
        return null;
      });

      const result = await fetchEncryptedUIConfig(mockToken, mockUserId);

      expect(global.fetch).not.toHaveBeenCalled();
      expect(result).toEqual(mockEncryptedResponse);
    });

    it('should fetch from API if cache is expired', async () => {
      const cacheKey = `uiconfig_${mockUserId}`;
      const cacheTimestampKey = `uiconfig_${mockUserId}_timestamp`;
      const expiredTimestamp = Date.now() - 6 * 60 * 1000; // 6 minutes ago

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === cacheKey) return JSON.stringify(mockEncryptedResponse);
        if (key === cacheTimestampKey) return expiredTimestamp.toString();
        return null;
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockEncryptedResponse,
      });

      const result = await fetchEncryptedUIConfig(mockToken, mockUserId);

      expect(global.fetch).toHaveBeenCalled();
      expect(result).toEqual(mockEncryptedResponse);
    });

    it('should cache the response after fetching', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockEncryptedResponse,
      });

      await fetchEncryptedUIConfig(mockToken, mockUserId);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        `uiconfig_${mockUserId}`,
        JSON.stringify(mockEncryptedResponse)
      );
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        `uiconfig_${mockUserId}_timestamp`,
        expect.any(String)
      );
    });

    it('should throw error on 404 response', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
      });

      await expect(fetchEncryptedUIConfig(mockToken, mockUserId)).rejects.toThrow(
        'No interface configuration found'
      );
    });

    it('should throw error on other failed responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      });

      await expect(fetchEncryptedUIConfig(mockToken, mockUserId)).rejects.toThrow(
        'Internal server error'
      );
    });

    it('should handle corrupted cache gracefully', async () => {
      const cacheKey = `uiconfig_${mockUserId}`;
      const cacheTimestampKey = `uiconfig_${mockUserId}_timestamp`;
      const cachedTimestamp = Date.now() - 2 * 60 * 1000;

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === cacheKey) return 'invalid-json';
        if (key === cacheTimestampKey) return cachedTimestamp.toString();
        return null;
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockEncryptedResponse,
      });

      const result = await fetchEncryptedUIConfig(mockToken, mockUserId);

      expect(global.fetch).toHaveBeenCalled();
      expect(result).toEqual(mockEncryptedResponse);
    });
  });

  describe('decryptUIConfig', () => {
    // Note: Full decryption testing requires complex Web Crypto API mocking
    // This test verifies the function structure and error handling

    it('should handle decryption with provided salt', async () => {
      const mockEncryptedResponse: EncryptedUIConfigResponse = {
        encrypted_config: 'base64-encrypted-data',
        salt: 'base64-salt',
        version: '1.0.0',
        generated_at: '2025-01-15T10:00:00Z',
        user_id: mockUserId,
      };

      // Mock Web Crypto API
      const mockDecryptedData = new TextEncoder().encode(JSON.stringify({ version: '1.0.0' }));
      mockCrypto.subtle.digest.mockResolvedValue(new ArrayBuffer(32));
      mockCrypto.subtle.importKey.mockResolvedValue({} as CryptoKey);
      mockCrypto.subtle.deriveKey.mockResolvedValue({} as CryptoKey);
      mockCrypto.subtle.decrypt.mockResolvedValue(mockDecryptedData);

      // Mock base64 decoding
      global.atob = jest.fn(() => 'decoded-string');
      global.TextDecoder = jest.fn().mockImplementation(() => ({
        decode: jest.fn(() => JSON.stringify({ version: '1.0.0', theme: 'neutral' })),
      })) as any;

      const result = await decryptUIConfig(mockEncryptedResponse, mockUserKey);

      expect(result).toHaveProperty('version', '1.0.0');
    });

    it('should derive salt from userKey if not provided', async () => {
      const mockEncryptedResponse: EncryptedUIConfigResponse = {
        encrypted_config: 'base64-encrypted-data',
        salt: '',
        version: '1.0.0',
        generated_at: '2025-01-15T10:00:00Z',
        user_id: mockUserId,
      };

      const mockHashBuffer = new ArrayBuffer(32);
      mockCrypto.subtle.digest.mockResolvedValue(mockHashBuffer);
      mockCrypto.subtle.importKey.mockResolvedValue({} as CryptoKey);
      mockCrypto.subtle.deriveKey.mockResolvedValue({} as CryptoKey);

      const mockDecryptedData = new TextEncoder().encode(JSON.stringify({ version: '1.0.0' }));
      mockCrypto.subtle.decrypt.mockResolvedValue(mockDecryptedData);

      global.atob = jest.fn(() => 'decoded-string');
      global.TextDecoder = jest.fn().mockImplementation(() => ({
        decode: jest.fn(() => JSON.stringify({ version: '1.0.0' })),
      })) as any;

      await decryptUIConfig(mockEncryptedResponse, mockUserKey);

      expect(mockCrypto.subtle.digest).toHaveBeenCalledWith(
        'SHA-256',
        expect.any(Uint8Array)
      );
    });

    it('should throw error on decryption failure', async () => {
      const mockEncryptedResponse: EncryptedUIConfigResponse = {
        encrypted_config: 'invalid-encrypted-data',
        salt: '',
        version: '1.0.0',
        generated_at: '2025-01-15T10:00:00Z',
        user_id: mockUserId,
      };

      mockCrypto.subtle.decrypt.mockRejectedValue(new Error('Decryption failed'));

      await expect(decryptUIConfig(mockEncryptedResponse, mockUserKey)).rejects.toThrow(
        'Failed to decrypt interface configuration'
      );
    });
  });

  describe('fetchAndDecryptUIConfig', () => {
    it('should fetch and decrypt config', async () => {
      const mockEncryptedResponse: EncryptedUIConfigResponse = {
        encrypted_config: 'base64-encrypted-data',
        salt: '',
        version: '1.0.0',
        generated_at: '2025-01-15T10:00:00Z',
        user_id: mockUserId,
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockEncryptedResponse,
      });

      // Mock decryption
      const mockDecryptedData = new TextEncoder().encode(JSON.stringify({ version: '1.0.0' }));
      mockCrypto.subtle.digest.mockResolvedValue(new ArrayBuffer(32));
      mockCrypto.subtle.importKey.mockResolvedValue({} as CryptoKey);
      mockCrypto.subtle.deriveKey.mockResolvedValue({} as CryptoKey);
      mockCrypto.subtle.decrypt.mockResolvedValue(mockDecryptedData);

      global.atob = jest.fn(() => 'decoded-string');
      global.TextDecoder = jest.fn().mockImplementation(() => ({
        decode: jest.fn(() => JSON.stringify({ version: '1.0.0' })),
      })) as any;

      const result = await fetchAndDecryptUIConfig(mockToken, mockUserId, mockUserKey);

      expect(global.fetch).toHaveBeenCalled();
      expect(result).toHaveProperty('version', '1.0.0');
    });
  });

  describe('checkUIConfigUpdate', () => {
    it('should return true when version differs', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.1' }),
      });

      const result = await checkUIConfigUpdate(mockToken, mockUserId, '1.0.0');

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiBaseUrl}/users/${mockUserId}/interface/version`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${mockToken}`,
          },
        }
      );
      expect(result).toBe(true);
    });

    it('should return false when version matches', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.0' }),
      });

      const result = await checkUIConfigUpdate(mockToken, mockUserId, '1.0.0');

      expect(result).toBe(false);
    });

    it('should return false on API error', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
      });

      const result = await checkUIConfigUpdate(mockToken, mockUserId, '1.0.0');

      expect(result).toBe(false);
    });

    it('should return false on network error', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      const result = await checkUIConfigUpdate(mockToken, mockUserId, '1.0.0');

      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('clearUIConfigCache', () => {
    it('should clear cache for user', () => {
      clearUIConfigCache(mockUserId);

      expect(localStorageMock.removeItem).toHaveBeenCalledWith(`uiconfig_${mockUserId}`);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(
        `uiconfig_${mockUserId}_timestamp`
      );
    });
  });

  describe('setupUIConfigPolling', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should poll for updates at specified interval', async () => {
      const onUpdate = jest.fn();
      const pollInterval = 1000; // 1 second for testing

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.0' }),
      });

      const stopPolling = setupUIConfigPolling(
        mockToken,
        mockUserId,
        '1.0.0',
        onUpdate,
        pollInterval
      );

      // Fast-forward time to trigger polling
      jest.advanceTimersByTime(pollInterval);

      // Wait for async operations
      await Promise.resolve();

      expect(global.fetch).toHaveBeenCalled();

      stopPolling();
    });

    it('should call onUpdate when update is detected', async () => {
      const onUpdate = jest.fn();
      const pollInterval = 1000;

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.1' }), // Different version
      });

      const stopPolling = setupUIConfigPolling(
        mockToken,
        mockUserId,
        '1.0.0',
        onUpdate,
        pollInterval
      );

      jest.advanceTimersByTime(pollInterval);
      await Promise.resolve();

      expect(onUpdate).toHaveBeenCalled();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(`uiconfig_${mockUserId}`);

      stopPolling();
    });

    it('should not call onUpdate when version matches', async () => {
      const onUpdate = jest.fn();
      const pollInterval = 1000;

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.0' }), // Same version
      });

      const stopPolling = setupUIConfigPolling(
        mockToken,
        mockUserId,
        '1.0.0',
        onUpdate,
        pollInterval
      );

      jest.advanceTimersByTime(pollInterval);
      await Promise.resolve();

      expect(onUpdate).not.toHaveBeenCalled();

      stopPolling();
    });

    it('should handle errors gracefully during polling', async () => {
      const onUpdate = jest.fn();
      const pollInterval = 1000;
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const stopPolling = setupUIConfigPolling(
        mockToken,
        mockUserId,
        '1.0.0',
        onUpdate,
        pollInterval
      );

      jest.advanceTimersByTime(pollInterval);
      await Promise.resolve();

      expect(consoleErrorSpy).toHaveBeenCalled();
      expect(onUpdate).not.toHaveBeenCalled();

      stopPolling();
      consoleErrorSpy.mockRestore();
    });

    it('should stop polling when stop function is called', () => {
      const onUpdate = jest.fn();
      const pollInterval = 1000;

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ version: '1.0.0' }),
      });

      const stopPolling = setupUIConfigPolling(
        mockToken,
        mockUserId,
        '1.0.0',
        onUpdate,
        pollInterval
      );

      const initialCallCount = (global.fetch as jest.Mock).mock.calls.length;

      stopPolling();

      jest.advanceTimersByTime(pollInterval * 2);
      await Promise.resolve();

      // Fetch should not be called again after stopping
      expect((global.fetch as jest.Mock).mock.calls.length).toBe(initialCallCount);
    });
  });
});

