# Voice Truth Detector: Design Analysis & Improvement Roadmap

## Executive Summary

**Current State**: ResonaAI has a solid foundation for basic voice emotion detection (7 emotions) using Wav2Vec2 + Random Forest, but **critically lacks** the core "truth detection" capability described in the framework.

**The Gap**: The system detects *what emotion is in the voice* but **does not detect the gap between what people SAY and how they SOUND** - which is the revolutionary insight.

**Priority**: Transform from "emotion classifier" → "truth detector" by implementing dissonance analysis.

---

## 1. Current Implementation: Strengths & Limitations

### ✅ What Works Well

| Component | Current Implementation | Why It's Good |
|-----------|----------------------|---------------|
| **Audio Processing** | Noise reduction, normalization, silence trimming | Clean input data |
| **Feature Extraction** | MFCC, spectral, prosodic, temporal, statistical features | Comprehensive acoustic analysis |
| **Deep Learning** | Wav2Vec2 (768-dim embeddings) | State-of-the-art speech representations |
| **Ensemble Approach** | Random Forest on combined features | Robust predictions |
| **Real-time Streaming** | WebSocket support with chunked processing | Live analysis capability |
| **East African Focus** | Accent adaptation in speech service | Cultural awareness |

### ❌ Critical Missing Pieces (The "Truth Detector" Gap)

| What's Missing | Why It Matters | Impact |
|----------------|----------------|---------|
| **1. Word-Voice Dissonance Detection** | Can't catch "I'm fine" said with shaky voice | **Misses hidden distress** |
| **2. Speech-to-Text Integration** | No text to compare against voice | **Can't analyze what they SAY vs how they SOUND** |
| **3. Personal Baseline Tracking** | No user-specific normal state | **Can't detect "different from their usual"** |
| **4. Micro-Moment Detection** | No sighs, tremors, voice cracks, pauses | **Misses physiological leakage** |
| **5. Cultural Deflection Patterns** | No "Nimechoka", "Sawa", stoicism detection | **Misses culturally-coded distress** |
| **6. Risk Scoring from Dissonance** | Only emotion labels, no risk assessment | **Can't flag suicide risk from "performing wellness"** |
| **7. Emotional Archaeology Layers** | Single-level analysis | **Misses depth of hidden truth** |

---

## 2. The Fundamental Architecture Problem

### Current Flow (Emotion Detection Only)
```
Audio Input
    ↓
[Audio Preprocessing]
    ↓
[Feature Extraction]
    ↓
[Emotion Classification]
    ↓
Output: "User is SAD (85% confidence)"
```

**Problem**: This tells us the emotion in the voice, but not whether it matches what they're saying.

### Required Flow (Truth Detection)
```
Audio Input
    ↓
    ├─→ [Audio Features] → Voice Emotion
    │
    └─→ [Speech-to-Text] → Transcribed Words
                              ↓
                         [Content Analysis] → Stated Emotion

Both signals converge:
    ↓
[Dissonance Detector]
    ├─ Compare: Voice Emotion vs Stated Emotion
    ├─ Detect: Micro-moments (sighs, tremors, breaks)
    ├─ Check: Cultural deflection patterns
    └─ Compare to: Personal baseline
    ↓
[Truth Signal]
    ├─ What they actually feel (voice)
    ├─ What they claim to feel (words)
    ├─ The GAP (dissonance score)
    └─ Risk level (hidden distress)
    ↓
Output:
    "User SAID: 'I'm fine' (positive)
     User SOUNDS: Sad + trembling (negative)
     Dissonance: HIGH (0.85)
     Truth: Hiding distress
     Risk: Medium-High (defensive concealment)"
```

---

## 3. Detailed Design Improvements

### 🎯 Priority 1: Word-Voice Dissonance Detection (CRITICAL)

**What**: Build the core "lie detector" that compares verbal content to vocal emotion.

**Technical Implementation**:

