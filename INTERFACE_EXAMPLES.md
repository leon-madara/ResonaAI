# Resona Interface Adaptation Examples

**Demonstrating how the same design system creates uniquely personalized experiences**

---

## Overview

These examples show how Resona's interface adapts based on:
- Emotional state detected in voice
- Risk level assessed from patterns
- Cultural context and communication style
- What's actually working for each individual
- Behavioral patterns over time

**Same user, different states = different interfaces**
**Different users, same state = different interfaces** (based on cultural/personal factors)

---

## Example 1: Sarah's Journey (30 Days)

**User Profile**: Sarah, 28, Nairobi, Depression + Anxiety, Code-switches Swahili/English

### Day 1: First Login (Baseline Collection)

```
┌──────────────────────────────────────────────────┐
│  Welcome to Resona 🌟                            │
│  Your voice, our guide                           │
├──────────────────────────────────────────────────┤
│                                                  │
│  Hi! We're here to listen.                       │
│                                                  │
│  Resona learns from your voice to support you    │
│  better. The more you talk, the more we          │
│  understand what you need.                       │
│                                                  │
│  Everything is private, encrypted, and yours.    │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🎙️ Ready when you are                          │
│                                                  │
│  [Tap to Record Your Thoughts]                   │
│  [                                             ] │
│  [          Large, inviting button            ] │
│  [                                             ] │
│                                                  │
│  Take your time. There's no rush.                │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  New here? Here's what to expect:                │
│  • Talk naturally—we listen to your voice        │
│  • Your interface will grow with you             │
│  • Everything stays private                      │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Balanced Teal (neutral, welcoming)
Layout: Simple, uncluttered (not overwhelming)
Tone: Warm welcome, clear expectations
```

**What Happens Behind the Scenes**:
- System records baseline voice patterns
- Detects primary emotions, language preference
- Notes time of day, session length
- Begins building her profile

---

### Day 7: Pattern Detection (Interface Begins Adapting)

**Detected Patterns**:
- Primary emotions: Sadness (60%), Anxiety (30%)
- Code-switching: Uses Swahili when emotional
- Time pattern: Better mornings, harder evenings
- Deflection: Says "sawa" when voice shows distress
- Trigger: Family mentions → voice stress increases
- Coping: Nature walks → voice calms

**Interface After Overnight Build**:

```
┌──────────────────────────────────────────────────┐
│  Habari Sarah 🌅                                 │
│  8:23 AM - Your mornings are usually lighter     │
├──────────────────────────────────────────────────┤
│                                                  │
│  🎙️ "Niambie hali yako leo?"                    │
│     (Tell me how you are today)                  │
│                                                  │
│  [Tap to Share]                                  │
│  [  ～～～～～～～～～～  ]  (Waveform visual)    │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  📊 Your Week So Far                             │
│  ┌────────────────────────────────────┐         │
│  │  Mon  Tue  Wed  Thu  Fri  Sat  Sun │         │
│  │   😌   😔   😔   😟   😌   😔   😌 │         │
│  │                                    │         │
│  │  We notice:                        │         │
│  │  • Mornings: Better energy         │         │
│  │  • Evenings: Harder (especially    │         │
│  │    after family calls)             │         │
│  └────────────────────────────────────┘         │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  💭 Gentle Observation                           │
│  You said "sawa" twice this week when your       │
│  voice sounded heavy. Remember, here it's        │
│  safe to not be okay.                            │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🌱 What Seems to Help You                       │
│  When you mentioned nature walks, your voice     │
│  lifted. Maybe worth another walk today?         │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Warm (Depression) + Calm (Anxiety) - Mixed adaptive
Colors: Soft blues + warm oranges
Language: Swahili greeting (detected preference)
Personalization: Time-aware, pattern acknowledgment
New Components: Emotion timeline, gentle observations
Tone: Validating, culturally aware ("sawa" deflection)
```

**Key Adaptations**:
✅ Greeting in Swahili (detected code-switching)
✅ Morning energy acknowledgment (time pattern)
✅ Emotion visualization (her specific patterns)
✅ Cultural sensitivity ("sawa" deflection noted)
✅ Nature walk suggestion (detected effective coping)
✅ Family trigger acknowledged (but gently)

