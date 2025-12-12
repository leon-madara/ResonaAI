import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../../pages/HomePage';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

describe('HomePage', () => {
  const renderHomePage = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <HomePage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('renders welcome message', () => {
    renderHomePage();
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it('displays user email when authenticated', () => {
    const mockUser = {
      id: 'test-id',
      email: 'user@example.com',
      isAnonymous: false,
      consentVersion: '1.0',
      createdAt: new Date().toISOString(),
      lastActive: new Date().toISOString(),
    };

    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'token') return 'mock-token';
      if (key === 'user') return JSON.stringify(mockUser);
      return null;
    });

    renderHomePage();
    expect(screen.getByText(/user@example.com/i)).toBeInTheDocument();
  });

  it('renders feature cards', () => {
    renderHomePage();
    expect(screen.getByText(/empathetic ai/i)).toBeInTheDocument();
    expect(screen.getByText(/privacy first/i)).toBeInTheDocument();
    expect(screen.getByText(/track progress/i)).toBeInTheDocument();
  });

  it('renders quick action links', () => {
    renderHomePage();
    expect(screen.getByText(/new conversation/i)).toBeInTheDocument();
    expect(screen.getByText(/view profile/i)).toBeInTheDocument();
    expect(screen.getByText(/settings/i)).toBeInTheDocument();
  });
});

