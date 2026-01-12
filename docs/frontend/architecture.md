# Frontend Architecture

## Privacy Through Radical Personalization

**Core Principle:** When two users see each other's screens, they should look like completely different apps.

This prevents:
- Social stigma (others don't know you're using mental health support)
- Identification (can't tell who else uses the app)
- Privacy breaches (your interface reveals nothing about others)

**How we achieve this:**
1. **Different themes**: Calm (blues) vs Warm (oranges) vs Crisis (high contrast) vs Balanced (teals)
2. **Different components**: Sarah sees DissonanceIndicator, James doesn't
3. **Different layouts**: Components in different orders, prominence levels
4. **Different language**: Swahili vs English vs Mixed
5. **Different greetings**: Personalized messages based on patterns

Result: **Same app, infinitely different appearances**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  App Entry Point (index.tsx)                         │  │
│  │  - Fetch UIConfig from API                           │  │
│  │  - Decrypt config (E2E)                              │  │
│  │  - Pass to InterfaceRenderer                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  InterfaceRenderer                                    │  │
│  │  - Takes UIConfig                                     │  │
│  │  - Applies theme (ThemeProvider)                     │  │
│  │  - Renders layout sections (hero, primary, sidebar)  │  │
│  │  - Dynamic component loading                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Component Registry                                   │  │
│  │  Maps component names → React components             │  │
│  │  {                                                    │  │
│  │    'VoiceRecorder': VoiceRecorderComponent,          │  │
│  │    'DissonanceIndicator': DissonanceIndicatorComp,   │  │
│  │    'CrisisResources': CrisisResourcesComponent,      │  │
│  │    ...                                                │  │
│  │  }                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Core Components (10 components)                      │  │
│  │  - VoiceRecorder                                      │  │
│  │  - CulturalGreeting                                   │  │
│  │  - DissonanceIndicator                                │  │
│  │  - CrisisResources                                    │  │
│  │  - GentleObservations                                 │  │
│  │  - WhatsWorking                                       │  │
│  │  - ProgressCelebration                                │  │
│  │  - TriggerAwareness                                   │  │
│  │  - SafetyCheck                                        │  │
│  │  - PersonalizedResources                              │  │
│  │                                                        │  │
│  │  Each component:                                      │  │
│  │  - Accepts props from ComponentConfig                │  │
│  │  - Responds to prominence (modal, card, sidebar)     │  │
│  │  - Adapts to theme context                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS + CSS-in-JS (styled-components)
- **State**: Zustand (lightweight, no boilerplate)
- **Audio**: Web Audio API + MediaRecorder
- **Encryption**: Web Crypto API (AES-GCM)
- **Routing**: React Router (minimal, mostly single-page)
- **Build**: Vite (fast, modern)

---

## Theme System

### ThemeProvider Component

```typescript
interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
    accent: string;
    warning: string;
  };
  spacing: 'compressed' | 'comfortable' | 'spacious';
  animations: 'none' | 'gentle' | 'moderate';
  contrast: 'low' | 'medium' | 'high';
  fontScale: number;
}

<ThemeProvider theme={theme}>
  {children}
</ThemeProvider>
```

Themes are **injected from UIConfig**, not hardcoded. Each user gets their own theme.

---

## Component Prominence Levels

Components render differently based on prominence:

| Prominence | Rendering |
|-----------|-----------|
| `modal` | Full-screen overlay, blocks interaction |
| `top` | Hero section, full width |
| `card` | Primary section, elevated card |
| `sidebar` | Sidebar, less prominent |
| `minimal` | Footer, subtle |
| `hidden` | Not rendered |

**Example:**
- Sarah (high risk): `CrisisResources` = **modal** (full-screen urgent)
- James (low risk): `CrisisResources` = **hidden** (not shown)

---

## Component Props

Each component receives props from `ComponentConfig`:

```typescript
interface ComponentProps {
  prominence: 'modal' | 'top' | 'card' | 'sidebar' | 'minimal' | 'hidden';
  urgency: 'none' | 'low' | 'medium' | 'high' | 'critical';
  props: Record<string, any>; // Component-specific props
}
```

**Example - VoiceRecorder:**
```typescript
<VoiceRecorder
  prominence="top"
  urgency="high"
  props={{
    prompt: "Niambie hali yako halisi?",
    culturalMode: "swahili",
    encouragement: "Your voice matters. We're here to listen."
  }}
/>
```

---

## Layout Rendering

### Desktop Layout (3 sections)

```
┌─────────────────────────────────────────────────┐
│  Hero Section                                    │
│  (modal, top prominence)                         │
│  - SafetyCheck (if critical)                     │
│  - VoiceRecorder                                 │
│  - CulturalGreeting                              │
└─────────────────────────────────────────────────┘
┌───────────────────────────┬─────────────────────┐
│  Primary Section          │  Sidebar            │
│  (card prominence)        │  (sidebar prom.)    │
│  - DissonanceIndicator    │  - TriggerAwareness │
│  - GentleObservations     │  - Resources        │
│  - ProgressCelebration    │                     │
└───────────────────────────┴─────────────────────┘
┌─────────────────────────────────────────────────┐
│  Footer                                          │
│  (minimal prominence)                            │
└─────────────────────────────────────────────────┘
```

### Mobile Layout (single column)

```
┌─────────────────┐
│  Hero           │
│  - SafetyCheck  │
│  - VoiceRec     │
│  - Greeting     │
├─────────────────┤
│  Primary        │
│  (Top 5-7)      │
│  - Dissonance   │
│  - Crisis       │
│  - Observations │
│  ...            │
└─────────────────┘
```

Layout is **computed from UIConfig.layout** and **UIConfig.mobile_layout**.

---

## Visual Diversity Examples

### Sarah (Anxiety, Medium Risk)

**Theme**: Calm (blues, greens, spacious)
**Components**:
- VoiceRecorder (top)
- CulturalGreeting: "We're listening" (gentle)
- CrisisResources (sidebar, medium prominence)
- TriggerAwareness (sidebar)

**Appearance**: Spacious, lots of white space, soft blues, gentle animations

---

### James (Depression, High Risk)

**Theme**: Crisis (high contrast, no animations)
**Components**:
- SafetyCheck (modal, full-screen)
- CrisisResources (hero section, urgent red)
- VoiceRecorder (card)
- DissonanceIndicator (card)

**Appearance**: High contrast black/white/red, compressed spacing, no animations

---

### Amina (Improving, Low Risk)

**Theme**: Balanced (teals, growth-focused)
**Components**:
- VoiceRecorder (top)
- ProgressCelebration (card, prominent)
- WhatsWorking (card)
- PersonalizedResources (sidebar)

**Appearance**: Bright teals, moderate spacing, moderate animations, celebratory

---

**When these three users sit next to each other, they see COMPLETELY DIFFERENT apps.**

Sarah: Soft blues, lots of space
James: Stark black/white/red, urgent
Amina: Bright teals, celebratory

**No one knows they're using the same platform.**

---

## File Structure

```
frontend/
├── src/
│   ├── main.tsx                      # Entry point
│   ├── App.tsx                       # Main app component
│   │
│   ├── components/
│   │   ├── core/                     # 10 core components
│   │   │   ├── VoiceRecorder.tsx
│   │   │   ├── CulturalGreeting.tsx
│   │   │   ├── DissonanceIndicator.tsx
│   │   │   ├── CrisisResources.tsx
│   │   │   ├── GentleObservations.tsx
│   │   │   ├── WhatsWorking.tsx
│   │   │   ├── ProgressCelebration.tsx
│   │   │   ├── TriggerAwareness.tsx
│   │   │   ├── SafetyCheck.tsx
│   │   │   └── PersonalizedResources.tsx
│   │   │
│   │   ├── layout/                   # Layout components
│   │   │   ├── InterfaceRenderer.tsx
│   │   │   ├── Section.tsx
│   │   │   └── ComponentWrapper.tsx
│   │   │
│   │   └── shared/                   # Shared components
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       └── Button.tsx
│   │
│   ├── theme/
│   │   ├── ThemeProvider.tsx         # Theme context provider
│   │   ├── themes.ts                 # Theme definitions
│   │   └── useTheme.ts               # Theme hook
│   │
│   ├── registry/
│   │   └── ComponentRegistry.ts      # Maps component names → components
│   │
│   ├── services/
│   │   ├── api.ts                    # API client
│   │   ├── encryption.ts             # E2E encryption (Web Crypto API)
│   │   └── audio.ts                  # Audio recording
│   │
│   ├── store/
│   │   └── useConfigStore.ts         # Zustand store for UIConfig
│   │
│   └── types/
│       └── index.ts                  # TypeScript types
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## Data Flow

```
1. User opens app
   ↓
2. App fetches encrypted UIConfig from API
   GET /api/users/{user_id}/interface/current
   ↓
3. Decrypt UIConfig using user's encryption key
   (Web Crypto API)
   ↓
4. Parse UIConfig → extract theme, components, layout
   ↓
5. InterfaceRenderer receives UIConfig
   ↓
6. Apply theme (ThemeProvider wraps app)
   ↓
7. Render layout sections (hero, primary, sidebar)
   ↓
8. For each component in layout:
   - Look up component in registry
   - Pass props from ComponentConfig
   - Render with prominence styling
   ↓
9. User interacts (records voice)
   ↓
10. Voice sent to backend for processing
    ↓
11. Patterns updated
    ↓
12. Next night: New UIConfig generated
    ↓
13. On next login: Interface has evolved
```

---

## Key Implementation Details

### 1. Dynamic Component Loading

```typescript
const ComponentRegistry = {
  VoiceRecorder: lazy(() => import('./components/core/VoiceRecorder')),
  CulturalGreeting: lazy(() => import('./components/core/CulturalGreeting')),
  DissonanceIndicator: lazy(() => import('./components/core/DissonanceIndicator')),
  // ... all 10 components
};

function renderComponent(componentName: string, config: ComponentConfig) {
  const Component = ComponentRegistry[componentName];
  return (
    <Suspense fallback={<Skeleton />}>
      <Component {...config.props} prominence={config.prominence} urgency={config.urgency} />
    </Suspense>
  );
}
```

### 2. Prominence Styling

```typescript
const prominenceStyles = {
  modal: 'fixed inset-0 z-50 bg-white',
  top: 'w-full mb-8',
  card: 'bg-white rounded-lg shadow-md p-6 mb-4',
  sidebar: 'bg-gray-50 rounded p-4 mb-3',
  minimal: 'text-sm text-gray-600',
  hidden: 'hidden'
};
```

### 3. Theme Application

```typescript
function applyTheme(theme: ThemeConfig) {
  return {
    '--color-primary': theme.colors.primary,
    '--color-secondary': theme.colors.secondary,
    '--color-background': theme.colors.background,
    '--color-text': theme.colors.text,
    '--spacing-scale': theme.spacing === 'spacious' ? 1.5 :
                       theme.spacing === 'compressed' ? 0.75 : 1,
    '--animation-speed': theme.animations === 'none' ? '0s' :
                         theme.animations === 'gentle' ? '0.8s' : '0.4s',
    '--font-scale': theme.fontScale,
  };
}
```

### 4. Change Notifications

When user logs in and sees new interface:

```typescript
// Check if there are unacknowledged changes
const changes = uiConfig.changes.filter(c => !c.acknowledged);

if (changes.length > 0) {
  // Show change notification
  <ChangeNotification changes={changes} />
  // "We've noticed a gap between your words and your voice..."
}
```

---

## Responsive Design

### Desktop (≥1024px)
- 3-column layout (hero full-width, then 2-column primary/sidebar)
- All components visible (if not hidden)
- Full prominence differentiation

### Tablet (768px - 1023px)
- 2-column layout (hero full-width, then primary/sidebar collapse to 2-column)
- Some components deprioritized to sidebar

### Mobile (<768px)
- Single column
- Only show top 5-7 most important components (from mobile_layout)
- Modal components take full screen
- Simplified animations

---

## Accessibility

- **Keyboard navigation**: All interactive elements accessible via keyboard
- **Screen readers**: ARIA labels on all components
- **High contrast mode**: Crisis theme is already high contrast
- **Text scaling**: Font scale adjustable from UIConfig
- **Focus indicators**: Visible focus rings
- **Language support**: Swahili + English (from UIConfig)

---

## Performance

- **Code splitting**: Each component lazy-loaded
- **Theme caching**: Theme CSS variables computed once, applied globally
- **UIConfig caching**: Stored in localStorage (encrypted), reused until next login
- **Audio streaming**: Voice data streamed, not stored client-side
- **Minimal re-renders**: Zustand store prevents unnecessary re-renders

---

## Security

### Client-Side Encryption

```typescript
// Decrypt UIConfig on client
async function decryptUIConfig(encryptedConfig: string, userKey: CryptoKey) {
  const encrypted = base64ToArrayBuffer(encryptedConfig);
  const iv = encrypted.slice(0, 16);
  const ciphertext = encrypted.slice(16);

  const plaintext = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    userKey,
    ciphertext
  );

  return JSON.parse(new TextDecoder().decode(plaintext));
}
```

### No Local Storage of Sensitive Data

- UIConfig stored encrypted in localStorage
- Audio never stored (streamed directly to server)
- User key derived from passphrase (never stored)

---

## Next Steps

1. **Set up React project** (Vite + TypeScript + Tailwind)
2. **Build theme system** (ThemeProvider + theme definitions)
3. **Build 10 core components**
4. **Build InterfaceRenderer** (layout + dynamic rendering)
5. **Build component registry**
6. **Test visual diversity** (3 different user interfaces side-by-side)
7. **Integrate with backend API**
8. **Add encryption layer**
9. **Deploy to production**

Ready to build.