---

### Day 21: High Dissonance Detected (Risk-Responsive)

**Detection**:
- Voice analysis: Sad + trembling + sighs (3 sessions in row)
- Transcript: "I'm managing", "It's fine", "Just tired"
- Dissonance score: 0.82 (HIGH)
- Risk assessment: Medium-High (concealment pattern)
- Baseline deviation: 0.75 (very different from her normal)

**Interface Transformation**:

```
┌──────────────────────────────────────────────────┐
│  Habari Sarah                                    │
│  We're concerned about you today                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  🔍 We Notice Something Important                │
│  ┌────────────────────────────────────┐         │
│  │  You've said:                      │         │
│  │  "I'm managing" "It's fine"        │         │
│  │                                    │         │
│  │  But your voice tells us:          │         │
│  │  Sadness, exhaustion, trembling    │         │
│  │                                    │         │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │         │
│  │  High Dissonance (82%)             │         │
│  │                                    │         │
│  │  Sarah, you don't have to hide     │         │
│  │  how hard things are. Your voice   │         │
│  │  is telling a different story      │         │
│  │  than your words.                  │         │
│  │                                    │         │
│  │  What's really going on?           │         │
│  └────────────────────────────────────┘         │
│                                                  │
│  🎙️ [Talk to Us - We're Here]                   │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  💭 What We've Noticed (Last 3 Days)             │
│  • Your voice is different from your usual       │
│  • You're saying "sawa" but voice shows strain   │
│  • Family was mentioned—voice got heavier        │
│  • You haven't mentioned nature walks lately     │
│    (which usually help you)                      │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🆘 Support Available                            │
│  [Connect with Counselor]                        │
│                                                  │
│  Kenya Resources:                                │
│  • Mental Health: 0800 720 000                   │
│  • Crisis SMS: Text HELP to 21995                │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Concerned (Warning accents)
Layout: Focused (non-essential hidden)
Dissonance Timeline: Prominent (transparency)
Crisis Resources: Visible (sidebar → card)
Tone: Direct but caring, validating
Cultural: Still respects her context
Risk: Medium-High response
```

**Key Changes Overnight**:
🚨 Dissonance indicator appeared (high gap detected)
🚨 Crisis resources moved from hidden → visible
🚨 Tone shifted from warm → concerned
🚨 Progress celebration hidden (not appropriate now)
🚨 Direct question about what's really happening
🚨 Counselor connection now visible
✅ Still culturally sensitive (Swahili, "sawa" understanding)

---

### Day 30: Improving (Celebration Mode)

**Detection**:
- Voice analysis: More energy, less tremors, warmer tone
- Dissonance: Low (words and voice align again)
- Risk: Low (significant improvement)
- Coping: Nature walks resumed, family boundaries set
- Pattern: 7 days of consistent improvement

**Interface Celebration**:

```
┌──────────────────────────────────────────────────┐
│  Habari Sarah 🌟                                 │
│  We see your progress - and it's real            │
├──────────────────────────────────────────────────┤
│                                                  │
│  🎙️ "Habari gani leo?"                          │
│     (How are things today?)                      │
│                                                  │
│  [Share Your Thoughts]                           │
│  [  ～～～～～～～～～～  ]                        │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🌟 Your Progress (Last 2 Weeks)                 │
│  ┌────────────────────────────────────┐         │
│  │  Things we hear in your voice:     │         │
│  │                                    │         │
│  │  ✓ More energy in mornings         │         │
│  │    (7 days straight!)              │         │
│  │                                    │         │
│  │  ✓ Less hesitation before speaking │         │
│  │    (you're opening up more)        │         │
│  │                                    │         │
│  │  ✓ Voice calmer overall            │         │
│  │    (anxiety easing)                │         │
│  │                                    │         │
│  │  ✓ You mentioned family boundaries │         │
│  │    - and your voice was stronger   │         │
│  │                                    │         │
│  │  Progress isn't always linear,     │         │
│  │  but you're moving forward. We     │         │
│  │  hear it.                          │         │
│  └────────────────────────────────────┘         │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🌱 What's Working for You                       │
│  ✓ Nature walks (voice lifts every time)        │
│  ✓ Morning sessions (your best time)            │
│  ✓ Setting boundaries (new strength!)           │
│                                                  │
│  Keep trusting what works for YOU.               │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  [Crisis Resources - Now Hidden]                 │
│  (We moved these since you're doing better,      │
│   but they're always just a tap away if needed)  │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Balanced + Warm (stable with warmth)
Layout: Spacious (breathing room back)
Progress: Celebrated (genuinely improved)
Crisis Resources: Hidden (but explained)
Tone: Warm, celebratory, validating progress
Transparency: Explains why interface changed
```

