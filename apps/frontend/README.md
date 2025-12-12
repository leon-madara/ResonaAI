# Frontend Application

React-based web application for ResonaAI.

## 📁 Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Auth/             # Authentication components
│   │   │   └── ProtectedRoute.tsx
│   │   ├── ConversationUI/   # Chat interface
│   │   │   ├── ConversationUI.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── Layout/           # Layout components
│   │   │   └── Layout.tsx
│   │   ├── UI/               # Base components
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   └── VoiceRecorder/    # Voice recording
│   │       └── VoiceRecorder.tsx
│   ├── contexts/             # React contexts
│   │   ├── AuthContext.tsx
│   │   ├── EmotionContext.tsx
│   │   ├── OfflineContext.tsx
│   │   └── ThemeContext.tsx
│   ├── pages/                # Page components (9 pages)
│   │   ├── HomePage.tsx
│   │   ├── ChatPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── SettingsPage.tsx
│   │   ├── ConsentPage.tsx
│   │   ├── CrisisPage.tsx
│   │   └── OfflinePage.tsx
│   ├── utils/                # Utility functions
│   │   ├── api.ts            # API client
│   │   ├── encryption.ts     # Client-side encryption
│   │   └── secureStorage.ts  # Secure local storage
│   ├── __tests__/            # Test files
│   │   ├── components/
│   │   ├── contexts/
│   │   └── pages/
│   ├── App.tsx
│   └── index.tsx
└── package.json
```

## 🔄 Migration Notes

This directory contains code migrated from `web-app/`.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
npm install
```

### Run Development Server
```bash
npm start
# Opens http://localhost:3000
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test
```

## 🎨 Component Architecture

### Contexts
| Context | Purpose |
|---------|---------|
| `AuthContext` | User authentication state |
| `EmotionContext` | Emotion detection state |
| `OfflineContext` | Offline mode handling |
| `ThemeContext` | Theme preferences |

### Pages
| Page | Route | Description |
|------|-------|-------------|
| HomePage | `/` | Landing page |
| LoginPage | `/login` | User login |
| RegisterPage | `/register` | User registration |
| ChatPage | `/chat` | Main conversation |
| ProfilePage | `/profile` | User profile |
| SettingsPage | `/settings` | App settings |
| ConsentPage | `/consent` | Data consent |
| CrisisPage | `/crisis` | Crisis resources |
| OfflinePage | `/offline` | Offline mode |

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ChatPage.test.tsx
```

## 📱 Responsive Design

The app is designed mobile-first with breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🔒 Security Features

- JWT token management
- Client-side encryption for sensitive data
- Secure storage using encrypted localStorage
- CSRF protection
- XSS prevention