```python
# New file: src/dissonance_detector.py

from typing import Dict, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class DissonanceResult:
    """Result of word-voice dissonance analysis"""
    stated_emotion: str              # From words: "positive", "negative", "neutral"
    stated_confidence: float         # Confidence in text analysis

    voice_emotion: str               # From voice: "sad", "happy", "angry", etc.
    voice_confidence: float          # Confidence in voice emotion

    dissonance_score: float          # 0.0 (aligned) to 1.0 (high mismatch)
    dissonance_type: str            # "concealment", "exaggeration", "congruent"

    truth_signal: str               # What we believe they actually feel
    truth_confidence: float         # Confidence in the truth signal

    risk_level: str                 # "low", "medium", "high", "critical"
    risk_interpretation: str        # Human-readable risk explanation

    micro_moments: Dict[str, bool]  # Detected physiological leakage
    baseline_deviation: float       # How different from their normal (0-1)


class DissonanceDetector:
    """
    Detects the gap between what people SAY and how they SOUND
    """

    def __init__(self):
        # Emotion valence mapping (positive/negative/neutral)
        self.emotion_valence = {
            'happy': 'positive',
            'surprise': 'positive',
            'neutral': 'neutral',
            'sad': 'negative',
            'angry': 'negative',
            'fear': 'negative',
            'disgust': 'negative'
        }

        # Risk interpretation based on dissonance patterns
        self.risk_patterns = {
            ('positive', 'negative'): 'defensive_concealment',  # "I'm fine" but sounds sad
            ('positive', 'neutral_flat'): 'emotional_numbing',   # "Happy" but voice is dead
            ('neutral', 'negative_intense'): 'suppressed_crisis', # "Just tired" but severe distress
            ('negative', 'negative_resolved'): 'post_decision_calm' # Suicidal relief
        }

    async def detect_dissonance(
        self,
        transcript: str,
        voice_emotion: str,
        voice_features: Dict,
        user_baseline: Optional[Dict] = None
    ) -> DissonanceResult:
        """
        Main dissonance detection pipeline

        Args:
            transcript: What the user said (text)
            voice_emotion: Detected emotion from voice
            voice_features: Extracted audio features
            user_baseline: User's personal baseline (if available)

        Returns:
            DissonanceResult with truth signal and risk assessment
        """

        # Step 1: Analyze what they SAID
        stated_emotion, stated_conf = await self._analyze_verbal_content(transcript)

        # Step 2: Analyze how they SOUND
        voice_valence = self.emotion_valence[voice_emotion]
        voice_conf = voice_features.get('confidence', 0.5)

        # Step 3: Detect micro-moments (physiological leakage)
        micro_moments = self._detect_micro_moments(voice_features)

        # Step 4: Calculate dissonance
        dissonance_score = self._calculate_dissonance(
            stated_emotion,
            voice_valence,
            micro_moments
        )

        # Step 5: Determine truth signal (which to trust more)
        truth_signal, truth_conf = self._determine_truth(
            stated_emotion,
            voice_emotion,
            dissonance_score,
            micro_moments
        )

        # Step 6: Calculate baseline deviation (if available)
        baseline_dev = 0.0
        if user_baseline:
            baseline_dev = self._calculate_baseline_deviation(
                voice_features,
                user_baseline
            )

        # Step 7: Assess risk
        risk_level, risk_interpretation = self._assess_risk(
            dissonance_score,
            truth_signal,
            micro_moments,
            baseline_dev,
            transcript
        )

        # Step 8: Classify dissonance type
        dissonance_type = self._classify_dissonance_type(
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
            risk_interpretation=risk_interpretation,
            micro_moments=micro_moments,
            baseline_deviation=baseline_dev
        )

    async def _analyze_verbal_content(self, transcript: str) -> Tuple[str, float]:
        """
        Analyze what the user SAID to infer stated emotion

        Uses sentiment analysis + cultural deflection detection
        """
        # Positive indicators
        positive_phrases = [
            "i'm fine", "i'm good", "i'm okay", "feeling better",
            "it's fine", "no problem", "all good", "managing",
            "sawa", "niko sawa", "safi"  # Swahili positives
        ]

        # Negative indicators
        negative_phrases = [
            "i'm not okay", "struggling", "difficult", "hard",
            "can't cope", "overwhelming", "hopeless", "tired",
            "nimechoka", "shida", "sijui"  # Swahili negatives
        ]

        # Cultural deflection (says positive but culturally means negative)
        deflection_phrases = {
            "nimechoka": "exhausted/giving up",  # Not just "tired"
            "sawa": "okay (but may not be)",     # Common deflection
            "managing": "barely holding on",      # Understated distress
            "just tired": "emotionally exhausted"
        }

        transcript_lower = transcript.lower()

        # Check for deflection first
        for phrase, meaning in deflection_phrases.items():
            if phrase in transcript_lower:
                # This is a deflection - stated positive, implied negative
                return "positive", 0.6  # Low confidence positive

        # Check positive
        if any(phrase in transcript_lower for phrase in positive_phrases):
            return "positive", 0.8

        # Check negative
        if any(phrase in transcript_lower for phrase in negative_phrases):
            return "negative", 0.8

        # Neutral default
        return "neutral", 0.5

    def _detect_micro_moments(self, voice_features: Dict) -> Dict[str, bool]:
        """
        Detect physiological leakage: sighs, tremors, voice cracks, pauses

        These are the "soul signals" that bypass conscious control
        """
        micro_moments = {
            'voice_tremor': False,      # Trembling voice (fear/crying)
            'voice_crack': False,       # Pitch breaks (emotion leaking)
            'sigh_detected': False,     # Sighing (burden, resignation)
            'hesitation': False,        # Pauses before speaking (searching for "safe" answer)
            'breath_catch': False,      # Irregular breathing (suppressing emotion)
            'flat_prosody': False,      # Dead voice (depression, numbing)
            'harsh_voice': False        # Tense voice (anger, stress)
        }

        # Tremor detection (high pitch variability)
        pitch_std = voice_features.get('prosodic', {}).get('pitch_std', 0)
        if pitch_std > 50:  # High variability suggests tremor
            micro_moments['voice_tremor'] = True

        # Voice crack detection (pitch discontinuities)
        pitch_range = voice_features.get('prosodic', {}).get('pitch_range', 0)
        if pitch_range > 200:  # Large jumps suggest breaks
            micro_moments['voice_crack'] = True

        # Flat prosody (low variability - depression marker)
        if pitch_std < 10:  # Very low variability
            micro_moments['flat_prosody'] = True

        # Energy analysis for sighs/breath patterns
        energy_std = voice_features.get('prosodic', {}).get('energy_std', 0)
        if energy_std > 0.15:  # High energy variation suggests sighing
            micro_moments['sigh_detected'] = True

        # Pause detection (high pause ratio)
        pause_ratio = voice_features.get('temporal', {}).get('pause_ratio', 0)
        if pause_ratio > 0.3:  # More than 30% pauses
            micro_moments['hesitation'] = True

        # Harsh voice (spectral features)
        zero_crossing = voice_features.get('spectral', {}).get('zero_crossing_rate', 0)
        if zero_crossing > 0.15:  # High zero-crossing suggests harsh voice
            micro_moments['harsh_voice'] = True

        return micro_moments

    def _calculate_dissonance(
        self,
        stated_emotion: str,
        voice_emotion: str,
        micro_moments: Dict[str, bool]
    ) -> float:
        """
        Calculate how much the words and voice DISAGREE

        Returns: 0.0 (perfectly aligned) to 1.0 (maximum mismatch)
        """
        # Base dissonance from emotion mismatch
        if stated_emotion == voice_emotion:
            base_dissonance = 0.0  # Aligned
        elif (stated_emotion == 'positive' and voice_emotion == 'negative') or \
             (stated_emotion == 'negative' and voice_emotion == 'positive'):
            base_dissonance = 0.8  # Opposite emotions - high dissonance
        else:
            base_dissonance = 0.4  # Partial mismatch

        # Amplify dissonance if micro-moments detected
        micro_moment_count = sum(micro_moments.values())
        micro_amplification = min(micro_moment_count * 0.1, 0.3)

        # Special case: "positive" words + distress signals = concealment
        if stated_emotion == 'positive' and micro_moment_count >= 2:
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

        Rule: When dissonance is high, TRUST THE VOICE, not the words
        """
        if dissonance_score < 0.3:
            # Low dissonance - both agree, trust either
            return voice_emotion, 0.9

        elif dissonance_score < 0.6:
            # Moderate dissonance - trust voice slightly more
            return voice_emotion, 0.75

        else:
            # High dissonance - DEFINITELY trust voice
            # They're hiding something - the voice reveals the truth
            micro_count = sum(micro_moments.values())
            confidence = min(0.6 + (micro_count * 0.1), 0.95)
            return voice_emotion, confidence

    def _calculate_baseline_deviation(
        self,
        current_features: Dict,
        baseline: Dict
    ) -> float:
        """
        How different is this from their NORMAL voice?

        Returns: 0.0 (normal for them) to 1.0 (very different)
        """
        deviations = []

        # Pitch deviation
        current_pitch = current_features.get('prosodic', {}).get('pitch_mean', 0)
        baseline_pitch = baseline.get('typical_pitch_mean', 0)
        baseline_pitch_std = baseline.get('typical_pitch_std', 1)

        if baseline_pitch_std > 0:
            pitch_dev = abs(current_pitch - baseline_pitch) / baseline_pitch_std
            deviations.append(min(pitch_dev / 2, 1.0))  # Normalize to 0-1

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

        # Average deviation
        if deviations:
            return np.mean(deviations)
        return 0.0

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

        Returns: (risk_level, interpretation)
        """
        risk_score = 0.0
        risk_factors = []

        # Factor 1: High dissonance (hiding distress)
        if dissonance_score > 0.7:
            risk_score += 0.4
            risk_factors.append("Concealing true emotions")

        # Factor 2: Negative truth emotion
        if truth_emotion in ['sad', 'fear', 'angry']:
            risk_score += 0.3
            risk_factors.append(f"Experiencing {truth_emotion}")

        # Factor 3: Micro-moments (physiological distress)
        micro_count = sum(micro_moments.values())
        if micro_count >= 3:
            risk_score += 0.3
            risk_factors.append("Multiple physiological stress markers")

        # Factor 4: High baseline deviation (unusual for them)
        if baseline_deviation > 0.6:
            risk_score += 0.2
            risk_factors.append("Voice significantly different from normal")

        # Factor 5: Crisis keywords
        crisis_keywords = [
            'can\'t go on', 'want to die', 'no point', 'end it',
            'better off without me', 'give up', 'nimechoka sana'
        ]
        if any(keyword in transcript.lower() for keyword in crisis_keywords):
            risk_score += 0.5
            risk_factors.append("CRITICAL: Crisis language detected")

        # Factor 6: "Performing wellness" (dangerous calm)
        if dissonance_score > 0.6 and micro_moments.get('flat_prosody'):
            # Says "better" but voice is eerily flat - post-decision calm
            if any(word in transcript.lower() for word in ['better', 'peace', 'clear', 'decided']):
                risk_score += 0.6
                risk_factors.append("CRITICAL: Possible post-decision calm (suicide risk)")

        # Determine risk level
        if risk_score >= 0.8:
            level = "critical"
            interpretation = "IMMEDIATE RISK: " + "; ".join(risk_factors)
        elif risk_score >= 0.6:
            level = "high"
            interpretation = "High risk: " + "; ".join(risk_factors)
        elif risk_score >= 0.4:
            level = "medium"
            interpretation = "Moderate concern: " + "; ".join(risk_factors)
        else:
            level = "low"
            interpretation = "Low risk: " + ("; ".join(risk_factors) if risk_factors else "No significant concerns")

        return level, interpretation

    def _classify_dissonance_type(
        self,
        stated_emotion: str,
        voice_emotion: str,
        dissonance_score: float
    ) -> str:
        """
        Classify the TYPE of dissonance
        """
        if dissonance_score < 0.3:
            return "congruent"  # Aligned communication

        if stated_emotion == 'positive' and voice_emotion == 'negative':
            return "defensive_concealment"  # Hiding distress

        if stated_emotion == 'negative' and voice_emotion == 'positive':
            return "exaggeration"  # Overstating distress

        if stated_emotion == 'neutral' and voice_emotion == 'negative':
            return "minimization"  # Downplaying distress

        return "mixed_signals"  # Complex mismatch
```

