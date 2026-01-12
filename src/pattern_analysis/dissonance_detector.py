"""
Dissonance Detector

Detects gaps between stated emotion (words) and embodied emotion (voice).
Identifies concealment patterns and determines truth signals.
"""

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
        audio: Optional[np.ndarray] = None,
        sample_rate: int = 16000,
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
        audio: Optional[np.ndarray],
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
