# Resona Design System v1.0

**The Adaptive Mental Health Interface**

> "Your voice shapes your interface. Your truth guides your experience."

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Core Principles](#core-principles)
3. [Component Catalog](#component-catalog)
4. [Theming System](#theming-system)
5. [Layout System](#layout-system)
6. [Visual Identity](#visual-identity)
7. [Adaptation Logic](#adaptation-logic)
8. [Voice & Tone](#voice--tone)
9. [Accessibility](#accessibility)
10. [Implementation Guide](#implementation-guide)

---

## Design Philosophy

### The Fundamental Insight

**Traditional mental health apps are static tools that treat all users the same.**

**Resona is a living companion that evolves with each individual.**

The interface doesn't just display information—it **adapts to the emotional truth** detected in each user's voice, creating a uniquely personal experience that grows and changes as they do.

### The Overnight Transformation

Every night, while users sleep, Resona analyzes their voice patterns, emotional states, cultural markers, and behavioral signals to rebuild their interface. The next morning, they log in to find an experience tailored specifically to their needs, their journey, their truth.

### Design as Truth Detection

The interface itself becomes a mirror of the user's emotional state:
- When they're concealing distress ("I'm fine" but voice says otherwise), the interface gently acknowledges the gap
- When they're in crisis, the interface transforms to prioritize safety
- When they're stable, the interface focuses on growth and insight
- When they're improving, the interface celebrates progress

---

## Core Principles

### 1. **Emotional Intelligence**

The interface adapts to emotional state, not just stated preferences.

**Implementation:**
- Colors shift based on detected emotions (calming for anxiety, warm for depression)
- Layout density changes with urgency (compact for crisis, spacious for exploration)
- Component visibility responds to emotional needs (crisis resources appear when needed)

**Example:**
```
User with Anxiety:
→ Soft blues, generous spacing, slow animations
→ "Let's take this slowly. You're safe here."

User with Depression:
→ Warm oranges, energizing yellows, gentle prompts
→ "We see you. Small steps are still steps."

User in Crisis:
→ Clear whites, alert colors, direct actions
→ "We're concerned. Let's get you support right now."
```

---

### 2. **Voice-Truth Alignment**

The interface reflects the truth detected in the user's voice, not just their words.

**Implementation:**
- When high dissonance detected (saying "fine" but voice shows distress), interface acknowledges the gap
- Voice-truth timeline shows the difference between stated and embodied emotion
- Gentle observations validate what voice reveals: "Your words say one thing, but we hear something else in your voice"

**Example:**
```
User says: "I'm managing fine"
Voice shows: Sadness + tremor + sighs

Interface responds:
┌─────────────────────────────────────┐
│ We Notice Something                  │
├─────────────────────────────────────┤
│ You said "managing fine," but your  │
│ voice sounds heavy today. It's okay │
│ to not be okay. Want to talk about  │
│ what's really going on?              │
└─────────────────────────────────────┘
```

---

### 3. **Cultural Sensitivity**

The interface adapts to cultural context, language preferences, and communication styles.

**Implementation:**
- Language mixing (Swahili/English) based on user patterns
- Cultural deflection detection ("nimechoka" interpreted as exhaustion/giving up, not just "tired")
- Respect for stoicism while inviting vulnerability
- Localized resources (Kenyan mental health services, East African context)

**Example:**
```
East African User (Stoic Pattern):
→ Swahili greetings: "Habari yako?"
→ Permission-giving: "We know sharing burdens can feel uncomfortable. Here, it's safe."
→ Cultural understanding: When they say "sawa," interface checks voice for hidden distress

Western User (More Expressive):
→ English prompts: "How are you feeling today?"
→ Direct engagement: "Tell me what's on your mind."
→ Takes words at face value when voice aligns
```

---

### 4. **Risk-Responsive**

The interface transforms based on detected risk level—from encouraging to urgent.

**Implementation:**
- Crisis resources hidden for low-risk users, prominent for high-risk
- Interface urgency matches risk level (calm → concerned → urgent)
- One-click counselor connection appears when critically needed
- Emergency resources with local context (Kenyan hotlines, not generic)

**Risk Levels:**

| Risk Level | Interface State | Tone | Crisis Resources | Layout |
|------------|----------------|------|------------------|--------|
| **Low** | Encouraging, exploratory | "Let's explore..." | Hidden | Spacious, calm |
| **Medium** | Supportive, watchful | "We're here with you..." | Sidebar, subtle | Balanced |
| **High** | Concerned, direct | "We're concerned..." | Prominent card | Focused |
| **Critical** | Urgent, actionable | "Let's get you help now." | Top, modal | Compact, clear |

---

### 5. **Progressive Disclosure**

Show only what's relevant now. Hide what's not needed.

**Implementation:**
- Features that are never used → hidden after 14 days
- Crisis resources → shown only when risk detected
- Progress celebration → hidden when user is declining
- Advanced features → revealed as user grows comfortable

**Example:**
```
Week 1: Show all features (let user explore)
Week 3: Hide unused medication tracker, show used breathing exercises
Week 5: Crisis detected → hide progress, show counselor connection
Week 8: Stable → bring back progress, hide crisis resources
```

---

### 6. **Validation Over Judgment**

Never tell users what to do. Validate, observe, invite.

**Language Rules:**
- ❌ "You should try meditation"
- ✅ "When you mentioned nature walks, your voice lifted. That seems to help you."

- ❌ "Stop thinking negatively"
- ✅ "We hear how heavy things feel right now."

- ❌ "Just be positive"
- ✅ "Your feelings are valid. Depression lies—this isn't your fault."

**Implementation:**
- All prompts are invitations, not commands
- Observations are gentle, not prescriptive
- User always has control (can dismiss, skip, ignore)

---

### 7. **Transparency & Trust**

Users can see what the system detects and why the interface changed.

**Implementation:**
- Interface change log: "We noticed X, so we changed Y"
- Dissonance explanation: "Your voice sounded different from your words because..."
- Privacy controls: User can see what data is used, delete patterns, export config

**Example:**
```
Interface Change Notification:
┌─────────────────────────────────────────┐
│ Your Interface Updated Last Night       │
├─────────────────────────────────────────┤
│ What we noticed:                        │
│ • Your voice has been calmer in morning │
│   sessions (3 days in a row)            │
│ • Breathing exercises seem to help you  │
│ • You haven't used the journal feature  │
│                                         │
│ What we changed:                        │
│ ✓ Moved breathing exercises higher     │
│ ✓ Hidden journal (you can bring it     │
│   back anytime)                         │
│ ✓ Added morning encouragement           │
│                                         │
│ [See Full Change Log] [Undo Changes]   │
└─────────────────────────────────────────┘
```

---

## Component Catalog

All UI components that can be composed by the adaptive engine.

### Greeting Components

#### `<CulturalGreeting>`

Culturally-aware greeting that adapts to language preference and time of day.

**Props:**
```typescript
interface CulturalGreetingProps {
  language: 'swahili' | 'english' | 'mixed';
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  mood: 'warm' | 'gentle' | 'concerned' | 'celebratory';
  personalization: string; // e.g., "Your energy is usually higher now"
  userName?: string;
}
```

**Variants:**

```tsx
// Swahili morning (warm)
<CulturalGreeting
  language="swahili"
  timeOfDay="morning"
  mood="warm"
  personalization="Your voice is brighter in the mornings"
/>
// Output: "Habari za asubuhi, Sarah 🌅 Your voice is brighter in the mornings"

// English evening (concerned)
<CulturalGreeting
  language="english"
  timeOfDay="evening"
  mood="concerned"
  personalization="We've noticed your evenings have been harder"
/>
// Output: "Evening, James. We've noticed your evenings have been harder."

// Mixed language (gentle)
<CulturalGreeting
  language="mixed"
  timeOfDay="afternoon"
  mood="gentle"
/>
// Output: "Habari, how are you doing today?"
```

**Adaptation Logic:**
- Detected code-switching → `language="mixed"`
- User preference for Swahili → `language="swahili"`
- Risk elevated → `mood="concerned"`
- Progress detected → `mood="celebratory"`

---

### Voice Input Components

#### `<VoiceRecorder>`

Primary interaction—records user's voice with context-aware prompts.

**Props:**
```typescript
interface VoiceRecorderProps {
  prompt: string; // Dynamic, generated based on patterns
  promptLanguage: 'swahili' | 'english' | 'mixed';
  visualFeedback: 'waveform' | 'ambient' | 'minimal';
  culturallyAdapted: boolean;
  urgency: 'low' | 'medium' | 'high';
  maxDuration?: number; // seconds
}
```

**Variants:**

```tsx
// Anxiety user (calm, open-ended)
<VoiceRecorder
  prompt="Take your time. When you're ready, tell me what's on your mind."
  visualFeedback="ambient"
  urgency="low"
/>

// Depression user (warm, inviting)
<VoiceRecorder
  prompt="We're here. What's one thing you're feeling right now?"
  visualFeedback="waveform"
  urgency="low"
/>

// Crisis user (direct, clear)
<VoiceRecorder
  prompt="We're concerned about you. Talk to us—what's happening right now?"
  visualFeedback="minimal"
  urgency="high"
/>

// Swahili preference
<VoiceRecorder
  prompt="Niambie hali yako leo?"
  promptLanguage="swahili"
  culturallyAdapted={true}
/>
```

**Adaptation Logic:**
- User responds better to questions → prompt is question-based
- User prefers open-ended → prompt is invitational
- User deflects with "fine" → prompt addresses the pattern: "Last time you said 'sawa' but your voice sounded different. How are you really?"

---

### Emotion Visualization Components

#### `<EmotionTimeline>`

Shows user's emotional journey over time, with patterns highlighted.

**Props:**
```typescript
interface EmotionTimelineProps {
  timespan: '7day' | '30day' | 'session' | 'all';
  showPatterns: boolean;
  showTriggers: boolean;
  showCoping: boolean;
  highlightDissonance: boolean;
  style: 'detailed' | 'simple' | 'sparkline';
}
```

**Variants:**

```tsx
// Detailed view with patterns
<EmotionTimeline
  timespan="7day"
  showPatterns={true}
  showTriggers={true}
  showCoping={true}
  style="detailed"
/>

// Simple sparkline for overview
<EmotionTimeline
  timespan="30day"
  showPatterns={false}
  style="sparkline"
/>
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ Your Emotional Journey (Last 7 Days)       │
├─────────────────────────────────────────────┤
│                                             │
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun         │
│   😌   😔   😔   😟   😌   😔   😌         │
│                                             │
│ Patterns We Notice:                         │
│ • Mornings: Generally better (😌)          │
│ • Evenings: Harder, especially after        │
│   family dinners (😔)                       │
│ • Weekends: Mixed                           │
│                                             │
│ What Seems to Help:                         │
│ ✓ When you talk about nature walks,        │
│   your voice lifts                          │
│ ✓ Morning sessions lead to better days     │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Stable user → show detailed patterns, celebrate progress
- Declining user → simplify view, don't emphasize negative patterns
- Crisis user → hide timeline, focus on present moment

---

#### `<DissonanceIndicator>`

Shows the gap between what user says and what voice reveals.

**Props:**
```typescript
interface DissonanceIndicatorProps {
  visibility: 'always' | 'when_detected' | 'never';
  showExplanation: boolean;
  statedEmotion: string;
  voiceEmotion: string;
  dissonanceScore: number; // 0-1
  interpretation: string;
}
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ 🔍 We Notice a Gap                          │
├─────────────────────────────────────────────┤
│                                             │
│  Your Words:    "I'm fine, really"          │
│  Your Voice:    Sad, trembling              │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│        High Dissonance (85%)                │
│                                             │
│  What this might mean:                      │
│  You may be hiding how hard things really   │
│  are. That's understandable—but here, you   │
│  don't have to. We're here to listen to     │
│  the truth your voice is telling.           │
│                                             │
│  [Tell me more]  [I'm okay, really]         │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Low dissonance → component hidden (words and voice align)
- Medium dissonance → subtle indicator, gentle question
- High dissonance → prominent card, direct acknowledgment
- Critical risk + dissonance → urgent tone, counselor connection

---

### Risk & Safety Components

#### `<CrisisResources>`

Adaptive crisis resources that appear/disappear based on risk.

**Props:**
```typescript
interface CrisisResourcesProps {
  prominence: 'hidden' | 'sidebar' | 'card' | 'top' | 'modal';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  localContext: 'kenya' | 'uganda' | 'tanzania' | 'rwanda' | 'global';
  showCounselor: boolean;
  oneClickConnect: boolean;
}
```

**Variants:**

```tsx
// Low risk - hidden
<CrisisResources prominence="hidden" />

// Medium risk - sidebar
<CrisisResources
  prominence="sidebar"
  urgency="medium"
  localContext="kenya"
/>

// High risk - prominent card
<CrisisResources
  prominence="card"
  urgency="high"
  localContext="kenya"
  showCounselor={true}
/>

// Critical risk - modal (blocks other content)
<CrisisResources
  prominence="modal"
  urgency="critical"
  localContext="kenya"
  oneClickConnect={true}
/>
```

**Visual Output (High Urgency):**

```
┌─────────────────────────────────────────────┐
│ 🆘 We're Here to Support You                │
├─────────────────────────────────────────────┤
│                                             │
│ We've noticed signs that concern us.        │
│ You're not alone. Help is available.        │
│                                             │
│ [🎯 Connect with Counselor Now]             │
│                                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                             │
│ Crisis Resources (Kenya):                   │
│ • Mental Health Hotline: 0800 720 000      │
│ • Crisis SMS: Text HELP to 21995           │
│ • Befrienders Kenya: +254 722 178 177      │
│ • Emergency: 112                            │
│                                             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                             │
│ Immediate Steps:                            │
│ ✓ You're safe right now                     │
│ ✓ These feelings will pass                  │
│ ✓ Call someone—don't be alone               │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Risk level determines prominence
- Location determines hotline numbers
- Time of day affects counselor availability messaging
- Previous help-seeking behavior affects language (if they've called before, acknowledge it)

---

#### `<SafetyCheck>`

Gentle check-in when risk is detected.

**Props:**
```typescript
interface SafetyCheckProps {
  tone: 'gentle' | 'direct' | 'urgent';
  context: string; // Why we're asking
  frequency: 'once' | 'daily' | 'session';
}
```

**Visual Output (Gentle):**

```
┌─────────────────────────────────────────────┐
│ Quick Check-In                              │
├─────────────────────────────────────────────┤
│                                             │
│ Your voice has sounded different lately—    │
│ flatter, more pauses. We want to make sure  │
│ you're okay.                                │
│                                             │
│ Are you thinking about hurting yourself?    │
│                                             │
│ [Yes] [No] [I don't know] [I don't want    │
│                            to answer]       │
│                                             │
│ (Your answer helps us support you better.   │
│  We won't judge—we just want you safe.)     │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- First time asking → gentle, with explanation
- Follow-up → more direct
- User history of avoidance → option to skip but with "we're concerned" message

---

### Insight & Progress Components

#### `<WhatsWorking>`

Shows coping strategies that actually help THIS user.

**Props:**
```typescript
interface WhatsWorkingProps {
  strategies: Array<{
    name: string;
    effectiveness: number; // 0-1
    evidence: string; // "Your voice calms 80% of the time after"
  }>;
  maxItems: number;
  showEvidence: boolean;
}
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ 🌱 What's Working for You                   │
├─────────────────────────────────────────────┤
│                                             │
│ These help you (we can tell from your      │
│ voice):                                     │
│                                             │
│ ✓ Breathing exercises                       │
│   → Your voice calms 80% of the time after  │
│                                             │
│ ✓ Talking about work                        │
│   → Seems to distract from harder thoughts  │
│                                             │
│ ✓ Morning walks                             │
│   → You sound lighter when you mention them │
│                                             │
│ Keep doing what works for YOU.              │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Only show strategies with effectiveness > 0.6
- Rank by actual voice improvement, not self-report
- Update weekly as new patterns emerge
- Hidden if no effective strategies found yet

---

#### `<GentleObservations>`

Validates what the system detects without judgment.

**Props:**
```typescript
interface GentleObservationsProps {
  observations: Array<{
    type: 'trigger' | 'deflection' | 'pattern' | 'progress';
    message: string;
  }>;
  tone: 'validating' | 'curious' | 'concerned';
}
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ 💭 Gentle Observations (Not Judgments)      │
├─────────────────────────────────────────────┤
│                                             │
│ • You said "sawa" 4 times this week when    │
│   your voice sounded sad. Remember, it's    │
│   okay not to be okay here.                 │
│                                             │
│ • Family topics still bring tension to      │
│   your voice. Take your time—we can         │
│   explore when you're ready.                │
│                                             │
│ • You've been opening up more each session. │
│   That takes courage. We see it.            │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Cultural deflections → gently name the pattern
- Triggers → acknowledge without forcing exploration
- Progress → celebrate quietly (not over-the-top)
- Max 3 observations per session (not overwhelming)

---

#### `<ProgressCelebration>`

Celebrates genuine progress (hidden when user is declining).

**Props:**
```typescript
interface ProgressCelebrationProps {
  visibility: 'shown' | 'hidden'; // Based on trajectory
  metrics: Array<{
    label: string;
    improvement: number;
  }>;
  tone: 'quiet' | 'warm' | 'celebratory';
}
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ 🌟 We See Your Progress                     │
├─────────────────────────────────────────────┤
│                                             │
│ Over the last 2 weeks:                      │
│                                             │
│ ✓ Your voice has more energy in the         │
│   mornings (5 days straight)                │
│                                             │
│ ✓ You're pausing less before speaking       │
│   (sign of less hesitation)                 │
│                                             │
│ ✓ You mentioned "hopeless" only once this   │
│   week (vs 4 times last week)               │
│                                             │
│ These might seem small, but they're not.    │
│ Healing isn't linear—and you're moving.     │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Only shown if genuine improvement detected
- Hidden if user declining (would feel invalidating)
- Hidden during crisis
- Tone matches emotional state (quiet for fragile progress, warm for solid)

---

### Resource Components

#### `<PersonalizedResources>`

Resources filtered to user's specific patterns and cultural context.

**Props:**
```typescript
interface PersonalizedResourcesProps {
  filters: {
    mentalHealthNeeds: string[]; // ['depression', 'anxiety']
    culturalContext: string; // 'kenya'
    triggers: string[]; // ['family', 'work']
    coping: string[]; // ['breathing', 'nature']
  };
  maxItems: number;
  showReason: boolean; // Why this resource is suggested
}
```

**Visual Output:**

```
┌─────────────────────────────────────────────┐
│ 📚 Resources Chosen for You                 │
├─────────────────────────────────────────────┤
│                                             │
│ Based on what we've learned about your      │
│ journey, these might help:                  │
│                                             │
│ 🌍 Managing Family Expectations             │
│    (East African Context)                   │
│    → We noticed family is a trigger for you │
│    [Read More]                              │
│                                             │
│ 🧠 Understanding Emotional Exhaustion       │
│    vs Physical Tiredness                    │
│    → You often say "tired"—this explores    │
│      what that really means                 │
│    [Read More]                              │
│                                             │
│ 👥 Support Groups - Nairobi Area            │
│    → In-person mental health circles        │
│    [Find Groups]                            │
│                                             │
│ [Hidden: 47 other generic resources]        │
│                                             │
└─────────────────────────────────────────────┘
```

**Adaptation Logic:**
- Filter by detected mental health needs
- Localize to user's geography
- Match to identified triggers
- Hide resources for problems they don't have
- Update as patterns change

---

### Navigation Components

#### `<AdaptiveMenu>`

Navigation that reorganizes based on usage and needs.

**Props:**
```typescript
interface AdaptiveMenuProps {
  items: Array<{
    id: string;
    label: string;
    icon: string;
    usageCount: number;
    priority: number; // Based on current needs
    visible: boolean;
  }>;
  layout: 'bottom' | 'sidebar' | 'hamburger';
}
```

**Adaptation Logic:**
- Crisis mode → only show "Talk Now", "Get Help", "Home"
- Most used features → top of menu
- Never used features → hidden after 14 days
- New features → badged "New" for 7 days

---

## Theming System

### Emotional State Themes

The visual design adapts to the user's detected emotional state.

#### Anxiety Theme

**Purpose**: Calm, spacious, breathing room

```typescript
const anxietyTheme = {
  name: 'Calm',

  colors: {
    primary: '#4A90A4',        // Calming blue
    secondary: '#7FB685',      // Soothing green
    background: '#F5F9FA',     // Soft, airy white
    surface: '#FFFFFF',
    text: {
      primary: '#2C3E50',
      secondary: '#7F8C8D',
      tertiary: '#BDC3C7'
    },
    accent: '#81C784',         // Gentle green accent
    warning: '#FFA726',        // Soft orange (not harsh red)
    danger: '#EF5350'
  },

  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif'
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem'
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    lineHeight: 1.6,           // More breathing room
    letterSpacing: '0.01em'
  },

  spacing: {
    unit: 8,
    scale: 'generous',         // 1.5x normal spacing
    containerPadding: 24,      // Extra padding
    componentGap: 24
  },

  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    round: '50%'
  },

  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.05)',
    md: '0 4px 8px rgba(0,0,0,0.08)',
    lg: '0 8px 16px rgba(0,0,0,0.12)',
    none: 'none'
  },

  animations: {
    duration: {
      fast: '200ms',
      normal: '400ms',         // Slower than standard
      slow: '600ms'
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'reduced-motion' // Respect accessibility
  },

  layout: {
    maxWidth: '800px',         // Narrower, less overwhelming
    density: 'spacious'
  }
};
```

**Visual Effect:**
- Lots of white space
- Soft, rounded corners
- Gentle shadows
- Slow, calming animations
- Low visual noise

---

#### Depression Theme

**Purpose**: Warm, energizing, hopeful

```typescript
const depressionTheme = {
  name: 'Warmth',

  colors: {
    primary: '#E07A5F',        // Warm coral
    secondary: '#F2CC8F',      // Uplifting yellow
    background: '#FFF9F5',     // Warm off-white
    surface: '#FFFFFF',
    text: {
      primary: '#3D2817',      // Warm dark brown
      secondary: '#8B6F47',
      tertiary: '#C9B189'
    },
    accent: '#F4A261',         // Energizing orange
    success: '#E9C46A',        // Warm yellow (not cold green)
    warning: '#E76F51',
    danger: '#D62828'
  },

  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif'  // Warmer, friendlier serif
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem'
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    lineHeight: 1.5,
    letterSpacing: 'normal'
  },

  spacing: {
    unit: 8,
    scale: 'comfortable',      // Standard spacing
    containerPadding: 20,
    componentGap: 20
  },

  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px',
    round: '50%'
  },

  shadows: {
    sm: '0 2px 6px rgba(224, 122, 95, 0.1)',   // Warm shadows
    md: '0 4px 12px rgba(224, 122, 95, 0.15)',
    lg: '0 8px 20px rgba(224, 122, 95, 0.2)',
    none: 'none'
  },

  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms'
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'gentle'       // Subtle movement
  },

  layout: {
    maxWidth: '900px',
    density: 'comfortable'
  },

  illustrations: {
    style: 'warm',             // Warm colors, hopeful imagery
    context: 'sunrise'         // Metaphor: new beginnings
  }
};
```

**Visual Effect:**
- Warm, inviting colors
- Slightly higher contrast (easier to focus)
- Friendly, approachable
- Subtle encouraging motion

---

#### Crisis Theme

**Purpose**: Clear, urgent, actionable

```typescript
const crisisTheme = {
  name: 'Clarity',

  colors: {
    primary: '#D62828',        // Alert red (but not alarming)
    secondary: '#003049',      // Grounding navy
    background: '#FFFFFF',     // Pure white - maximum clarity
    surface: '#F8F9FA',
    text: {
      primary: '#000000',      // Maximum contrast
      secondary: '#495057',
      tertiary: '#6C757D'
    },
    accent: '#F77F00',         // Attention orange
    success: '#06A77D',
    warning: '#E76F51',
    danger: '#D62828'
  },

  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',  // Highly readable
      secondary: 'Inter, sans-serif' // No decorative fonts
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.25rem',           // Larger base
      xl: '1.5rem',
      '2xl': '2rem',
      '3xl': '2.5rem'
    },
    weight: {
      normal: 400,
      medium: 600,             // Heavier weights for clarity
      semibold: 700,
      bold: 800
    },
    lineHeight: 1.4,           // Tighter for efficiency
    letterSpacing: 'normal'
  },

  spacing: {
    unit: 8,
    scale: 'compact',          // Efficient use of space
    containerPadding: 16,
    componentGap: 16
  },

  borderRadius: {
    sm: '4px',                 // Less rounded (more serious)
    md: '6px',
    lg: '8px',
    xl: '12px',
    round: '50%'
  },

  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.12)',
    md: '0 2px 6px rgba(0,0,0,0.16)',
    lg: '0 4px 12px rgba(0,0,0,0.2)',
    none: 'none'
  },

  animations: {
    duration: {
      fast: '100ms',
      normal: '200ms',
      slow: '300ms'
    },
    easing: 'ease-out',
    preference: 'none'         // No distracting animations
  },

  layout: {
    maxWidth: '700px',         // Focused, not wide
    density: 'compact'
  },

  buttons: {
    size: 'large',             // Easy to tap in crisis
    prominence: 'high'         // Clear CTAs
  }
};
```

**Visual Effect:**
- Maximum clarity
- High contrast
- No distractions
- Large, clear action buttons
- Minimal animation (focus on content)

---

#### Stable Theme

**Purpose**: Balanced, growth-focused

```typescript
const stableTheme = {
  name: 'Balance',

  colors: {
    primary: '#2A9D8F',        // Balanced teal
    secondary: '#264653',      // Grounded dark teal
    background: '#F8F9FA',     // Neutral light gray
    surface: '#FFFFFF',
    text: {
      primary: '#212529',
      secondary: '#495057',
      tertiary: '#6C757D'
    },
    accent: '#E76F51',
    success: '#06A77D',
    warning: '#F4A261',
    danger: '#E63946'
  },

  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Lora, serif'
    },
    scale: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem'
    },
    weight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    lineHeight: 1.5,
    letterSpacing: 'normal'
  },

  spacing: {
    unit: 8,
    scale: 'standard',
    containerPadding: 20,
    componentGap: 20
  },

  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px',
    round: '50%'
  },

  shadows: {
    sm: '0 2px 4px rgba(0,0,0,0.06)',
    md: '0 4px 8px rgba(0,0,0,0.1)',
    lg: '0 8px 16px rgba(0,0,0,0.15)',
    none: 'none'
  },

  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '450ms'
    },
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    preference: 'standard'
  },

  layout: {
    maxWidth: '1000px',
    density: 'standard'
  }
};
```

---

### Cultural Themes

#### East African Theme

**Purpose**: Culturally relevant, localized, warm

```typescript
const eastAfricanTheme = {
  name: 'East African Context',

  colors: {
    primary: '#E07A5F',        // Warm terracotta
    secondary: '#F2CC8F',      // Savanna gold
    tertiary: '#81B29A',       // Highland green
    background: '#FFF9F5',
    accent: '#F4A261'
  },

  patterns: {
    style: 'geometric',        // East African textile patterns
    usage: 'subtle',           // Background, not overwhelming
    inspiration: 'kanga'       // Kenyan fabric patterns
  },

  imagery: {
    context: 'local',          // Kenyan landscapes, not generic
    people: 'representative',  // East African representation
    avoidStereotypes: true
  },

  language: {
    primary: 'english',
    secondary: 'swahili',
    mixing: true,              // Code-switching supported
    phrases: {
      // Common Swahili phrases with cultural weight
      'habari': 'greeting',
      'sawa': 'deflection_check',
      'nimechoka': 'exhaustion_flag',
      'tutaona': 'resignation_check'
    }
  },

  resources: {
    hotlines: 'kenya',         // Local crisis resources
    support: 'nairobi',        // Localized support groups
    context: 'east_africa'     // Cultural mental health info
  }
};
```

---

### Urgency Level Themes

How interface urgency adapts to risk:

```typescript
const urgencyLevels = {
  low: {
    alertStyle: 'none',
    tone: 'encouraging',
    crisisVisibility: 'hidden',
    layout: 'exploratory',
    colors: 'primary_theme'
  },

  medium: {
    alertStyle: 'subtle_indicator',  // Small badge or icon
    tone: 'concerned_but_calm',
    crisisVisibility: 'sidebar',     // Available but not prominent
    layout: 'focused',
    colors: 'primary_theme_with_warning_accents'
  },

  high: {
    alertStyle: 'prominent_card',    // Visible card
    tone: 'direct_caring',
    crisisVisibility: 'top_card',    // Front and center
    layout: 'streamlined',           // Hide non-essential
    colors: 'warning_palette'
  },

  critical: {
    alertStyle: 'modal',             // Blocks other content
    tone: 'urgent_compassionate',
    crisisVisibility: 'modal',       // Cannot be dismissed easily
    layout: 'minimal',               // Only critical actions
    colors: 'crisis_theme',          // Red accents, high contrast
    actions: {
      primary: 'connect_counselor',
      secondary: 'call_hotline',
      tertiary: 'safety_resources'
    }
  }
};
```

---

## Layout System

### Adaptive Layout Rules

The layout adapts based on user state and content needs.

#### Priority-Based Layout

```typescript
interface LayoutPriority {
  // Higher number = higher priority (shown first)
  priorities: {
    crisis_modal: 100,              // Blocks everything else
    crisis_resources: 90,           // Top of page
    safety_check: 85,
    dissonance_alert: 80,
    voice_input: 70,                // Primary interaction
    gentle_observations: 60,
    emotion_timeline: 50,
    whats_working: 45,
    progress_celebration: 40,
    personalized_resources: 30,
    navigation: 20,
    settings: 10
  };

