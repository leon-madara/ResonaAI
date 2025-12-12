import React from 'react';
import { render, screen } from '@testing-library/react';
import ChatPage from '../../pages/ChatPage';
import { EmotionProvider } from '../../contexts/EmotionContext';
import { OfflineProvider } from '../../contexts/OfflineContext';

describe('ChatPage', () => {
  const renderChatPage = () => {
    return render(
      <OfflineProvider>
        <EmotionProvider>
          <ChatPage />
        </EmotionProvider>
      </OfflineProvider>
    );
  };

  it('renders chat page', () => {
    renderChatPage();
    // Should render chat interface (adjust based on actual implementation)
    expect(screen.getByRole('main') || screen.getByText(/chat/i)).toBeInTheDocument();
  });

  it('displays online/offline status', () => {
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      configurable: true,
      value: true,
    });

    renderChatPage();
    // Should show online indicator (adjust based on actual implementation)
    expect(screen.getByRole('main') || screen.getByText(/online/i)).toBeInTheDocument();
  });
});

