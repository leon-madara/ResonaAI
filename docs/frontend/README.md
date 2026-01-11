# Frontend Documentation

**User interface and experience documentation for ResonaAI**

---

## 🎨 Frontend Overview

ResonaAI's frontend is a **React-based Progressive Web App (PWA)** that provides an adaptive, culturally-sensitive interface for voice-first mental health support. The UI evolves with each user's patterns, creating personalized experiences.

### Core Frontend Principles
- **Voice-First**: Primary interaction through voice recording
- **Adaptive Interface**: UI changes based on user patterns
- **Cultural Sensitivity**: East African context and Swahili support
- **Offline-First**: Works without internet connectivity
- **Privacy-Preserving**: Client-side encryption and minimal data exposure

---

## 📚 Frontend Documents

### [Frontend Architecture](architecture.md)
**React application structure and technical design**
- Component architecture and organization
- State management with React contexts
- Routing and navigation patterns
- PWA capabilities and offline support
- Integration with backend services

### [Design System](design-system.md)
**Comprehensive UI/UX specifications and guidelines**
- Adaptive theming system (Calm, Warm, Crisis, Balanced)
- Component library and design tokens
- Cultural adaptation patterns
- Voice and tone guidelines
- Accessibility standards (WCAG AA)

### [Component Library](components.md)
**Reusable UI components and patterns**
- Core components (VoiceRecorder, CulturalGreeting, etc.)
- Layout components (AdaptiveInterface, InterfaceRenderer)
- Utility components (ErrorBoundary, LoadingSpinner)
- Form components and validation
- Navigation and routing components

### [Testing Guide](testing.md)
**Frontend testing strategies and implementation**
- Component testing with React Testing Library
- Integration testing patterns
- E2E testing with Cypress/Playwright
- Accessibility testing
- Performance testing

---

## 🎯 Frontend Highlights

### Unique Innovations
1. **Adaptive Interface System**
   - UI rebuilds nightly based on voice patterns
   - Different themes for different emotional states
   - Component visibility based on user needs
   - Personalized greetings and observations

2. **Cultural Interface Adaptation**
   - Swahili/English language switching
   - Cultural greeting patterns
   - East African color schemes and imagery
   - Culturally-appropriate resource recommendations

3. **Voice-First Design**
   - Large, accessible voice recording interface
   - Visual feedback during recording
   - Transcription display with confidence indicators
   - Emotion visualization from voice analysis

4. **Privacy-Preserving UI**
   - Client-side encryption before data transmission
   - No sensitive data stored in browser
   - Secure session management
   - Privacy controls and transparency

### Technical Excellence
- **React 18+**: Modern React with concurrent features
- **TypeScript**: Type safety and developer experience
- **Tailwind CSS**: Utility-first styling with design system
- **PWA**: Offline capability and app-like experience
- **Responsive Design**: Mobile-first with desktop support

---

## 🎨 Design System Overview

### Adaptive Themes
The interface adapts to user emotional state and cultural context:

| Theme | Use Case | Colors | Mood |
|-------|----------|--------|------|
| **Calm** | Anxiety, stress | Soft blues, greens | Spacious, gentle |
| **Warm** | Depression, low energy | Oranges, yellows | Encouraging, energizing |
| **Crisis** | High risk, urgent | High contrast, red accents | Clear, actionable |
| **Balanced** | Stable, improving | Teals, balanced palette | Growth-focused |

### Component Prominence Levels
Components render differently based on user needs:

| Prominence | Rendering | Use Case |
|------------|-----------|----------|
| **Modal** | Full-screen overlay | Crisis situations |
| **Top** | Hero section | Primary interactions |
| **Card** | Elevated content | Important information |
| **Sidebar** | Secondary content | Supporting resources |
| **Minimal** | Subtle presence | Background features |
| **Hidden** | Not rendered | Irrelevant content |

---

## 📱 Component Architecture

### Core Components (Production Ready)
```
src/components/
├── core/                           # 10 adaptive components
│   ├── VoiceRecorder.tsx          ✅ Voice input with feedback
│   ├── CulturalGreeting.tsx       ✅ Personalized greetings
│   ├── DissonanceIndicator.tsx    ✅ Truth gap visualization
│   ├── CrisisResources.tsx        ✅ Emergency support
│   ├── GentleObservations.tsx     ✅ Pattern insights
│   ├── WhatsWorking.tsx           ✅ Effective strategies
│   ├── ProgressCelebration.tsx    ✅ Achievement recognition
│   ├── TriggerAwareness.tsx       ✅ Pattern awareness
│   ├── SafetyCheck.tsx            ✅ Risk assessment
│   └── PersonalizedResources.tsx  ✅ Tailored resources
│
├── layout/                        # Layout system
│   ├── AdaptiveInterface.tsx      ✅ Main layout controller
│   ├── InterfaceRenderer.tsx      ✅ Dynamic component rendering
│   └── Section.tsx                ✅ Layout sections
│
└── shared/                        # Utility components
    ├── ErrorBoundary.tsx          ✅ Error handling
    ├── LoadingSpinner.tsx         ✅ Loading states
    └── ProtectedRoute.tsx         ✅ Authentication
```