  // Visibility rules
  visibility: {
    crisis_resources: (risk) => risk >= 'medium',
    progress_celebration: (trajectory) => trajectory !== 'declining',
    dissonance_timeline: (dissonance) => dissonance > 0.6,
    whats_working: (strategies) => strategies.length > 0,
    gentle_observations: (observations) => observations.length > 0
  };

  // Layout density
  density: {
    crisis: 'compact',       // 16px gaps, minimal padding
    concerned: 'standard',   // 20px gaps, normal padding
    stable: 'comfortable',   // 24px gaps, generous padding
    exploratory: 'spacious'  // 32px gaps, lots of breathing room
  };
}
```

#### Responsive Breakpoints

```typescript
const breakpoints = {
  mobile: {
    max: '768px',
    layout: 'single_column',
    navigation: 'bottom_bar',
    density: 'compact'
  },

  tablet: {
    min: '768px',
    max: '1024px',
    layout: 'flexible',
    navigation: 'sidebar_collapsible',
    density: 'comfortable'
  },

  desktop: {
    min: '1024px',
    layout: 'multi_column',
    navigation: 'sidebar_persistent',
    density: 'spacious'
  }
};
```

#### Mobile-First Layout (Primary)

Since primary use is voice-first on mobile:

```
┌─────────────────────────────────┐
│  [Greeting]                     │  ← Personalized greeting
├─────────────────────────────────┤
│                                 │
│  [VoiceRecorder]                │  ← Primary interaction (large)
│                                 │
├─────────────────────────────────┤
│  [Risk Component]               │  ← If risk detected (adaptive)
├─────────────────────────────────┤
│  [Emotion Timeline]             │  ← Their patterns
├─────────────────────────────────┤
│  [Insights]                     │  ← What's working, observations
├─────────────────────────────────┤
│  [Resources]                    │  ← Personalized resources
├─────────────────────────────────┤
│                                 │
│  [Navigation Bar]               │  ← Bottom (thumb-friendly)
│                                 │
└─────────────────────────────────┘
```

---

## Visual Identity

### Brand

**Name**: Resona

**Meaning**:
- "Resonate" - Your voice resonates with us
- "Persona" - Personal, individual experience
- "Resona" - The interface that resonates with your truth

**Tagline Options**:
1. "Your voice, our guide"
2. "Truth in your voice, care in ours"
3. "Voice-first mental wellness for East Africa"
4. "We hear what you can't say"

**Logo Concept**:
```
    ≈≈≈ ♥