**Integration Points**:
```python
# In main.py - add new endpoint

@app.post("/detect-truth", response_model=TruthDetectionResult)
async def detect_emotional_truth(file: UploadFile = File(...)):
    """
    Analyze emotional truth from audio + transcription
    Detects gap between what they SAY and how they SOUND
    """
    # 1. Read audio
    audio_data = await file.read()

    # 2. Process audio
    processed_audio = audio_processor.preprocess_audio(audio_data)

    # 3. Detect voice emotion
    emotion_result = await emotion_detector.detect_emotion(processed_audio)

    # 4. Transcribe speech (NEW - needs integration)
    transcript = await speech_service.transcribe(audio_data)

    # 5. Detect dissonance (NEW)
    truth_result = await dissonance_detector.detect_dissonance(
        transcript=transcript.text,
        voice_emotion=emotion_result.emotion,
        voice_features=emotion_result.features,
        user_baseline=None  # TODO: fetch from database
    )

    return truth_result
```

---

### 🎯 Priority 2: Personal Baseline Tracking

**What**: Learn each user's "normal" voice to detect when they're NOT themselves.

**Database Schema**:
```sql
-- New table: user_voice_baselines
CREATE TABLE user_voice_baselines (
    user_id UUID PRIMARY KEY,
    sessions_analyzed INT DEFAULT 0,
    baseline_established BOOLEAN DEFAULT FALSE,

    -- Prosodic baseline
    typical_pitch_mean FLOAT,
    typical_pitch_std FLOAT,
    typical_pitch_range FLOAT,

    -- Energy baseline
    typical_energy_mean FLOAT,
    typical_energy_std FLOAT,

    -- Temporal baseline
    typical_speech_rate FLOAT,
    typical_pause_ratio FLOAT,

    -- Emotional expressiveness
    typical_prosody_variance FLOAT,  -- How expressive they normally are

    -- Personal stress markers
    stress_markers JSONB,  -- e.g., {"faster_when_anxious": true, "quieter_when_sad": true}

    -- Update tracking
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Session history for baseline calculation
CREATE TABLE voice_sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    timestamp TIMESTAMP DEFAULT NOW(),

    -- Extracted features
    pitch_mean FLOAT,
    pitch_std FLOAT,
    energy_mean FLOAT,
    speech_rate FLOAT,

    -- Detected emotion
    emotion VARCHAR(50),
    emotion_confidence FLOAT,

    -- Dissonance
    dissonance_score FLOAT,
    risk_level VARCHAR(20),

    -- Raw features (for reanalysis)
    features JSONB
);
```