### Page Components (85% Complete)
```
src/pages/
├── HomePage.tsx                   ✅ Main dashboard
├── ChatPage.tsx                   ✅ Voice conversation
├── ProfilePage.tsx                ✅ User profile
├── SettingsPage.tsx               ✅ App settings
├── LoginPage.tsx                  ✅ Authentication
├── RegisterPage.tsx               ✅ User registration
├── ConsentPage.tsx                ✅ Privacy consent
├── CrisisPage.tsx                 ✅ Emergency resources
└── OfflinePage.tsx                ✅ Offline mode
```

### Context Providers (100% Complete)
```
src/contexts/
├── AuthContext.tsx                ✅ Authentication state
├── EmotionContext.tsx             ✅ Emotion tracking
├── OfflineContext.tsx             ✅ Network status
└── ThemeContext.tsx               ✅ Adaptive theming
```

---

## 📊 Frontend Metrics

### Completion Status
| Category | Status | Completion |
|----------|--------|------------|
| **Component Library** | ✅ Complete | 100% (10/10 core components) |
| **Page Components** | ✅ Complete | 100% (9/9 pages) |
| **Context Providers** | ✅ Complete | 100% (4/4 contexts) |
| **Layout System** | ✅ Complete | 100% |
| **Testing Infrastructure** | ✅ Complete | 85% coverage |

### Performance Targets
- **First Contentful Paint**: <1.5s
- **Largest Contentful Paint**: <2.5s
- **Time to Interactive**: <3.5s
- **Cumulative Layout Shift**: <0.1
- **Lighthouse Score**: 90+ (Performance, Accessibility, Best Practices)

### Accessibility Compliance
- **WCAG AA**: Full compliance target
- **Screen Reader**: Complete ARIA support
- **Keyboard Navigation**: All interactive elements
- **Color Contrast**: 4.5:1 minimum ratio
- **Focus Management**: Visible focus indicators

---

## 🔄 Data Flow Architecture

### Frontend-Backend Integration
```
User Interaction
    ↓
Voice Recording (Web Audio API)
    ↓
Client-side Processing
    ↓
Encryption (Web Crypto API)
    ↓
API Request to Gateway
    ↓
Service Processing
    ↓
Encrypted Response
    ↓
Client-side Decryption
    ↓
UI Update (React State)
    ↓
Adaptive Interface Rendering
```

### State Management
- **React Context**: Global state (auth, theme, emotion)
- **Local State**: Component-specific state
- **Session Storage**: Temporary data (encrypted)
- **IndexedDB**: Offline data storage
- **Cache**: API response caching

---

## 🎯 User Experience Patterns

### Voice-First Interaction Flow
1. **Cultural Greeting** - Personalized welcome
2. **Voice Recording** - Primary interaction method
3. **Real-time Feedback** - Visual recording indicators
4. **Processing State** - Loading with progress
5. **Results Display** - Emotion and insights
6. **Adaptive Response** - Interface adjusts to results

### Adaptive Interface Behavior
- **Morning Login**: Interface reflects overnight analysis
- **Emotional State**: Theme adapts to detected emotions
- **Risk Level**: Component prominence adjusts to risk
- **Cultural Context**: Language and imagery adapt
- **Progress Tracking**: Interface celebrates improvements

### Offline Experience
- **Offline Detection**: Network status monitoring
- **Local Storage**: Encrypted offline data
- **Sync Indicators**: Clear sync status
- **Graceful Degradation**: Reduced functionality offline
- **Background Sync**: Automatic sync when online

---

## 🚀 Future Frontend Evolution

### Phase 1 (Current): Core Interface
- Complete adaptive component system
- Cultural context integration
- Offline-first functionality
- Basic personalization

### Phase 2 (Next 3 months): Enhancement
- Advanced animations and micro-interactions
- Voice visualization improvements
- Enhanced cultural adaptation
- Performance optimizations

### Phase 3 (Next 6 months): Mobile
- React Native mobile application
- Native device integrations
- Enhanced offline capabilities
- Platform-specific optimizations

---

## 📖 Related Documentation

### Technical Implementation
- [Architecture Overview](../architecture/system-overview.md)
- [API Integration](../api/overview.md)
- [Development Setup](../development/setup-guide.md)
- [Testing Guide](../development/testing-guide.md)

### Design Resources
- [Design System Specifications](design-system.md)
- [Component Library](components.md)
- [Cultural Adaptation Guidelines](design-system.md#cultural-themes)
- [Accessibility Standards](design-system.md#accessibility)

### Project Context
- [Project Status](../project-status/current-status.md)
- [Backend Architecture](../architecture/microservices.md)
- [Security Architecture](../architecture/security-architecture.md)

---

**Frontend Team**: UI/UX Design, Frontend Engineering, Accessibility  
**Last Updated**: January 11, 2025  
**Next Review**: After cultural context integration