# Frontend Tests

This directory contains all frontend tests for the ResonaAI web application.

## Test Structure

```
__tests__/
├── setupTests.ts              # Jest setup and configuration
├── components/                # Component tests
│   ├── VoiceRecorder.test.tsx
│   ├── ProtectedRoute.test.tsx
│   ├── LoadingSpinner.test.tsx
│   └── ErrorBoundary.test.tsx
├── contexts/                  # Context provider tests
│   ├── AuthContext.test.tsx
│   ├── EmotionContext.test.tsx
│   ├── OfflineContext.test.tsx
│   └── ThemeContext.test.tsx
└── pages/                     # Page component tests
    ├── LoginPage.test.tsx
    ├── HomePage.test.tsx
    └── ChatPage.test.tsx
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- VoiceRecorder.test.tsx
```

## Test Coverage

### Components Tested
- ✅ VoiceRecorder - Voice recording functionality
- ✅ ProtectedRoute - Authentication route protection
- ✅ LoadingSpinner - Loading state indicator
- ✅ ErrorBoundary - Error handling boundary

### Contexts Tested
- ✅ AuthContext - Authentication state management
- ✅ EmotionContext - Emotion state tracking
- ✅ OfflineContext - Online/offline status
- ✅ ThemeContext - Theme management

### Pages Tested
- ✅ LoginPage - User login functionality
- ✅ HomePage - Home page rendering
- ✅ ChatPage - Chat interface

## Test Utilities

Tests use:
- **@testing-library/react** - React component testing
- **@testing-library/user-event** - User interaction simulation
- **@testing-library/jest-dom** - Custom Jest matchers
- **jest** - Test runner (via react-scripts)

## Mocking

Tests mock:
- `localStorage` - For state persistence
- `fetch` - For API calls
- `navigator.onLine` - For offline detection
- External libraries (react-audio-voice-recorder, etc.)

## Notes

- All tests follow React Testing Library best practices
- Tests focus on user behavior and component output
- Mocks are used to isolate components from external dependencies
- Tests are designed to be maintainable and readable