**Implementation**:
```python
# New file: src/baseline_tracker.py

class BaselineTracker:
    """
    Tracks user's personal voice baseline over time
    """

    async def update_baseline(self, user_id: str, session_features: Dict):
        """
        Update user's baseline with new session data

        First 3 sessions: collect data
        Session 4+: calculate baseline and update incrementally
        """
        # Get current baseline
        baseline = await self.db.get_baseline(user_id)

        if baseline is None:
            # Create new baseline
            baseline = await self.db.create_baseline(user_id)

        # Add session to history
        await self.db.add_session(user_id, session_features)

        # Get all sessions for this user
        sessions = await self.db.get_user_sessions(user_id)

        if len(sessions) < 3:
            # Not enough data yet
            return baseline

        # Calculate baseline from sessions
        baseline_data = self._calculate_baseline_from_sessions(sessions)

        # Update database
        await self.db.update_baseline(user_id, baseline_data)

        return baseline_data

    def _calculate_baseline_from_sessions(self, sessions: List[Dict]) -> Dict:
        """
        Calculate typical values from session history
        """
        # Extract features from all sessions
        pitch_means = [s['pitch_mean'] for s in sessions]
        pitch_stds = [s['pitch_std'] for s in sessions]
        energy_means = [s['energy_mean'] for s in sessions]
        speech_rates = [s['speech_rate'] for s in sessions]

        # Calculate typical values
        baseline = {
            'typical_pitch_mean': np.mean(pitch_means),
            'typical_pitch_std': np.mean(pitch_stds),
            'typical_energy_mean': np.mean(energy_means),
            'typical_speech_rate': np.mean(speech_rates),
            'sessions_analyzed': len(sessions),
            'baseline_established': len(sessions) >= 3
        }

        return baseline
```

---

### 🎯 Priority 3: Micro-Moment Detection (Advanced)

**What**: Detect physiological leakage signals that bypass conscious control.

**Currently Missing Features**:

1. **Voice Tremor Detection** (better implementation needed)
```python
def detect_voice_tremor(audio: np.ndarray, sr: int) -> Tuple[bool, float]:
    """
    Detect trembling voice (fear, suppressed crying)

    Method: Analyze amplitude modulation in 4-8 Hz range (tremor frequency)
    """
    # Extract amplitude envelope
    amplitude = np.abs(librosa.stft(audio))
    envelope = np.mean(amplitude, axis=0)

    # FFT of envelope to find modulation frequencies
    fft = np.fft.fft(envelope)
    freqs = np.fft.fftfreq(len(envelope), 1/sr)

    # Check for peak in tremor range (4-8 Hz)
    tremor_range = (freqs >= 4) & (freqs <= 8)
    tremor_power = np.sum(np.abs(fft[tremor_range]))
    total_power = np.sum(np.abs(fft))

    tremor_ratio = tremor_power / total_power if total_power > 0 else 0

    return tremor_ratio > 0.15, tremor_ratio
```

2. **Sigh Detection**
```python
def detect_sighs(audio: np.ndarray, sr: int) -> List[float]:
    """
    Detect sighs (burden, resignation, emotional release)

    Method: Find sudden energy increases followed by decay
    """
    # Extract energy envelope
    rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]

    # Find peaks (sudden increases)
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(rms, prominence=0.1, width=5)

    # Filter for sigh pattern (longer duration, followed by decay)
    sighs = []
    for peak_idx in peaks:
        # Check if followed by decay
        if peak_idx + 10 < len(rms):
            decay = rms[peak_idx] - rms[peak_idx + 10]
            if decay > 0.05:  # Significant decay
                sigh_time = librosa.frames_to_time(peak_idx, sr=sr, hop_length=512)
                sighs.append(sigh_time)

    return sighs
```

3. **Voice Crack Detection** (pitch discontinuities)
```python
def detect_voice_cracks(audio: np.ndarray, sr: int) -> List[float]:
    """
    Detect voice cracks (emotion breaking through)

    Method: Find sudden large pitch jumps
    """
    # Extract F0
    f0, voiced_flag, _ = librosa.pyin(audio, fmin=80, fmax=400, sr=sr)

    # Find voiced segments
    f0_voiced = f0[voiced_flag]

    if len(f0_voiced) < 2:
        return []

    # Calculate pitch jumps
    pitch_diff = np.diff(f0_voiced)

    # Find large jumps (> 50 Hz)
    crack_indices = np.where(np.abs(pitch_diff) > 50)[0]

    # Convert to time
    cracks = []
    for idx in crack_indices:
        crack_time = idx * (len(audio) / sr) / len(f0_voiced)
        cracks.append(crack_time)

    return cracks
```

4. **Hesitation/Pause Pattern Analysis**
```python
def analyze_hesitation_patterns(audio: np.ndarray, sr: int) -> Dict:
    """
    Detect hesitation before speech (searching for "acceptable" answer)

    Returns: Pause statistics
    """
    # Voice Activity Detection
    from speechbrain.pretrained import VAD
    vad = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparole")

    # Detect speech/silence boundaries
    boundaries = vad.get_speech_segments(audio, sr)

    # Calculate pauses
    pauses = []
    for i in range(len(boundaries) - 1):
        pause_duration = boundaries[i+1][0] - boundaries[i][1]
        pauses.append(pause_duration)

    if not pauses:
        return {'avg_pause': 0, 'max_pause': 0, 'pause_count': 0}

    return {
        'avg_pause': np.mean(pauses),
        'max_pause': np.max(pauses),
        'pause_count': len(pauses),
        'long_pauses': sum(1 for p in pauses if p > 1.0)  # Pauses > 1 second
    }
```