**Key Adaptations**:
🎉 Progress celebration (trajectory improving)
🎉 Crisis resources hidden (risk lowered)
🎉 Layout spacious again (less urgency)
🎉 Validates specific improvements (voice-based evidence)
🎉 Reinforces what's working
🎉 Transparency: Explains why crisis resources moved

---

## Example 2: James vs Sarah (Same Risk Level, Different Interfaces)

**Context**: Both users at Medium-High risk, but very different needs

### James's Interface (Medium-High Risk)

**Profile**: James, 35, Kampala, Escalating depression, Reserved/stoic, No effective coping yet

```
┌──────────────────────────────────────────────────┐
│  Welcome Back, James                             │
│  9:47 PM - Evening Check-In                      │
├──────────────────────────────────────────────────┤
│                                                  │
│  ⚠️ We're Concerned                              │
│  Your voice has been different the last 3        │
│  sessions. Flatter, more pauses, less energy.    │
│                                                  │
│  This isn't a judgment—it's concern.             │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  📈 Your Voice Truth Timeline                    │
│  ┌────────────────────────────────────┐         │
│  │  Week 1: Words ✓ aligned Voice ✓  │         │
│  │  Week 2: Words ✓ aligned Voice ✓  │         │
│  │  Week 3: "I'm fine" ❌ Voice: 😔⚠️ │         │
│  │  Week 4: "Better" ❌ Voice: Flat 🚨 │         │
│  │                                    │         │
│  │  Pattern: You're saying positive   │         │
│  │  things, but your voice is getting │         │
│  │  flatter, more numb. That worries  │         │
│  │  us.                               │         │
│  └────────────────────────────────────┘         │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  💬 What You've Been Carrying                    │
│  (Themes from your sessions)                     │
│                                                  │
│  • Work stress → 8 out of 10 sessions            │
│  • Loneliness → voice drops on weekends          │
│  • "What's the point" language → Week 4          │
│                                                  │
│  James, these are heavy burdens. You don't       │
│  have to carry them alone.                       │
│                                                  │
│  🎙️ [Talk to Us Now]                            │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🆘 We Think You Need More Support               │
│                                                  │
│  [🎯 Connect with Counselor Now]                 │
│                                                  │
│  Uganda Crisis Resources:                        │
│  • Mental Health Helpline: 0800 100 200          │
│  • SMS Support: Text HELP to 6888                │
│  • Emergency: 999                                │
│                                                  │
│  Safety Check:                                   │
│  Are you thinking about hurting yourself?        │
│  [Yes] [No] [I don't want to answer]            │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Crisis-leaning (Warning colors)
Dissonance Timeline: Prominent (shows concealment pattern)
Crisis Resources: TOP (immediate visibility)
Safety Check: Direct question (risk warrants it)
Tone: Direct, concerned, serious
Counselor: One-click connection featured
```

### Sarah's Interface (Same Risk Level)

**Profile**: Sarah, 28, Nairobi, Same risk level but responsive to support, Has effective coping