[Voice wave + Heart rhythm merged]
```

- Top: Voice waveform (user's voice)
- Bottom: Heart rate/EKG line (emotional truth)
- Together: The connection between voice and emotion

**Color**: Primary teal (#2A9D8F) - calming, trustworthy, balanced

---

### Typography

#### Primary Font: **Inter**

**Why**:
- Highly readable (designed for screens)
- Excellent at small sizes
- Works well in Swahili (diacritics supported)
- Open source, web-optimized
- Accessible (dyslexia-friendly)

**Usage**:
- UI text
- Buttons
- Navigation
- Short prompts

#### Secondary Font: **Lora**

**Why**:
- Warm, friendly serif
- Great for longer reading
- Pairs well with Inter
- Approachable, not clinical

**Usage**:
- Body text
- Long-form content
- Resources
- Storytelling

#### Type Scale

```typescript
const typography = {
  fontSizes: {
    xs: '0.75rem',    // 12px - Fine print
    sm: '0.875rem',   // 14px - Secondary text
    base: '1rem',     // 16px - Base (accessible)
    lg: '1.125rem',   // 18px - Emphasized
    xl: '1.25rem',    // 20px - Subheadings
    '2xl': '1.5rem',  // 24px - Headings
    '3xl': '1.875rem', // 30px - Page titles
    '4xl': '2.25rem'  // 36px - Hero
  },

  lineHeights: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75
  },

  fontWeights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  }
};
```

---

### Color System

#### Base Palette

```typescript
const colors = {
  // Primary (Balanced Teal)
  primary: {
    50: '#E0F2F1',
    100: '#B2DFDB',
    200: '#80CBC4',
    300: '#4DB6AC',
    400: '#26A69A',
    500: '#2A9D8F',  // Base
    600: '#00897B',
    700: '#00796B',
    800: '#00695C',
    900: '#004D40'
  },

  // Warm (Depression/Encouragement)
  warm: {
    50: '#FFF3E0',
    100: '#FFE0B2',
    200: '#FFCC80',
    300: '#FFB74D',
    400: '#FFA726',
    500: '#E07A5F',  // Base warm
    600: '#FB8C00',
    700: '#F57C00',
    800: '#EF6C00',
    900: '#E65100'
  },

  // Cool (Anxiety/Calm)
  cool: {
    50: '#E1F5FE',
    100: '#B3E5FC',
    200: '#81D4FA',
    300: '#4FC3F7',
    400: '#29B6F6',
    500: '#4A90A4',  // Base cool
    600: '#039BE5',
    700: '#0288D1',
    800: '#0277BD',
    900: '#01579B'
  },

  // Neutrals
  gray: {
    50: '#F8F9FA',
    100: '#F1F3F5',
    200: '#E9ECEF',
    300: '#DEE2E6',
    400: '#CED4DA',
    500: '#ADB5BD',
    600: '#6C757D',
    700: '#495057',
    800: '#343A40',
    900: '#212529'
  },

  // Semantic
  success: '#06A77D',
  warning: '#F4A261',
  danger: '#E63946',
  info: '#4A90A4'
};
```

---

### Iconography

**Style**: Rounded, friendly, voice-centric

**Sources**:
- Heroicons (primary)
- Custom voice/waveform icons
- East African pattern accents (subtle)

**Key Icons**:
- 🎙️ Microphone (voice input)
- 📊 Waveform (voice visualization)
- 💭 Thought bubble (observations)
- 🌱 Seedling (growth/progress)
- 🆘 Lifebuoy (crisis support)
- ♥ Heart (care/connection)

---

## Adaptation Logic

### How the Overnight Builder Decides

```typescript
interface AdaptationDecisionTree {
  // Step 1: Assess current state
  assess: (userData: UserData) => UserState;