**Integration**:
```python
# Update src/dissonance_detector.py

def _detect_micro_moments_advanced(self, audio: np.ndarray, sr: int, features: Dict) -> Dict:
    """
    Advanced micro-moment detection with physiological signals
    """
    micro_moments = {
        # Basic (already implemented)
        'voice_tremor': False,
        'voice_crack': False,
        'sigh_detected': False,
        'hesitation': False,

        # Advanced (new)
        'tremor_intensity': 0.0,
        'crack_count': 0,
        'sigh_times': [],
        'pause_stats': {},
        'breath_irregularity': 0.0
    }

    # Advanced tremor detection
    has_tremor, tremor_intensity = detect_voice_tremor(audio, sr)
    micro_moments['voice_tremor'] = has_tremor
    micro_moments['tremor_intensity'] = tremor_intensity

    # Voice crack detection
    cracks = detect_voice_cracks(audio, sr)
    micro_moments['voice_crack'] = len(cracks) > 0
    micro_moments['crack_count'] = len(cracks)

    # Sigh detection
    sighs = detect_sighs(audio, sr)
    micro_moments['sigh_detected'] = len(sighs) > 0
    micro_moments['sigh_times'] = sighs

    # Hesitation analysis
    pause_stats = analyze_hesitation_patterns(audio, sr)
    micro_moments['hesitation'] = pause_stats['long_pauses'] > 2
    micro_moments['pause_stats'] = pause_stats

    return micro_moments
```

---

### 🎯 Priority 4: Cultural Context Integration

**What**: Recognize East African cultural deflection patterns and interpret them correctly.

**Implementation**:
```python
# New file: src/cultural_context.py

class CulturalContextAnalyzer:
    """
    Interpret East African cultural communication patterns
    """

    def __init__(self):
        # Swahili deflection phrases
        self.swahili_deflections = {
            'nimechoka': {
                'literal': 'I am tired',
                'cultural_meaning': 'Emotionally exhausted, possibly giving up',
                'risk_level': 'high',
                'probe_question': 'When you say "nimechoka," it sounds like more than physical tiredness. What burden are you carrying?'
            },
            'sawa': {
                'literal': 'Okay/fine',
                'cultural_meaning': 'May be deflecting, culturally polite response',
                'risk_level': 'medium',
                'probe_question': 'I hear you say "sawa." But how are you really feeling beneath that?'
            },
            'sijui': {
                'literal': 'I don\'t know',
                'cultural_meaning': 'Overwhelmed, confused, or avoiding',
                'risk_level': 'medium',
                'probe_question': 'You said "sijui" - it sounds like things feel confusing right now. Tell me more about that.'
            },
            'tutaona': {
                'literal': 'We\'ll see',
                'cultural_meaning': 'Fatalistic, giving up control, resignation',
                'risk_level': 'medium',
                'probe_question': 'When you say "tutaona," it sounds like you\'re letting go. What feels out of your control?'
            }
        }

        # English deflection patterns (East African context)
        self.english_deflections = {
            'managing': {
                'surface': 'Coping adequately',
                'hidden': 'Barely holding on, minimizing struggle',
                'risk_level': 'medium'
            },
            'just tired': {
                'surface': 'Physically tired',
                'hidden': 'Emotionally/existentially exhausted',
                'risk_level': 'high'
            },
            'it\'s fine': {
                'surface': 'No problem',
                'hidden': 'Suppressing feelings, being stoic',
                'risk_level': 'medium'
            }
        }

        # Code-switching patterns (stress indicator)
        self.code_switch_triggers = {
            'swahili_to_english': 'May indicate distancing from emotion',
            'english_to_swahili': 'May indicate emotional overwhelm, returning to mother tongue for comfort'
        }

    def analyze_cultural_patterns(
        self,
        transcript: str,
        detected_language: str,
        voice_emotion: str
    ) -> Dict:
        """
        Detect cultural deflection and interpret meaning
        """
        result = {
            'deflection_detected': False,
            'cultural_meaning': None,
            'risk_amplification': 0.0,
            'suggested_probe': None
        }

        transcript_lower = transcript.lower()

        # Check Swahili deflections
        for phrase, context in self.swahili_deflections.items():
            if phrase in transcript_lower:
                result['deflection_detected'] = True
                result['cultural_meaning'] = context['cultural_meaning']
                result['suggested_probe'] = context['probe_question']

                # Amplify risk if voice also shows distress
                if voice_emotion in ['sad', 'fear', 'angry']:
                    result['risk_amplification'] = 0.3

                break

        # Check English deflections
        for phrase, context in self.english_deflections.items():
            if phrase in transcript_lower:
                result['deflection_detected'] = True
                result['cultural_meaning'] = context['hidden']
                result['risk_amplification'] = 0.2
                break

        return result

    def detect_code_switching(
        self,
        transcript: str,
        previous_language: Optional[str]
    ) -> Dict:
        """
        Detect when user switches language mid-conversation (stress indicator)
        """
        # Simplified: Check for mixed language
        has_swahili = any(word in transcript.lower() for word in [
            'nimechoka', 'sawa', 'sijui', 'tutaona', 'shida', 'niko'
        ])
        has_english = any(word in transcript.lower() for word in [
            'i', 'am', 'feeling', 'tired', 'fine', 'okay'
        ])

        code_switched = has_swahili and has_english

        return {
            'code_switched': code_switched,
            'interpretation': 'Possible stress-induced language mixing' if code_switched else None,
            'risk_indicator': code_switched
        }
```

---

### 🎯 Priority 5: Speech-to-Text Integration

**Current**: Speech service defined but not integrated with emotion detection.

**Fix**: Connect STT to dissonance detector.