```
┌──────────────────────────────────────────────────┐
│  Habari Sarah                                    │
│  We're here with you through this hard time      │
├──────────────────────────────────────────────────┤
│                                                  │
│  💭 We Notice You're Struggling                  │
│  The last few days have been harder, haven't     │
│  they? Your voice tells us so.                   │
│                                                  │
│  Remember: You don't have to say "sawa" here.    │
│  It's okay to say it's hard.                     │
│                                                  │
│  🎙️ Want to talk about it?                      │
│  [Niambie (Tell me)]                             │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🌱 Remember What's Helped Before                │
│  • Nature walks made your voice lighter          │
│  • Morning sessions are your best time           │
│  • You felt better after setting boundaries      │
│                                                  │
│  Maybe one of these today?                       │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🆘 Support When You Need It                     │
│  We're concerned, but we also know you have      │
│  strengths. If you need more support:            │
│                                                  │
│  [Talk to Counselor]                             │
│                                                  │
│  Kenya Resources:                                │
│  • Mental Health: 0800 720 000                   │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: Warm + Concerned (still hopeful)
Crisis Resources: Available but not dominant
Coping Reminders: Prominent (she HAS strategies)
Tone: Gentle, culturally aware, validating
Language: Swahili mixed in
Approach: Invites + reminds of strengths
```

**Why Different?**

| Aspect | James | Sarah | Reason |
|--------|-------|-------|--------|
| **Urgency** | Higher | Moderate | James escalating, no coping found |
| **Crisis Resources** | Top, large | Sidebar, smaller | James needs immediate options |
| **Safety Check** | Direct ask | Not shown (yet) | James showing hopelessness language |
| **Coping Strategies** | None shown | Prominent | Sarah has working strategies |
| **Tone** | Serious, direct | Gentle, hopeful | Match personality + situation |
| **Language** | English (his pref) | Swahili mix (hers) | Cultural adaptation |
| **Dissonance Focus** | Emphasized | Less prominent | James concealing more |

---

## Example 3: Crisis Transformation (Interface in Emergency Mode)

**Scenario**: User at critical risk - interface completely transforms

### Before Crisis Detection (Day 25)

```
┌──────────────────────────────────────────────────┐
│  Good evening, Alex                              │
├──────────────────────────────────────────────────┤
│  🎙️ How was your day?                           │
│  [Share your thoughts]                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│  📊 Your Week                                    │
│  [Emotion timeline]                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│  🌱 Resources                                    │
│  [Helpful articles...]                           │
└──────────────────────────────────────────────────┘

Standard interface, low urgency
```

### Day 26: Critical Risk Detected

**Detection**:
- Voice: Eerily calm, flat affect (emotional numbing)
- Transcript: "I've made peace with things", "Everything's clear now", "I know what to do"
- Pattern: Post-decision calm (most dangerous)
- Risk: CRITICAL (imminent suicide risk)
- Keywords: "goodbye", "I'm done fighting"