  // Step 2: Determine theme
  selectTheme: (userState: UserState) => Theme;

  // Step 3: Choose components
  selectComponents: (userState: UserState) => Component[];

  // Step 4: Set visibility
  setVisibility: (components: Component[], userState: UserState) => VisibilityRules;

  // Step 5: Order layout
  orderLayout: (components: Component[], userState: UserState) => LayoutOrder;

  // Step 6: Apply cultural context
  applyCulturalContext: (config: UIConfig, culturalProfile: CulturalProfile) => UIConfig;

  // Step 7: Generate final config
  generateConfig: () => UIConfig;
}
```

### Decision Matrix

| User State | Theme | Primary Components | Crisis Resources | Tone |
|-----------|-------|-------------------|------------------|------|
| **Anxiety + Low Risk** | Calm (Blue) | VoiceRecorder, EmotionTimeline, WhatsWorking | Hidden | Gentle, spacious |
| **Depression + Medium Risk** | Warm (Orange) | VoiceRecorder, GentleObservations, ProgressCelebration | Sidebar | Encouraging, validating |
| **High Dissonance + High Risk** | Mixed (Concerned) | VoiceRecorder, DissonanceIndicator, CrisisResources | Top Card | Direct, caring |
| **Crisis + Critical Risk** | Crisis (Red) | SafetyCheck, CrisisResources, CounselorConnect | Modal | Urgent, compassionate |
| **Stable + Progressing** | Balance (Teal) | VoiceRecorder, ProgressCelebration, PersonalizedResources | Hidden | Warm, growth-focused |

---

## Voice & Tone

### Personality

Resona speaks like:
- A compassionate companion (not a therapist)
- A trusted friend (not clinical)
- A truth-teller (not sugar-coating)
- A culturally-aware ally (not generic)

### Language Guidelines

#### Do's ✅

- **Validate feelings**: "We hear how heavy things feel right now."
- **Use observations**: "We notice your voice sounds different today."
- **Invite, don't command**: "Would you like to talk about that?"
- **Be specific**: "Your voice calms after breathing exercises" (not "breathing is good")
- **Acknowledge truth**: "Your words say 'fine' but your voice tells a different story."
- **Cultural awareness**: "We know saying 'nimechoka' means more than just tired."

#### Don'ts ❌

- **No toxic positivity**: ❌ "Just think positive!"
- **No commands**: ❌ "You should try meditation."
- **No judgment**: ❌ "You're not trying hard enough."
- **No clinical jargon**: ❌ "You're displaying depressive symptomatology."
- **No false promises**: ❌ "This will fix everything!"
- **No dismissal**: ❌ "Everyone feels that way sometimes."

### Tone by Context

```typescript
const toneGuidelines = {
  low_risk_stable: {
    tone: 'warm_encouraging',
    examples: [
      "Tell us about your day",
      "What's been on your mind?",
      "You've been doing well lately. What's helping?"
    ]
  },

  medium_risk_declining: {
    tone: 'gentle_concerned',
    examples: [
      "We've noticed you sound tired lately. Want to talk about it?",
      "Your voice tells us things have been harder. We're here.",
      "It's okay if you're not okay. Let's talk."
    ]
  },

  high_risk_concealing: {
    tone: 'direct_validating',
    examples: [
      "You said 'fine,' but your voice sounds different. What's really going on?",
      "We hear the gap between your words and your voice. You don't have to hide here.",
      "Your voice tells us you're carrying something heavy. We're concerned."
    ]
  },

  critical_risk: {
    tone: 'urgent_compassionate',
    examples: [
      "We're very concerned about you. Are you thinking about hurting yourself?",
      "You're not alone. Let's get you support right now.",
      "This is serious. We need to make sure you're safe."
    ]
  }
};
```

---

## Accessibility

### Core Commitments

1. **Voice-First** - Primary interaction is voice (overcomes literacy barriers)
2. **WCAG AA Minimum** - All color contrast, font sizes meet standards
3. **Screen Reader Support** - Full semantic HTML, ARIA labels
4. **Offline Capable** - PWA works without internet (East African connectivity)
5. **Low-Data Mode** - Minimal bandwidth usage
6. **Simple Language** - Clear, direct, no jargon

### Accessibility Features

```typescript
const accessibilityFeatures = {
  visual: {
    colorContrast: 'WCAG_AA_minimum',
    fontSize: 'minimum_16px',
    scalability: 'up_to_200%',
    darkMode: 'system_preference',
    reducedMotion: 'respected'
  },

  auditory: {
    voiceInput: 'primary_interaction',
    textAlternative: 'always_available',
    captions: 'for_all_audio'
  },

  cognitive: {
    language: 'simple_clear',
    progressiveDisclosure: 'not_overwhelming',
    consistency: 'predictable_patterns',
    forgiveness: 'undo_always_available'
  },

  motor: {
    touchTargets: 'minimum_44px',
    voiceControl: 'full_navigation',
    keyboard: 'all_features_accessible'
  },

  connectivity: {
    offline: 'PWA_capable',
    lowBandwidth: 'optimized',
    sync: 'when_connection_available'
  }
};
```

---

## Implementation Guide

### Tech Stack Recommendations

```typescript
const techStack = {
  frontend: {
    framework: 'React 18+ with TypeScript',
    stateManagement: 'Zustand (simple) or Redux Toolkit',
    styling: 'Styled Components + Theme Provider',
    components: 'Custom (based on this design system)',
    animation: 'Framer Motion',
    voiceInput: 'Web Audio API + react-audio-voice-recorder'
  },

  designTokens: {
    format: 'Design Tokens (JSON)',
    tool: 'Style Dictionary',
    output: 'CSS Variables, TypeScript types, React theme'
  },

  documentation: {
    components: 'Storybook',
    designSystem: 'Markdown + live examples'
  }
};
```

### File Structure

```
/design-system
  /tokens
    colors.json
    typography.json
    spacing.json
    themes.json

  /components
    /CulturalGreeting
      CulturalGreeting.tsx
      CulturalGreeting.stories.tsx
      CulturalGreeting.test.tsx
      README.md

    /VoiceRecorder
      VoiceRecorder.tsx
      VoiceRecorder.stories.tsx
      VoiceRecorder.test.tsx
      README.md

    [...other components]

  /themes
    anxiety.ts
    depression.ts
    crisis.ts
    stable.ts
    east-african.ts

  /utils
    themeSelector.ts
    componentVisibility.ts
    layoutPriority.ts

  /docs
    principles.md
    components.md
    theming.md
    voice-tone.md