```python
# Update services/speech-processing/main.py

@app.post("/transcribe-with-emotion")
async def transcribe_with_emotion_analysis(
    audio: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """
    Combined endpoint: transcribe + emotion + dissonance analysis
    """
    audio_data = await audio.read()

    # 1. Transcribe
    transcript_result = await transcribe_audio(audio_data)

    # 2. Detect emotion from voice
    emotion_result = await emotion_service.detect_emotion(audio_data)

    # 3. Get user baseline (if exists)
    baseline = None
    if user_id:
        baseline = await baseline_service.get_baseline(user_id)

    # 4. Analyze dissonance
    truth_result = await dissonance_detector.detect_dissonance(
        transcript=transcript_result['text'],
        voice_emotion=emotion_result.emotion,
        voice_features=emotion_result.features,
        user_baseline=baseline
    )

    # 5. Cultural context
    cultural_context = cultural_analyzer.analyze_cultural_patterns(
        transcript=transcript_result['text'],
        detected_language=transcript_result['language'],
        voice_emotion=emotion_result.emotion
    )

    return {
        'transcript': transcript_result,
        'voice_emotion': emotion_result,
        'truth_analysis': truth_result,
        'cultural_context': cultural_context,
        'timestamp': datetime.now().isoformat()
    }
```

---

## 4. Critical Architecture Critiques

### ❌ Critique 1: No Conversation Context

**Problem**: Each audio analysis is isolated. No conversational memory.

**Impact**: Can't track patterns like:
- "Third time they said 'I'm fine' but sounds sad"
- "Emotional state deteriorating over session"
- "First mentioned 'tired' 10 minutes ago, now using 'nimechoka' - escalation"

**Fix**: Add conversation session tracking.

```python
# New: Conversation session manager

class ConversationSession:
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.turns = []  # All conversation turns
        self.emotional_trajectory = []  # Track emotion over time
        self.dissonance_history = []  # Track concealment patterns
        self.risk_escalation = []  # Track if risk is increasing

    def add_turn(self, turn_data: Dict):
        """Add a conversation turn"""
        self.turns.append(turn_data)
        self.emotional_trajectory.append(turn_data['voice_emotion'])
        self.dissonance_history.append(turn_data['dissonance_score'])
        self.risk_escalation.append(turn_data['risk_level'])

    def analyze_session_patterns(self) -> Dict:
        """
        Analyze patterns across the session
        """
        return {
            'emotional_trend': self._calculate_emotional_trend(),
            'dissonance_trend': self._calculate_dissonance_trend(),
            'risk_trajectory': self._calculate_risk_trajectory(),
            'repeated_deflections': self._count_repeated_deflections()
        }

    def _calculate_risk_trajectory(self) -> str:
        """Is risk increasing, decreasing, or stable?"""
        if len(self.risk_escalation) < 2:
            return 'insufficient_data'

        risk_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        numeric_risks = [risk_values.get(r, 0) for r in self.risk_escalation]

        # Simple trend
        if numeric_risks[-1] > numeric_risks[0]:
            return 'escalating'  # DANGER
        elif numeric_risks[-1] < numeric_risks[0]:
            return 'improving'
        else:
            return 'stable'
```

### ❌ Critique 2: No Real-Time Risk Alerting

**Problem**: System detects risk but doesn't actively alert or escalate.

**Impact**: High-risk users might not get immediate help.

**Fix**: Add crisis detection service with alerting.

```python
# New: Crisis alert system

class CrisisAlertSystem:
    def __init__(self):
        self.alert_thresholds = {
            'critical': self._critical_alert,
            'high': self._high_alert,
            'medium': self._medium_alert
        }

    async def evaluate_and_alert(
        self,
        user_id: str,
        truth_result: DissonanceResult,
        session_context: ConversationSession
    ):
        """
        Evaluate risk and trigger appropriate alerts
        """
        risk_level = truth_result.risk_level

        if risk_level in self.alert_thresholds:
            await self.alert_thresholds[risk_level](user_id, truth_result, session_context)

    async def _critical_alert(self, user_id, truth_result, session):
        """
        CRITICAL: Immediate intervention needed
        """
        # 1. Notify human counselor immediately
        await self.notify_counselor(
            user_id=user_id,
            urgency='CRITICAL',
            reason=truth_result.risk_interpretation,
            session_id=session.session_id
        )

        # 2. Send emergency resources to user
        await self.send_emergency_resources(user_id)

        # 3. Log for compliance
        await self.log_crisis_event(user_id, truth_result)

        # 4. If configured, alert emergency contacts
        user_settings = await self.get_user_settings(user_id)
        if user_settings.get('emergency_contact_consent'):
            await self.alert_emergency_contact(user_id)

    async def _high_alert(self, user_id, truth_result, session):
        """
        HIGH: Elevated risk, needs follow-up
        """
        # Add to counselor queue (non-urgent)
        await self.add_to_counselor_queue(
            user_id=user_id,
            priority='high',
            reason=truth_result.risk_interpretation
        )

        # Suggest professional help to user
        await self.suggest_professional_help(user_id)
```

### ❌ Critique 3: No Model Fine-Tuning for Mental Health

**Problem**: Using generic Wav2Vec2 + RandomForest trained on general emotions.

**Impact**: May not capture mental health-specific patterns (e.g., "post-decision calm" before suicide).

**Fix**: Create mental health-specific training dataset and fine-tune.

**Recommendation**:
1. Collect dataset of mental health conversations (with consent)
2. Label with:
   - Basic emotion
   - Risk level
   - Dissonance type
   - Cultural context
3. Fine-tune Wav2Vec2 for mental health domain
4. Train specialized classifier for risk patterns

```python
# Future: Mental health-specific model

class MentalHealthEmotionDetector(EmotionDetector):
    """
    Specialized emotion detector for mental health contexts
    """

    def __init__(self):
        super().__init__()
        # Load mental health fine-tuned model
        self.model_name = "resonaai/wav2vec2-mental-health"

        # Expanded emotion labels for mental health
        self.emotion_labels = [
            'neutral', 'happy', 'sad', 'angry', 'fear',
            'hopeless',  # NEW: Depression marker
            'resigned',  # NEW: Giving up
            'numb',      # NEW: Emotional numbing
            'agitated',  # NEW: Anxiety/mania
            'resolved'   # NEW: Post-decision calm (dangerous)
        ]

    def _load_mental_health_classifier(self):
        """
        Load classifier trained on mental health dataset
        """
        # This would be trained on labeled mental health conversations
        pass
```

