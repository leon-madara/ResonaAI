import React from 'react';
import { render, screen } from '@testing-library/react';
import { OfflineProvider, useOffline } from '../../contexts/OfflineContext';

// Test component
const TestComponent = () => {
  const { isOnline } = useOffline();

  return <div data-testid="online-status">{isOnline ? 'online' : 'offline'}</div>;
};

describe('OfflineContext', () => {
  it('provides online status', () => {
    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: true,
    });

    render(
      <OfflineProvider>
        <TestComponent />
      </OfflineProvider>
    );

    expect(screen.getByTestId('online-status')).toHaveTextContent('online');
  });

  it('detects offline status', () => {
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: false,
    });

    render(
      <OfflineProvider>
        <TestComponent />
      </OfflineProvider>
    );

    expect(screen.getByTestId('online-status')).toHaveTextContent('offline');
  });
});