```

### Implementation Priority

**Phase 1: Foundation (Week 1)**
1. Set up design tokens
2. Create theme provider
3. Build base components (Button, Card, Typography)

**Phase 2: Core Components (Week 2)**
1. CulturalGreeting
2. VoiceRecorder
3. EmotionTimeline
4. CrisisResources

**Phase 3: Adaptive Logic (Week 3)**
1. Theme selector based on user state
2. Component visibility rules
3. Layout priority system

**Phase 4: Polish (Week 4)**
1. Animations
2. Accessibility audit
3. Responsive refinement
4. Documentation

---

## Next Steps

### Immediate Actions

1. **Review & Refine**: Get feedback on this design system
2. **Prototype**: Create visual mockups of key screens in different states
3. **Component Specs**: Detail out each component's full prop API
4. **Design Tokens**: Convert color/typography system to JSON tokens
5. **Storybook Setup**: Prepare component documentation environment

### Questions to Resolve

1. **Branding**: Final logo design and tagline?
2. **Localization**: Full Swahili translation strategy?
3. **Illustrations**: Custom illustration style needed?
4. **Animations**: Motion design specifics (micro-interactions)?
5. **Testing**: User testing plan for adaptive interfaces?

---

## Conclusion

This design system is the **DNA** of Resona's adaptive interface. Every overnight build uses these principles, components, and themes to create uniquely personalized experiences.

**Key Principles to Remember:**
1. Emotional intelligence guides visual design
2. Voice truth shapes interface honesty
3. Cultural sensitivity is non-negotiable
4. Risk-responsiveness saves lives
5. Progressive disclosure prevents overwhelm
6. Validation over judgment, always
7. Transparency builds trust

The interface doesn't just display data—it **becomes** the user's companion, evolving with them, reflecting their truth, and adapting to their needs.

---

**Resona Design System v1.0**
*Your voice shapes your interface. Your truth guides your experience.*