### ❌ Critique 4: No Explainability for Clinicians

**Problem**: AI gives risk scores but doesn't explain WHY to therapists.

**Impact**: Therapists can't validate or learn from AI assessments.

**Fix**: Add explainability module.

```python
class TruthDetectionExplainer:
    """
    Generate human-readable explanations of truth detection results
    """

    def explain_analysis(self, truth_result: DissonanceResult, audio_features: Dict) -> str:
        """
        Generate explanation for clinicians
        """
        explanation = []

        # 1. What they said vs how they sounded
        explanation.append(
            f"**Verbal Content**: User stated they were feeling '{truth_result.stated_emotion}' "
            f"(confidence: {truth_result.stated_confidence:.0%})"
        )

        explanation.append(
            f"**Voice Analysis**: Voice emotion detected as '{truth_result.voice_emotion}' "
            f"(confidence: {truth_result.voice_confidence:.0%})"
        )

        # 2. Dissonance explanation
        if truth_result.dissonance_score > 0.6:
            explanation.append(
                f"**⚠️ HIGH DISSONANCE** ({truth_result.dissonance_score:.0%}): "
                f"There is a significant mismatch between what the user said and how their voice sounded. "
                f"This suggests they may be concealing their true emotional state."
            )

        # 3. Micro-moments
        detected_signals = [k for k, v in truth_result.micro_moments.items() if v]
        if detected_signals:
            explanation.append(
                f"**Physiological Signals Detected**: {', '.join(detected_signals)}. "
                f"These involuntary vocal changes suggest emotional distress that may not be verbally expressed."
            )

        # 4. Baseline comparison
        if truth_result.baseline_deviation > 0.5:
            explanation.append(
                f"**Voice Different from Baseline** ({truth_result.baseline_deviation:.0%}): "
                f"The user's voice is significantly different from their typical patterns, "
                f"suggesting an unusual emotional state."
            )

        # 5. Risk interpretation
        explanation.append(
            f"**Risk Assessment** [{truth_result.risk_level.upper()}]: {truth_result.risk_interpretation}"
        )

        return "\n\n".join(explanation)
```

---

## 5. Implementation Roadmap

### Phase 1: Core Truth Detection (Weeks 1-3) ⭐ HIGHEST PRIORITY

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 1.1 | Build DissonanceDetector | `src/dissonance_detector.py` (new) | Medium |
| 1.2 | Integrate STT with emotion | `main.py`, `services/speech-processing/` | Low |
| 1.3 | Add /detect-truth endpoint | `main.py` | Low |
| 1.4 | Test on "I'm fine" scenarios | `tests/test_dissonance.py` (new) | Medium |
| 1.5 | Measure false negative rate | Evaluation script | Medium |

**Success Metric**: Can correctly identify 80%+ of "I'm fine" + sad voice cases as "concealment"

---

### Phase 2: Baseline Tracking (Weeks 4-5)

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 2.1 | Create database schema | `migrations/` | Low |
| 2.2 | Build BaselineTracker | `src/baseline_tracker.py` (new) | Medium |
| 2.3 | Modify endpoints to update baseline | `main.py` | Low |
| 2.4 | Add baseline deviation to dissonance | `src/dissonance_detector.py` | Medium |
| 2.5 | Test baseline convergence | User testing (3+ sessions) | High |

**Success Metric**: After 3 sessions, system can detect 70%+ of "unusual for this person" states

---

### Phase 3: Micro-Moment Detection (Weeks 6-7)

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 3.1 | Implement tremor detection | `src/micro_moments.py` (new) | High |
| 3.2 | Implement sigh detection | `src/micro_moments.py` | High |
| 3.3 | Implement voice crack detection | `src/micro_moments.py` | High |
| 3.4 | Implement hesitation analysis | `src/micro_moments.py` | Medium |
| 3.5 | Integrate with dissonance | `src/dissonance_detector.py` | Medium |

**Success Metric**: Detect 75%+ of physiological stress signals in labeled test data

---

### Phase 4: Cultural Context (Weeks 8-9)

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 4.1 | Build cultural analyzer | `src/cultural_context.py` (new) | Medium |
| 4.2 | Add Swahili deflection database | `config/cultural_patterns.json` | Low |
| 4.3 | Implement code-switching detection | `src/cultural_context.py` | Medium |
| 4.4 | Integrate with dissonance | `src/dissonance_detector.py` | Low |
| 4.5 | Test with East African users | User testing | High |

**Success Metric**: Correctly interpret 80%+ of "nimechoka", "sawa" cultural deflections

---

### Phase 5: Risk Alerting & Session Context (Weeks 10-11)

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 5.1 | Build ConversationSession | `src/session_manager.py` (new) | Medium |
| 5.2 | Track emotional trajectory | `src/session_manager.py` | Low |
| 5.3 | Build CrisisAlertSystem | `src/crisis_alerts.py` (new) | High |
| 5.4 | Integrate with counselor queue | `services/crisis-detection/` | Medium |
| 5.5 | Add emergency resource delivery | `src/crisis_alerts.py` | Medium |

**Success Metric**: 100% of critical risk cases trigger alert within 30 seconds

---

### Phase 6: Explainability & Clinician Tools (Weeks 12-13)

| Task | Description | Files to Create/Modify | Complexity |
|------|-------------|------------------------|------------|
| 6.1 | Build TruthDetectionExplainer | `src/explainability.py` (new) | Medium |
| 6.2 | Create clinician dashboard | `web-app/src/pages/Clinician/` | High |
| 6.3 | Add "Emotion Timeline" visualization | `web-app/src/components/EmotionTimeline/` | Medium |
| 6.4 | Generate session reports | `src/report_generator.py` | Medium |

**Success Metric**: Clinicians rate explanations as "helpful" 80%+ of the time

---

## 6. Data Flow Comparison: Current vs Proposed

### Current System
```
Input: Audio file
    ↓
Emotion: "sad" (85%)
    ↓
Output: Emotion label
```

**Weakness**: Tells us the emotion but not the TRUTH.

