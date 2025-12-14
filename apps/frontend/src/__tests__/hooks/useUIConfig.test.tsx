/**
 * Tests for useUIConfig hook
 * 
 * Tests the React hook that manages UIConfig state and polling
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { useUIConfig } from '../../hooks/useUIConfig';
import { AuthProvider } from '../../contexts/AuthContext';
import { BrowserRouter } from 'react-router-dom';
import * as uiconfigUtils from '../../utils/uiconfig';

// Mock UIConfig utilities
jest.mock('../../utils/uiconfig', () => ({
  fetchAndDecryptUIConfig: jest.fn(),
  checkUIConfigUpdate: jest.fn(),
  setupUIConfigPolling: jest.fn(),
  clearUIConfigCache: jest.fn(),
}));

// Mock AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../contexts/AuthContext'),
  useAuth: jest.fn(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Test component that uses useUIConfig hook
const TestComponent = ({ userKey, autoPoll = true, pollInterval }: {
  userKey: string | null;
  autoPoll?: boolean;
  pollInterval?: number;
}) => {
  const { config, loading, error, refetch, hasUpdate } = useUIConfig(userKey, autoPoll, pollInterval);

  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'not-loading'}</div>
      <div data-testid="error">{error || 'no-error'}</div>
      <div data-testid="config">{config ? JSON.stringify(config) : 'no-config'}</div>
      <div data-testid="has-update">{hasUpdate ? 'true' : 'false'}</div>
      <button onClick={refetch} data-testid="refetch-button">
        Refetch
      </button>
    </div>
  );
};

describe('useUIConfig Hook', () => {
  const mockUser = {
    id: 'test-user-id',
    email: 'test@example.com',
    isAnonymous: false,
    consentVersion: '1.0',
    createdAt: new Date().toISOString(),
    lastActive: new Date().toISOString(),
  };
  const mockToken = 'test-token';
  const mockUserKey = 'test-user-key';
  const mockUIConfig = {
    version: '1.0.0',
    theme: 'neutral',
    components: [],
    layout: {},
  };

  // Mock useAuth
  const mockUseAuth = require('../../contexts/AuthContext').useAuth;

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: mockUser,
      token: mockToken,
    });
    (uiconfigUtils.fetchAndDecryptUIConfig as jest.Mock).mockResolvedValue(mockUIConfig);
    (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockReturnValue(() => {});
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          {component}
        </AuthProvider>
      </BrowserRouter>
    );
  };

  describe('Initial State', () => {
    it('should show loading state initially', () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      expect(screen.getByTestId('loading')).toHaveTextContent('loading');
    });

    it('should fetch config on mount', async () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(uiconfigUtils.fetchAndDecryptUIConfig).toHaveBeenCalledWith(
          mockToken,
          mockUser.id,
          mockUserKey
        );
      });
    });

    it('should not fetch if user is not authenticated', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        token: null,
      });

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      expect(uiconfigUtils.fetchAndDecryptUIConfig).not.toHaveBeenCalled();
    });

    it('should not fetch if userKey is null', () => {
      renderWithProviders(<TestComponent userKey={null} />);

      expect(uiconfigUtils.fetchAndDecryptUIConfig).not.toHaveBeenCalled();
    });
  });

  describe('Config Loading', () => {
    it('should display config after successful fetch', async () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      expect(screen.getByTestId('config')).toHaveTextContent(JSON.stringify(mockUIConfig));
    });

    it('should display error on fetch failure', async () => {
      const errorMessage = 'Failed to load interface configuration';
      (uiconfigUtils.fetchAndDecryptUIConfig as jest.Mock).mockRejectedValue(
        new Error(errorMessage)
      );

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(errorMessage);
      });
    });

    it('should handle generic errors', async () => {
      (uiconfigUtils.fetchAndDecryptUIConfig as jest.Mock).mockRejectedValue('Generic error');

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent(
          'Failed to load interface configuration'
        );
      });
    });
  });

  describe('Polling', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should setup polling when autoPoll is true', async () => {
      const stopPolling = jest.fn();
      (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockReturnValue(stopPolling);

      renderWithProviders(<TestComponent userKey={mockUserKey} autoPoll={true} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      expect(uiconfigUtils.setupUIConfigPolling).toHaveBeenCalledWith(
        mockToken,
        mockUser.id,
        mockUIConfig.version,
        expect.any(Function),
        5 * 60 * 1000 // Default 5 minutes
      );
    });

    it('should not setup polling when autoPoll is false', async () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} autoPoll={false} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      expect(uiconfigUtils.setupUIConfigPolling).not.toHaveBeenCalled();
    });

    it('should use custom poll interval', async () => {
      const customInterval = 60000; // 1 minute
      const stopPolling = jest.fn();
      (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockReturnValue(stopPolling);

      renderWithProviders(
        <TestComponent userKey={mockUserKey} autoPoll={true} pollInterval={customInterval} />
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      expect(uiconfigUtils.setupUIConfigPolling).toHaveBeenCalledWith(
        mockToken,
        mockUser.id,
        mockUIConfig.version,
        expect.any(Function),
        customInterval
      );
    });

    it('should stop polling on unmount', async () => {
      const stopPolling = jest.fn();
      (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockReturnValue(stopPolling);

      const { unmount } = renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      unmount();

      expect(stopPolling).toHaveBeenCalled();
    });

    it('should set hasUpdate when polling detects update', async () => {
      let updateCallback: () => void;
      (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockImplementation(
        (token, userId, version, onUpdate) => {
          updateCallback = onUpdate;
          return () => {};
        }
      );

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      expect(screen.getByTestId('has-update')).toHaveTextContent('false');

      // Simulate update detection
      act(() => {
        updateCallback!();
      });

      expect(screen.getByTestId('has-update')).toHaveTextContent('true');
    });

    it('should not setup polling if config is not loaded', () => {
      (uiconfigUtils.fetchAndDecryptUIConfig as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      expect(uiconfigUtils.setupUIConfigPolling).not.toHaveBeenCalled();
    });
  });

  describe('Refetch', () => {
    it('should refetch config when refetch is called', async () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      const initialCallCount = (uiconfigUtils.fetchAndDecryptUIConfig as jest.Mock).mock.calls
        .length;

      const refetchButton = screen.getByTestId('refetch-button');
      await act(async () => {
        refetchButton.click();
      });

      await waitFor(() => {
        expect(uiconfigUtils.fetchAndDecryptUIConfig).toHaveBeenCalledTimes(initialCallCount + 1);
      });
    });

    it('should clear cache before refetching', async () => {
      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      const refetchButton = screen.getByTestId('refetch-button');
      await act(async () => {
        refetchButton.click();
      });

      expect(uiconfigUtils.clearUIConfigCache).toHaveBeenCalledWith(mockUser.id);
    });

    it('should reset hasUpdate after successful refetch', async () => {
      let updateCallback: () => void;
      (uiconfigUtils.setupUIConfigPolling as jest.Mock).mockImplementation(
        (token, userId, version, onUpdate) => {
          updateCallback = onUpdate;
          return () => {};
        }
      );

      renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      // Trigger update
      act(() => {
        updateCallback!();
      });

      expect(screen.getByTestId('has-update')).toHaveTextContent('true');

      // Refetch should reset hasUpdate
      const refetchButton = screen.getByTestId('refetch-button');
      await act(async () => {
        refetchButton.click();
      });

      await waitFor(() => {
        expect(screen.getByTestId('has-update')).toHaveTextContent('false');
      });
    });
  });

  describe('Dependencies', () => {
    it('should refetch when user changes', async () => {
      const { rerender } = renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      const newUser = { ...mockUser, id: 'new-user-id' };
      mockUseAuth.mockReturnValue({
        user: newUser,
        token: mockToken,
      });

      rerender(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent userKey={mockUserKey} />
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(uiconfigUtils.fetchAndDecryptUIConfig).toHaveBeenCalledWith(
          mockToken,
          newUser.id,
          mockUserKey
        );
      });
    });

    it('should refetch when userKey changes', async () => {
      const { rerender } = renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      const newUserKey = 'new-user-key';
      rerender(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent userKey={newUserKey} />
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(uiconfigUtils.fetchAndDecryptUIConfig).toHaveBeenCalledWith(
          mockToken,
          mockUser.id,
          newUserKey
        );
      });
    });

    it('should refetch when token changes', async () => {
      const { rerender } = renderWithProviders(<TestComponent userKey={mockUserKey} />);

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });

      const newToken = 'new-token';
      mockUseAuth.mockReturnValue({
        user: mockUser,
        token: newToken,
      });

      rerender(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent userKey={mockUserKey} />
          </AuthProvider>
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(uiconfigUtils.fetchAndDecryptUIConfig).toHaveBeenCalledWith(
          newToken,
          mockUser.id,
          mockUserKey
        );
      });
    });
  });
});

