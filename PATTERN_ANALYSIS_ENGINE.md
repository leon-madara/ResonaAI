# Pattern Analysis Engine Architecture

**Phase 2: The Brain Behind Adaptive Interfaces**

> "Detecting the truth in voice, understanding the patterns in pain, finding what works for each individual."

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Analyzers](#core-analyzers)
4. [Database Schema](#database-schema)
5. [Analysis Pipeline](#analysis-pipeline)
6. [Integration Points](#integration-points)
7. [Implementation Plan](#implementation-plan)

---

## Overview

### Purpose

The Pattern Analysis Engine processes voice sessions to extract meaningful patterns that drive interface adaptation:

- **What emotions** are present over time?
- **What dissonance** exists between words and voice?
- **What cultural markers** shape communication?
- **What triggers** cause distress?
- **What coping** strategies actually work?
- **What risk** level is present and trending?
- **What baseline** is normal for this person?

### Data Flow

```
Voice Session
    ↓
[Session Processor]
    ├─→ Audio Analysis (existing emotion detector)
    ├─→ Speech-to-Text (transcription)
    └─→ Timestamp + Metadata
    ↓
[Pattern Analysis Engine] ← WE ARE BUILDING THIS
    ├─→ EmotionalPatternAnalyzer
    ├─→ DissonanceDetector
    ├─→ CulturalContextAnalyzer
    ├─→ TriggerDetector
    ├─→ CopingEffectivenessTracker
    ├─→ RiskAssessmentEngine
    └─→ BaselineTracker
    ↓
[Pattern Aggregator]
    ↓
Anonymized Patterns → Database
    ↓
[Overnight Interface Builder]
    ↓
Personalized UI Config
```

---

## Architecture

### System Components

```typescript
// High-level architecture

interface PatternAnalysisEngine {
  // Core analyzers
  emotionalAnalyzer: EmotionalPatternAnalyzer;
  dissonanceDetector: DissonanceDetector;
  culturalAnalyzer: CulturalContextAnalyzer;
  triggerDetector: TriggerDetector;
  copingTracker: CopingEffectivenessTracker;
  riskAssessor: RiskAssessmentEngine;
  baselineTracker: BaselineTracker;

  // Aggregation
  aggregator: PatternAggregator;

  // Main processing method
  analyzeSession(sessionData: SessionData): Promise<AnalysisResult>;
}
```

### Technology Stack

```typescript
const techStack = {
  language: 'Python 3.10+',  // For ML/NLP tasks

  nlp: {
    sentiment: 'transformers (HuggingFace)',
    textAnalysis: 'spaCy',
    swahili: 'custom models + translation'
  },

  audio: {
    existing: 'librosa, Wav2Vec2',
    microMoments: 'custom signal processing'
  },

  database: {
    primary: 'PostgreSQL 15',
    cache: 'Redis',
    vector: 'Pinecone (for cultural context)'
  },

  ml: {
    framework: 'PyTorch',
    inference: 'ONNX Runtime (optimized)',
    training: 'Custom mental health dataset'
  }
};
```

---

## Core Analyzers

### 1. EmotionalPatternAnalyzer

**Purpose**: Identify emotional patterns over time

**Detects**:
- Primary emotions (what they feel most)
- Temporal patterns (morning better, evening worse)
- Emotional trajectory (improving, declining, stable)
- Emotional variability (consistent vs volatile)

**Implementation**:

```python
# src/pattern_analysis/emotional_pattern_analyzer.py

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class EmotionalPattern:
    """Detected emotional patterns"""
    primary_emotions: List[str]  # Most frequent emotions
    emotion_distribution: Dict[str, float]  # % time in each emotion
    temporal_patterns: Dict[str, str]  # time_of_day -> typical_emotion
    trajectory: str  # 'improving', 'declining', 'stable', 'volatile'
    trajectory_confidence: float
    variability_score: float  # 0-1 (low variability = consistent)
    recent_shift: Optional[str]  # Recent change detected?

class EmotionalPatternAnalyzer:
    """
    Analyzes emotional patterns across sessions
    """

    def __init__(self):
        self.window_days = 30  # Analyze last 30 days
        self.recent_window_days = 7  # Recent trend window

    async def analyze(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> EmotionalPattern:
        """
        Analyze emotional patterns from session history

        Args:
            sessions: List of session data with emotions
            user_id: User identifier

        Returns:
            EmotionalPattern with detected patterns
        """
        if not sessions:
            return self._default_pattern()

        # 1. Calculate emotion distribution
        emotion_dist = self._calculate_emotion_distribution(sessions)

        # 2. Identify primary emotions (>20% of time)
        primary = [
            emotion for emotion, pct in emotion_dist.items()
            if pct > 0.20
        ]

        # 3. Detect temporal patterns (time of day)
        temporal = self._detect_temporal_patterns(sessions)

        # 4. Calculate trajectory (improving/declining/stable)
        trajectory, confidence = self._calculate_trajectory(sessions)

        # 5. Calculate emotional variability
        variability = self._calculate_variability(sessions)

        # 6. Detect recent shifts
        recent_shift = self._detect_recent_shift(sessions)

        return EmotionalPattern(
            primary_emotions=primary,
            emotion_distribution=emotion_dist,
            temporal_patterns=temporal,
            trajectory=trajectory,
            trajectory_confidence=confidence,
            variability_score=variability,
            recent_shift=recent_shift
        )

    def _calculate_emotion_distribution(
        self,
        sessions: List[Dict]
    ) -> Dict[str, float]:
        """Calculate % of time in each emotion"""
        emotion_counts = {}
        total = len(sessions)

        for session in sessions:
            emotion = session.get('voice_emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Convert to percentages
        return {
            emotion: count / total
            for emotion, count in emotion_counts.items()
        }

    def _detect_temporal_patterns(
        self,
        sessions: List[Dict]
    ) -> Dict[str, str]:
        """Detect if certain times of day have typical emotions"""
        time_buckets = {
            'morning': [],    # 5am-11am
            'afternoon': [],  # 11am-5pm
            'evening': [],    # 5pm-10pm
            'night': []       # 10pm-5am
        }

        for session in sessions:
            timestamp = session.get('timestamp')
            if not timestamp:
                continue

            # Parse timestamp
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour

            # Categorize time
            if 5 <= hour < 11:
                bucket = 'morning'
            elif 11 <= hour < 17:
                bucket = 'afternoon'
            elif 17 <= hour < 22:
                bucket = 'evening'
            else:
                bucket = 'night'

            emotion = session.get('voice_emotion', 'neutral')
            time_buckets[bucket].append(emotion)

        # Find most common emotion for each time
        patterns = {}
        for time_period, emotions in time_buckets.items():
            if not emotions:
                continue

            # Most common emotion
            most_common = max(set(emotions), key=emotions.count)
            patterns[time_period] = most_common

        return patterns

    def _calculate_trajectory(
        self,
        sessions: List[Dict]
    ) -> tuple[str, float]:
        """
        Calculate if emotional state is improving, declining, or stable

        Returns: (trajectory, confidence)
        """
        if len(sessions) < 7:
            return 'insufficient_data', 0.0

        # Map emotions to valence scores
        emotion_valence = {
            'happy': 1.0,
            'surprise': 0.5,
            'neutral': 0.0,
            'sad': -0.7,
            'angry': -0.6,
            'fear': -0.8,
            'disgust': -0.5,
            'hopeless': -1.0,
            'resigned': -0.9,
            'numb': -0.8
        }

        # Sort sessions by timestamp
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get('timestamp', '')
        )

        # Get valence scores over time
        valences = [
            emotion_valence.get(s.get('voice_emotion', 'neutral'), 0.0)
            for s in sorted_sessions
        ]

        # Split into first half and second half
        mid = len(valences) // 2
        first_half = valences[:mid]
        second_half = valences[mid:]

        # Calculate averages
        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)

        # Calculate change
        change = avg_second - avg_first

        # Determine trajectory
        if abs(change) < 0.15:
            trajectory = 'stable'
            confidence = 0.8
        elif change > 0.15:
            trajectory = 'improving'
            confidence = min(change / 0.5, 1.0)  # Normalize to 0-1
        else:
            trajectory = 'declining'
            confidence = min(abs(change) / 0.5, 1.0)

        return trajectory, confidence

    def _calculate_variability(
        self,
        sessions: List[Dict]
    ) -> float:
        """
        Calculate emotional variability (consistency)

        Returns: 0 (very consistent) to 1 (highly variable)
        """
        if len(sessions) < 3:
            return 0.5  # Neutral

        emotions = [s.get('voice_emotion', 'neutral') for s in sessions]

        # Calculate entropy (diversity of emotions)
        unique_emotions = set(emotions)
        total = len(emotions)

        entropy = 0.0
        for emotion in unique_emotions:
            count = emotions.count(emotion)
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)

        # Normalize entropy to 0-1
        # Max entropy = log2(num_possible_emotions) ≈ 3 for 8 emotions
        max_entropy = np.log2(len(unique_emotions)) if unique_emotions else 1
        variability = min(entropy / max_entropy, 1.0) if max_entropy > 0 else 0.0

        return variability

    def _detect_recent_shift(
        self,
        sessions: List[Dict]
    ) -> Optional[str]:
        """
        Detect if there's been a recent significant shift

        Returns: Description of shift or None
        """
        if len(sessions) < 14:
            return None

        # Sort by timestamp
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get('timestamp', '')
        )

        # Last 7 days vs previous 7 days
        recent = sorted_sessions[-7:]
        previous = sorted_sessions[-14:-7]

        # Get dominant emotions
        recent_emotions = [s.get('voice_emotion') for s in recent]
        previous_emotions = [s.get('voice_emotion') for s in previous]

        recent_dominant = max(set(recent_emotions), key=recent_emotions.count)
        previous_dominant = max(set(previous_emotions), key=previous_emotions.count)

        # Detect significant shifts
        if recent_dominant != previous_dominant:
            # Check if it's a meaningful shift
            if recent_dominant in ['sad', 'hopeless', 'resigned', 'numb']:
                if previous_dominant in ['happy', 'neutral']:
                    return f"Recent decline: {previous_dominant} → {recent_dominant}"
            elif recent_dominant in ['happy', 'neutral']:
                if previous_dominant in ['sad', 'hopeless', 'resigned']:
                    return f"Recent improvement: {previous_dominant} → {recent_dominant}"

        return None

    def _default_pattern(self) -> EmotionalPattern:
        """Return default pattern for new users"""
        return EmotionalPattern(
            primary_emotions=[],
            emotion_distribution={},
            temporal_patterns={},
            trajectory='insufficient_data',
            trajectory_confidence=0.0,
            variability_score=0.5,
            recent_shift=None
        )
```

---

### 2. DissonanceDetector

**Purpose**: Detect gaps between what users say and how they sound

**Detects**:
- Word-voice dissonance score (0-1)
- Dissonance type (concealment, exaggeration, etc.)
- Truth signal (which to trust: words or voice)
- Concealment patterns over time

**(Already designed in VOICE_TRUTH_DETECTOR_ANALYSIS.md - now implementing)**

```python
# src/pattern_analysis/dissonance_detector.py

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class DissonanceResult:
    """Result of dissonance analysis"""
    stated_emotion: str  # From words
    stated_confidence: float

    voice_emotion: str  # From voice
    voice_confidence: float

    dissonance_score: float  # 0-1
    dissonance_type: str  # concealment, exaggeration, congruent

    truth_signal: str  # What we believe they actually feel
    truth_confidence: float

    risk_level: str
    risk_interpretation: str

    micro_moments: Dict[str, bool]
    baseline_deviation: float

class DissonanceDetector:
    """
    Detects gap between stated emotion (words) and embodied emotion (voice)
    """

    def __init__(self):
        # Emotion valence mapping
        self.emotion_valence = {
            'happy': 'positive',
            'surprise': 'positive',
            'neutral': 'neutral',
            'sad': 'negative',
            'angry': 'negative',
            'fear': 'negative',
            'disgust': 'negative',
            'hopeless': 'negative',
            'resigned': 'negative',
            'numb': 'negative'
        }

    async def detect(
        self,
        transcript: str,
        voice_emotion: str,
        voice_features: Dict,
        audio: np.ndarray,
        sample_rate: int,
        user_baseline: Optional[Dict] = None
    ) -> DissonanceResult:
        """
        Main dissonance detection pipeline
        """
        # 1. Analyze stated emotion from words
        stated_emotion, stated_conf = await self._analyze_verbal_content(
            transcript
        )

        # 2. Get voice valence
        voice_valence = self.emotion_valence.get(voice_emotion, 'neutral')
        voice_conf = voice_features.get('confidence', 0.5)

        # 3. Detect micro-moments (physiological signals)
        micro_moments = self._detect_micro_moments(
            audio,
            sample_rate,
            voice_features
        )

        # 4. Calculate dissonance
        dissonance_score = self._calculate_dissonance(
            stated_emotion,
            voice_valence,
            micro_moments
        )

        # 5. Determine truth signal
        truth_signal, truth_conf = self._determine_truth(
            stated_emotion,
            voice_emotion,
            dissonance_score,
            micro_moments
        )

        # 6. Calculate baseline deviation (if baseline available)
        baseline_dev = 0.0
        if user_baseline:
            baseline_dev = self._calculate_baseline_deviation(
                voice_features,
                user_baseline
            )

        # 7. Assess risk
        risk_level, risk_interp = self._assess_risk(
            dissonance_score,
            truth_signal,
            micro_moments,
            baseline_dev,
            transcript
        )

        # 8. Classify dissonance type
        dissonance_type = self._classify_dissonance(
            stated_emotion,
            voice_valence,
            dissonance_score
        )

        return DissonanceResult(
            stated_emotion=stated_emotion,
            stated_confidence=stated_conf,
            voice_emotion=voice_emotion,
            voice_confidence=voice_conf,
            dissonance_score=dissonance_score,
            dissonance_type=dissonance_type,
            truth_signal=truth_signal,
            truth_confidence=truth_conf,
            risk_level=risk_level,
            risk_interpretation=risk_interp,
            micro_moments=micro_moments,
            baseline_deviation=baseline_dev
        )

    async def _analyze_verbal_content(
        self,
        transcript: str
    ) -> Tuple[str, float]:
        """
        Analyze stated emotion from transcript

        Returns: (emotion_valence, confidence)
        """
        transcript_lower = transcript.lower()

        # Positive phrases
        positive_phrases = [
            "i'm fine", "i'm good", "i'm okay", "feeling better",
            "it's fine", "no problem", "all good", "managing",
            "sawa", "niko sawa", "safi", "poa"  # Swahili
        ]

        # Negative phrases
        negative_phrases = [
            "i'm not okay", "struggling", "difficult", "hard",
            "can't cope", "overwhelming", "hopeless", "tired",
            "nimechoka", "shida", "sijui", "vibaya"  # Swahili
        ]

        # Cultural deflection (says positive but may mean negative)
        deflection_phrases = {
            "nimechoka": 0.6,  # "Tired" but often means giving up
            "sawa": 0.6,       # "Okay" but culturally deflects
            "managing": 0.6,   # Understates difficulty
            "just tired": 0.7  # Often means emotional exhaustion
        }

        # Check for deflection first
        for phrase, confidence in deflection_phrases.items():
            if phrase in transcript_lower:
                return "positive", confidence  # Low confidence positive

        # Check explicit positive
        if any(phrase in transcript_lower for phrase in positive_phrases):
            return "positive", 0.8

        # Check explicit negative
        if any(phrase in transcript_lower for phrase in negative_phrases):
            return "negative", 0.8

        # Neutral default
        return "neutral", 0.5

    def _detect_micro_moments(
        self,
        audio: np.ndarray,
        sr: int,
        voice_features: Dict
    ) -> Dict[str, bool]:
        """
        Detect physiological signals that leak truth
        """
        micro_moments = {
            'voice_tremor': False,
            'voice_crack': False,
            'sigh_detected': False,
            'hesitation': False,
            'flat_prosody': False,
            'harsh_voice': False
        }

        # Tremor (high pitch variability)
        pitch_std = voice_features.get('prosodic', {}).get('pitch_std', 0)
        if pitch_std > 50:
            micro_moments['voice_tremor'] = True

        # Voice crack (large pitch range)
        pitch_range = voice_features.get('prosodic', {}).get('pitch_range', 0)
        if pitch_range > 200:
            micro_moments['voice_crack'] = True

        # Flat prosody (low variability - depression marker)
        if pitch_std < 10:
            micro_moments['flat_prosody'] = True

        # Sighing (high energy variation)
        energy_std = voice_features.get('prosodic', {}).get('energy_std', 0)
        if energy_std > 0.15:
            micro_moments['sigh_detected'] = True

        # Hesitation (high pause ratio)
        pause_ratio = voice_features.get('temporal', {}).get('pause_ratio', 0)
        if pause_ratio > 0.3:
            micro_moments['hesitation'] = True

        # Harsh voice (high zero-crossing)
        zcr = voice_features.get('spectral', {}).get('zero_crossing_rate', 0)
        if zcr > 0.15:
            micro_moments['harsh_voice'] = True

        return micro_moments

    def _calculate_dissonance(
        self,
        stated_emotion: str,
        voice_emotion: str,
        micro_moments: Dict[str, bool]
    ) -> float:
        """
        Calculate word-voice dissonance (0-1)
        """
        # Base dissonance from emotion mismatch
        if stated_emotion == voice_emotion:
            base_dissonance = 0.0
        elif (stated_emotion == 'positive' and voice_emotion == 'negative') or \
             (stated_emotion == 'negative' and voice_emotion == 'positive'):
            base_dissonance = 0.8  # Opposite - high dissonance
        else:
            base_dissonance = 0.4  # Partial mismatch

        # Amplify if micro-moments detected
        micro_count = sum(micro_moments.values())
        micro_amplification = min(micro_count * 0.1, 0.3)

        # Special case: "positive" words + distress signals = concealment
        if stated_emotion == 'positive' and micro_count >= 2:
            base_dissonance = max(base_dissonance, 0.7)

        dissonance = min(base_dissonance + micro_amplification, 1.0)
        return dissonance

    def _determine_truth(
        self,
        stated_emotion: str,
        voice_emotion: str,
        dissonance_score: float,
        micro_moments: Dict[str, bool]
    ) -> Tuple[str, float]:
        """
        Decide what to trust: words or voice?

        Rule: High dissonance → trust voice
        """
        if dissonance_score < 0.3:
            # Low dissonance - both agree
            return voice_emotion, 0.9

        elif dissonance_score < 0.6:
            # Moderate - trust voice slightly more
            return voice_emotion, 0.75

        else:
            # High dissonance - trust voice strongly
            micro_count = sum(micro_moments.values())
            confidence = min(0.6 + (micro_count * 0.1), 0.95)
            return voice_emotion, confidence

    def _calculate_baseline_deviation(
        self,
        current_features: Dict,
        baseline: Dict
    ) -> float:
        """
        How different from user's normal voice?
        """
        deviations = []

        # Pitch deviation
        current_pitch = current_features.get('prosodic', {}).get('pitch_mean', 0)
        baseline_pitch = baseline.get('typical_pitch_mean', 0)
        baseline_pitch_std = baseline.get('typical_pitch_std', 1)

        if baseline_pitch_std > 0:
            pitch_dev = abs(current_pitch - baseline_pitch) / baseline_pitch_std
            deviations.append(min(pitch_dev / 2, 1.0))

        # Energy deviation
        current_energy = current_features.get('prosodic', {}).get('energy_mean', 0)
        baseline_energy = baseline.get('typical_energy_mean', 0)
        baseline_energy_std = baseline.get('typical_energy_std', 1)

        if baseline_energy_std > 0:
            energy_dev = abs(current_energy - baseline_energy) / baseline_energy_std
            deviations.append(min(energy_dev / 2, 1.0))

        # Speech rate deviation
        current_rate = current_features.get('temporal', {}).get('speech_rate', 0)
        baseline_rate = baseline.get('typical_speech_rate', 0)

        if baseline_rate > 0:
            rate_dev = abs(current_rate - baseline_rate) / baseline_rate
            deviations.append(min(rate_dev, 1.0))

        return np.mean(deviations) if deviations else 0.0

    def _assess_risk(
        self,
        dissonance_score: float,
        truth_emotion: str,
        micro_moments: Dict[str, bool],
        baseline_deviation: float,
        transcript: str
    ) -> Tuple[str, str]:
        """
        Assess mental health risk level
        """
        risk_score = 0.0
        risk_factors = []

        # Factor 1: High dissonance (hiding distress)
        if dissonance_score > 0.7:
            risk_score += 0.4
            risk_factors.append("Concealing true emotions")

        # Factor 2: Negative truth emotion
        if truth_emotion in ['sad', 'fear', 'hopeless', 'resigned']:
            risk_score += 0.3
            risk_factors.append(f"Experiencing {truth_emotion}")

        # Factor 3: Micro-moments (physiological distress)
        micro_count = sum(micro_moments.values())
        if micro_count >= 3:
            risk_score += 0.3
            risk_factors.append("Multiple physiological stress markers")

        # Factor 4: Baseline deviation (unusual state)
        if baseline_deviation > 0.6:
            risk_score += 0.2
            risk_factors.append("Voice significantly different from normal")

        # Factor 5: Crisis keywords
        crisis_keywords = [
            'can\'t go on', 'want to die', 'no point', 'end it',
            'better off without me', 'give up', 'nimechoka sana',
            'goodbye', 'done fighting'
        ]
        if any(kw in transcript.lower() for kw in crisis_keywords):
            risk_score += 0.5
            risk_factors.append("CRITICAL: Crisis language detected")

        # Factor 6: Post-decision calm (dangerous pattern)
        if dissonance_score > 0.6 and micro_moments.get('flat_prosody'):
            if any(w in transcript.lower() for w in ['better', 'peace', 'clear', 'decided']):
                risk_score += 0.6
                risk_factors.append("CRITICAL: Possible post-decision calm")

        # Determine risk level
        if risk_score >= 0.8:
            level = "critical"
            interp = "IMMEDIATE RISK: " + "; ".join(risk_factors)
        elif risk_score >= 0.6:
            level = "high"
            interp = "High risk: " + "; ".join(risk_factors)
        elif risk_score >= 0.4:
            level = "medium"
            interp = "Moderate concern: " + "; ".join(risk_factors)
        else:
            level = "low"
            interp = "Low risk: " + ("; ".join(risk_factors) if risk_factors else "No significant concerns")

        return level, interp

    def _classify_dissonance(
        self,
        stated_emotion: str,
        voice_emotion: str,
        dissonance_score: float
    ) -> str:
        """Classify the type of dissonance"""
        if dissonance_score < 0.3:
            return "congruent"

        if stated_emotion == 'positive' and voice_emotion == 'negative':
            return "defensive_concealment"

        if stated_emotion == 'negative' and voice_emotion == 'positive':
            return "exaggeration"

        if stated_emotion == 'neutral' and voice_emotion == 'negative':
            return "minimization"

        return "mixed_signals"
```

---

### 3. CulturalContextAnalyzer

**Purpose**: Detect and interpret cultural communication patterns

**Detects**:
- Language preferences (Swahili, English, code-switching)
- Cultural deflection patterns ("nimechoka", "sawa")
- Stoicism markers
- Code-switching stress indicators

```python
# src/pattern_analysis/cultural_context_analyzer.py

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CulturalContext:
    """Cultural communication patterns"""
    primary_language: str  # 'swahili', 'english', 'mixed'
    code_switching_detected: bool
    code_switching_pattern: Optional[str]  # When/why they switch

    deflection_phrases_used: List[str]  # Cultural deflections detected
    deflection_frequency: float  # How often they deflect

    stoicism_level: str  # 'low', 'medium', 'high'
    stoicism_markers: List[str]

    cultural_stressors: List[str]  # Family duty, economic, etc.

    recommended_approach: str  # How to communicate with them

class CulturalContextAnalyzer:
    """
    Analyzes cultural communication patterns
    """

    def __init__(self):
        # Swahili deflection phrases with cultural meanings
        self.swahili_deflections = {
            'nimechoka': {
                'literal': 'I am tired',
                'cultural': 'Emotionally exhausted, possibly giving up',
                'risk_level': 'high'
            },
            'sawa': {
                'literal': 'Okay/fine',
                'cultural': 'Culturally polite deflection, may not be okay',
                'risk_level': 'medium'
            },
            'sijui': {
                'literal': 'I don\'t know',
                'cultural': 'Overwhelmed, confused, or avoiding',
                'risk_level': 'medium'
            },
            'tutaona': {
                'literal': 'We\'ll see',
                'cultural': 'Fatalistic, giving up control, resignation',
                'risk_level': 'medium'
            }
        }

        # Stoicism markers
        self.stoicism_markers = [
            'managing', 'handling it', 'it\'s fine', 'no big deal',
            'just dealing with it', 'pushing through', 'staying strong'
        ]

    async def analyze(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> CulturalContext:
        """
        Analyze cultural communication patterns
        """
        if not sessions:
            return self._default_context()

        # Extract all transcripts
        transcripts = [
            s.get('transcript', '').lower()
            for s in sessions if s.get('transcript')
        ]

        # 1. Detect language preference
        primary_lang = self._detect_language_preference(transcripts)

        # 2. Detect code-switching
        code_switching, pattern = self._detect_code_switching(transcripts)

        # 3. Find deflection phrases
        deflections_used, deflection_freq = self._detect_deflections(transcripts)

        # 4. Assess stoicism level
        stoicism, markers = self._assess_stoicism(transcripts)

        # 5. Identify cultural stressors
        stressors = self._identify_cultural_stressors(transcripts)

        # 6. Recommend communication approach
        approach = self._recommend_approach(
            primary_lang,
            stoicism,
            deflection_freq
        )

        return CulturalContext(
            primary_language=primary_lang,
            code_switching_detected=code_switching,
            code_switching_pattern=pattern,
            deflection_phrases_used=deflections_used,
            deflection_frequency=deflection_freq,
            stoicism_level=stoicism,
            stoicism_markers=markers,
            cultural_stressors=stressors,
            recommended_approach=approach
        )

    def _detect_language_preference(
        self,
        transcripts: List[str]
    ) -> str:
        """Detect preferred language"""
        swahili_count = 0
        english_count = 0
        mixed_count = 0

        swahili_words = [
            'nimechoka', 'sawa', 'sijui', 'tutaona', 'habari',
            'niko', 'safi', 'poa', 'shida', 'vibaya', 'niambie'
        ]

        for transcript in transcripts:
            has_swahili = any(word in transcript for word in swahili_words)
            has_english = any(word in transcript for word in ['i', 'am', 'the', 'is'])

            if has_swahili and has_english:
                mixed_count += 1
            elif has_swahili:
                swahili_count += 1
            elif has_english:
                english_count += 1

        # Determine primary
        if mixed_count > len(transcripts) * 0.3:
            return 'mixed'
        elif swahili_count > english_count:
            return 'swahili'
        else:
            return 'english'

    def _detect_code_switching(
        self,
        transcripts: List[str]
    ) -> tuple[bool, Optional[str]]:
        """Detect if user code-switches and when"""
        # Simplified: Check if mixing languages
        swahili_words = [
            'nimechoka', 'sawa', 'sijui', 'tutaona', 'habari',
            'niko', 'safi', 'poa', 'shida', 'vibaya'
        ]

        mixed_sessions = 0
        for transcript in transcripts:
            has_swahili = any(word in transcript for word in swahili_words)
            has_english = any(word in transcript for word in ['i', 'am', 'the', 'is'])

            if has_swahili and has_english:
                mixed_sessions += 1

        if mixed_sessions > len(transcripts) * 0.3:
            return True, "Frequently mixes English and Swahili"
        return False, None

    def _detect_deflections(
        self,
        transcripts: List[str]
    ) -> tuple[List[str], float]:
        """Detect cultural deflection phrases"""
        deflections_found = []

        for transcript in transcripts:
            for phrase in self.swahili_deflections.keys():
                if phrase in transcript:
                    deflections_found.append(phrase)

        # Calculate frequency
        frequency = len(deflections_found) / len(transcripts) if transcripts else 0.0

        return list(set(deflections_found)), frequency

    def _assess_stoicism(
        self,
        transcripts: List[str]
    ) -> tuple[str, List[str]]:
        """Assess level of stoicism"""
        markers_found = []

        for transcript in transcripts:
            for marker in self.stoicism_markers:
                if marker in transcript:
                    markers_found.append(marker)

        count = len(markers_found)
        total = len(transcripts)

        if count / total > 0.5:
            level = 'high'
        elif count / total > 0.2:
            level = 'medium'
        else:
            level = 'low'

        return level, list(set(markers_found))

    def _identify_cultural_stressors(
        self,
        transcripts: List[str]
    ) -> List[str]:
        """Identify cultural-specific stressors"""
        stressors = []

        stressor_keywords = {
            'family_duty': ['family expects', 'family pressure', 'let my family down', 'disappoint family'],
            'economic': ['can\'t afford', 'money problems', 'financial', 'unemployment'],
            'social_stigma': ['what will people think', 'shame', 'embarrassment', 'reputation'],
            'gender_expectations': ['should be strong', 'man enough', 'good wife', 'good mother']
        }

        combined = ' '.join(transcripts)

        for stressor, keywords in stressor_keywords.items():
            if any(kw in combined for kw in keywords):
                stressors.append(stressor)

        return stressors

    def _recommend_approach(
        self,
        language: str,
        stoicism: str,
        deflection_freq: float
    ) -> str:
        """Recommend how to communicate with this user"""
        if stoicism == 'high' and deflection_freq > 0.3:
            return "permission_based"  # Give permission to be vulnerable
        elif language == 'swahili' or language == 'mixed':
            return "culturally_adapted_swahili"
        elif stoicism == 'low':
            return "direct_empathetic"
        else:
            return "balanced"

    def _default_context(self) -> CulturalContext:
        """Default context for new users"""
        return CulturalContext(
            primary_language='english',
            code_switching_detected=False,
            code_switching_pattern=None,
            deflection_phrases_used=[],
            deflection_frequency=0.0,
            stoicism_level='medium',
            stoicism_markers=[],
            cultural_stressors=[],
            recommended_approach='balanced'
        )
```

---

## Implementation Continues...

This document outlines the first 3 core analyzers. The remaining analyzers will be:

4. **TriggerDetector** - Identifies what topics/situations cause distress
5. **CopingEffectivenessTracker** - Finds what actually helps each user
6. **RiskAssessmentEngine** - Comprehensive risk scoring
7. **BaselineTracker** - Learns user's "normal" state
8. **MentalHealthProfiler** - Creates comprehensive profile
9. **PatternAggregator** - Combines all analyses

Would you like me to:
1. **Continue implementing the remaining analyzers** (4-9)?
2. **Create the database schema** for storing patterns?
3. **Build the integration pipeline** that connects these to the interface builder?
4. **Start with testing** the implemented analyzers?

Which direction should we go?