### Proposed System
```
Input: Audio file
    ↓
    ├─→ [Voice Emotion] → "sad" (85%)
    │   └─→ [Micro-Moments] → tremor, sigh detected
    │
    └─→ [Speech-to-Text] → "I'm fine, really"
           └─→ [Content Analysis] → "positive" (stated)

[Dissonance Detector]
    ├─ Voice says: sad
    ├─ Words say: positive
    ├─ Gap: HIGH (0.85)
    └─ Micro-signals: 2 detected

[Personal Baseline]
    └─ Deviation: 0.7 (very different from normal)

[Cultural Context]
    └─ Deflection: "I'm fine" pattern detected

[Truth Signal]
    ├─ True emotion: sad (trust voice over words)
    ├─ Risk: HIGH
    └─ Interpretation: "Defensive concealment - hiding distress"

Output: Complete truth analysis with risk assessment
```

---

## 7. Key Performance Indicators (KPIs)

### Truth Detection Accuracy
- **Dissonance Detection Rate**: % of "saying X but feeling Y" cases caught
  - Target: 85%+

- **False Negative Rate** (missed hidden distress):
  - Target: <10%

- **False Positive Rate** (flagging when actually fine):
  - Target: <15%

### Cultural Sensitivity
- **Deflection Recognition**: % of cultural patterns correctly interpreted
  - Target: 80%+ for Swahili deflections

- **Code-Switching Detection**: % of language switches detected
  - Target: 75%+

### Risk Assessment
- **Suicide Risk Detection**: % of critical cases identified
  - Target: 100% (zero tolerance for misses)

- **Alert Latency**: Time from detection to counselor alert
  - Target: <30 seconds

### Baseline Tracking
- **Baseline Convergence**: Sessions needed for accurate baseline
  - Target: 3 sessions

- **Deviation Accuracy**: % of "unusual for them" states detected
  - Target: 70%+

---

## 8. Resource Requirements

### Development Team
- **1 ML Engineer**: Wav2Vec2 fine-tuning, micro-moment detection algorithms
- **1 Backend Engineer**: Dissonance detector, baseline tracking, API integration
- **1 Frontend Engineer**: Emotion timeline, clinician dashboard
- **1 Mental Health Expert**: Validate risk assessments, define cultural patterns
- **1 East African Cultural Consultant**: Swahili patterns, code-switching norms

### Data Needs
- **Mental Health Audio Dataset**: 500+ hours of therapy conversations (with consent)
  - Labeled for: emotion, risk, dissonance, cultural context

- **East African Voice Data**: 200+ hours of Swahili/English conversations
  - For accent adaptation and cultural pattern learning

### Infrastructure
- **GPU Compute**: For Wav2Vec2 inference (real-time requirement)
  - Recommendation: 2x NVIDIA T4 GPUs

- **Database**: PostgreSQL for baseline + session history
  - Estimate: 100GB for 10K users (1 year)

### Timeline
- **Phase 1-3** (Core + Baseline + Micro-moments): 7 weeks
- **Phase 4-5** (Cultural + Alerts): 4 weeks
- **Phase 6** (Explainability): 2 weeks
- **Testing & Refinement**: 3 weeks
- **Total**: ~16 weeks (4 months)

---

## 9. Final Critique Summary

### ✅ What ResonaAI Does Well
1. **Solid technical foundation**: Wav2Vec2, comprehensive features, good architecture
2. **East African focus**: Accent adaptation, Swahili support
3. **Privacy-first**: Encryption, consent management
4. **Real-time capable**: Streaming support, WebSocket
5. **Well-documented**: Clear architecture, good code structure

### ❌ What ResonaAI is Missing (Critical for "Truth Detection")
1. **No dissonance detection** - Can't compare words to voice
2. **No baseline tracking** - Can't detect "unusual for them"
3. **No micro-moment detection** - Misses physiological leakage
4. **No cultural deflection** - Won't catch "nimechoka" correctly
5. **No risk scoring** - Just emotion, no crisis assessment
6. **No conversation context** - Each turn is isolated
7. **No explainability** - Black box for clinicians

### 🎯 The Core Innovation You Need
**The gap between words and voice IS the signal.**

Current ResonaAI answers: "What emotion is in the voice?"
Revolutionary ResonaAI should answer: "Is this person being honest about how they feel?"

### 💡 The Pitch Should Be
> "Text-based AI believes the words. Voice-based AI catches the truth.
>
> When someone says 'I'm fine' but their voice is trembling, Resona doesn't just detect sadness—it detects *concealment*. We catch the hidden distress that would lead text-only AI to say 'Great, glad you're doing well!' right before a suicide.
>
> This is why voice matters. This is why we'll save lives that text-based mental health apps miss."

---

## 10. Recommended Next Steps

1. **Immediate** (This week):
   - Implement basic DissonanceDetector (Priority 1.1-1.3)
   - Create /detect-truth endpoint
   - Test on synthetic "I'm fine" + sad voice examples

2. **Short-term** (Next month):
   - Complete Phase 1 (Core Truth Detection)
   - Start collecting user baselines (Phase 2)
   - Begin micro-moment algorithm development (Phase 3)

3. **Medium-term** (Months 2-3):
   - Deploy baseline tracking
   - Launch advanced micro-moment detection
   - Integrate cultural context

4. **Long-term** (Month 4+):
   - Fine-tune models on mental health data
   - Build clinician dashboard
   - Pilot with East African mental health providers

---

## Questions for You

1. **Do you have access to mental health conversation data** for training/testing?
   - If not, can you partner with mental health providers to collect (with consent)?

2. **What's your current user base?**
   - Do you have enough users to build baselines?

3. **Do you have clinical advisors** who can validate risk assessments?

4. **What's your risk tolerance** for false negatives (missing suicide risk)?
   - This determines how conservative the system should be

5. **Are you planning to fine-tune models** or use off-the-shelf?
   - Fine-tuning will significantly improve accuracy but requires data + compute

6. **What's your go-to-market timeline?**
   - This affects which phases to prioritize

---

This analysis shows ResonaAI has great bones but needs the "truth detection" core to fulfill the vision. The gap is clear, and the roadmap is buildable. Let me know which areas you want to dive deeper into!