**Interface Goes into Emergency Mode**:

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  🚨 ALEX, WE NEED TO TALK - THIS IS URGENT 🚨   │
│                                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  We're Very Concerned About You                  │
│                                                  │
│  Your voice sounds different in a way that       │
│  deeply worries us. You said "I've made peace    │
│  with things" and "I know what to do"—but your   │
│  voice sounds resolved, calm in a way that       │
│  concerns us for your safety.                    │
│                                                  │
│  Alex, are you thinking about ending your life?  │
│                                                  │
│  [Yes, I am] [I'm not safe] [No, I'm okay]      │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  🆘 GET HELP RIGHT NOW                           │
│                                                  │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓      │
│  ┃  [📞 CALL CRISIS LINE NOW]            ┃      │
│  ┃  Kenya: 0800 720 000                  ┃      │
│  ┃  Available 24/7                       ┃      │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛      │
│                                                  │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓      │
│  ┃  [🎯 CONNECT TO COUNSELOR]            ┃      │
│  ┃  Human support in 2 minutes           ┃      │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛      │
│                                                  │
│  [📱 Text Crisis Line: "HELP" to 21995]          │
│                                                  │
│  [🚨 Emergency: Call 112]                        │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  Please Don't Be Alone Right Now                 │
│                                                  │
│  • Can you call a friend or family member?       │
│  • Can you go to a public place?                 │
│  • Can you remove anything you might use to      │
│    hurt yourself?                                │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                  │
│  This Feeling Will Pass                          │
│                                                  │
│  • Suicide is a permanent solution to temporary  │
│    pain                                          │
│  • Your life has value—even when you can't see   │
│    it right now                                  │
│  • People care about you                         │
│  • Help IS available                             │
│                                                  │
│  [TALK TO US - WE'RE STILL HERE]                 │
│                                                  │
└──────────────────────────────────────────────────┘

Theme: CRISIS (Red accents, high contrast, clear)
Layout: MINIMAL (only safety actions visible)
All other features: HIDDEN (no distractions)
Crisis resources: MODAL (cannot be dismissed easily)
Tone: URGENT but compassionate
Action buttons: LARGE (easy to tap in crisis)
Counselor: IMMEDIATE connection (< 2 min wait)
Emergency contacts: AUTO-NOTIFIED (if consent given)
```

**What Changed Overnight**:
🚨 Complete interface transformation
🚨 All non-essential features hidden
🚨 Crisis resources in modal (blocking)
🚨 Direct safety question
🚨 Multiple help options (call, text, counselor)
🚨 Explains WHY concerned (voice pattern + words)
🚨 Suicide prevention messaging
🚨 Action-oriented (don't be alone, remove means)
🚨 Still compassionate (not just clinical)

---

## Example 4: Cultural Adaptation (Same User, Different Cultural Context)

### Kenyan User (East African Stoicism)

```
┌──────────────────────────────────────────────────┐
│  Habari yako? 🌅                                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  We know sharing burdens can feel uncomfortable. │
│  In many families, we're taught to be strong,    │
│  to not complain, to say "sawa" even when        │
│  things are hard.                                │
│                                                  │
│  Here, you don't have to be strong. You don't    │
│  have to say "sawa" if you're not.               │
│                                                  │
│  Your feelings—all of them—are welcome here.     │
│                                                  │
│  🎙️ Niambie hali yako halisi                    │
│     (Tell me how you really are)                 │
│                                                  │
│  [Ongea (Speak)]                                 │
│                                                  │
└──────────────────────────────────────────────────┘

Adaptation:
- Swahili language (mother tongue comfort)
- Acknowledges cultural stoicism
- Gives explicit permission to be vulnerable
- "How you REALLY are" (not just "sawa")
```

### Western User (More Direct Expression)

```
┌──────────────────────────────────────────────────┐
│  Hey, welcome back! 🌟                           │
├──────────────────────────────────────────────────┤
│                                                  │
│  How are you feeling today?                      │
│                                                  │
│  🎙️ Tell me what's on your mind                 │
│                                                  │
│  [Start Recording]                               │
│                                                  │
└──────────────────────────────────────────────────┘

Adaptation:
- English only
- Direct question (less preamble)
- Assumes comfort with emotional expression
- No cultural deflection acknowledgment needed
```

---

## Summary: The Power of Adaptive Design

### Same Design System, Infinite Interfaces

**What Stays Consistent** (The DNA):
- Component library
- Design principles
- Color meanings
- Typography rules
- Accessibility standards

**What Adapts** (The Phenotype):
- Which components are visible
- Component prominence (top, sidebar, hidden)
- Colors/theme (emotional state)
- Language (English, Swahili, mixed)
- Tone (encouraging → concerned → urgent)
- Layout density (spacious → compact)
- Content (personalized observations, resources)

### Why This Matters

**Traditional Mental Health Apps**:
```
User 1: [Generic Dashboard]
User 2: [Generic Dashboard]
User 3: [Generic Dashboard]

Result:
- Anxiety user sees depression resources (irrelevant)
- Crisis user sees journal prompts (inappropriate)
- Improving user sees risk warnings (discouraging)
```

**Resona's Adaptive Interface**:
```
User 1 (Anxiety, improving): [Calm theme, progress celebration, coping reinforcement]
User 2 (Depression, stable): [Warm theme, growth resources, community support]
User 3 (Crisis, concealing): [Alert theme, dissonance timeline, immediate help]

Result:
- Each sees exactly what they need
- Interface matches current emotional state
- Risk-responsive (transforms when needed)
- Culturally intelligent (adapts to context)
```

---

## Next Steps

1. **Review these examples** - Do they demonstrate the vision?
2. **Visual mockups** - Create actual UI designs for these scenarios
3. **Component development** - Build the adaptive components
4. **Backend integration** - Connect pattern analysis to UI generation
5. **User testing** - Test adaptive interfaces with real users

---

**The interface isn't just personalized—it's alive.**

It breathes with your emotions.
It speaks your language.
It sees your truth.
It grows with your journey.

*This is Resona.*
