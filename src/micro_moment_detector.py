"""
Micro-Moment Detector

Detects physiological stress signals in voice: tremors, sighs, voice cracks, hesitations,
and other micro-moments that indicate suppressed emotions or emotional burden.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import librosa
from scipy.signal import find_peaks
from loguru import logger


class MicroMomentDetector:
    """
    Detects micro-moments in voice that indicate physiological stress signals.
    
    These include:
    - Tremors: Voice trembling (suppressed crying, fear)
    - Sighs: Long exhalations (emotional burden, resignation)
    - Voice cracks: Pitch breaks (emotion breaking through)
    - Hesitations: Pauses and uncertainty patterns
    """

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the Micro-Moment Detector.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
        """
        self.sample_rate = sample_rate
        
        # Detection thresholds (tunable)
        self.tremor_freq_min = 4.0  # Hz
        self.tremor_freq_max = 8.0  # Hz
        self.tremor_power_threshold = 0.15  # Minimum tremor power ratio
        
        self.sigh_decay_threshold = 0.05  # Minimum energy decay for sigh
        self.sigh_prominence = 0.1  # Peak prominence for sigh detection
        
        self.voice_crack_threshold = 50.0  # Hz - minimum pitch jump for crack
        self.voice_crack_intensity_scale = 200.0  # Hz - scale for intensity calculation
        
        self.pause_energy_percentile = 20  # Percentile for pause detection
        self.long_pause_duration = 1.0  # seconds - minimum for long pause

    def detect_tremor(
        self, 
        audio: np.ndarray, 
        sr: Optional[int] = None
    ) -> Tuple[bool, float]:
        """
        Detect voice tremors (suppressed crying, fear patterns).
        
        Analyzes pitch variation and micro-oscillations in the 4-8 Hz range,
        which is characteristic of physiological tremors.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses self.sample_rate if not provided)
            
        Returns:
            Tuple of (detected: bool, intensity: float 0-1)
        """
        if sr is None:
            sr = self.sample_rate
            
        try:
            # Extract fundamental frequency (pitch)
            f0, voiced_flag, _ = librosa.pyin(
                audio,
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
                sr=sr
            )
            
            # Get voiced segments only
            f0_voiced = f0[voiced_flag]
            
            if len(f0_voiced) < 10:  # Need minimum data points
                return False, 0.0
            
            # Remove NaN values
            f0_voiced = f0_voiced[~np.isnan(f0_voiced)]
            
            if len(f0_voiced) < 10:
                return False, 0.0
            
            # Create pitch envelope (smoothed)
            # Use moving average to smooth the pitch contour
            window_size = min(5, len(f0_voiced) // 4)
            if window_size < 1:
                window_size = 1
            
            envelope = np.convolve(
                f0_voiced, 
                np.ones(window_size) / window_size, 
                mode='valid'
            )
            
            if len(envelope) < 10:
                return False, 0.0
            
            # Apply FFT to detect tremor frequency
            fft = np.fft.fft(envelope)
            freqs = np.fft.fftfreq(len(envelope), 1.0 / sr)
            
            # Get positive frequencies only
            positive_freqs = freqs[:len(freqs) // 2]
            fft_positive = fft[:len(fft) // 2]
            
            # Check for power in tremor range (4-8 Hz)
            tremor_range = (positive_freqs >= self.tremor_freq_min) & \
                          (positive_freqs <= self.tremor_freq_max)
            
            tremor_power = np.sum(np.abs(fft_positive[tremor_range]))
            total_power = np.sum(np.abs(fft_positive))
            
            if total_power == 0:
                return False, 0.0
            
            tremor_ratio = tremor_power / total_power
            detected = tremor_ratio > self.tremor_power_threshold
            
            # Intensity is normalized tremor ratio (capped at 1.0)
            intensity = min(1.0, tremor_ratio / self.tremor_power_threshold)
            
            return detected, intensity
            
        except Exception as e:
            logger.error(f"Error detecting tremor: {str(e)}")
            return False, 0.0

    def detect_sighs(
        self, 
        audio: np.ndarray, 
        sr: Optional[int] = None
    ) -> List[float]:
        """
        Detect sighs (emotional burden indicators).
        
        Detects long exhalations characterized by sudden energy increases
        followed by decay, indicating stress-release patterns.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses self.sample_rate if not provided)
            
        Returns:
            List of timestamps (in seconds) where sighs occur
        """
        if sr is None:
            sr = self.sample_rate
            
        try:
            # Extract energy envelope (RMS)
            rms = librosa.feature.rms(
                y=audio, 
                frame_length=2048, 
                hop_length=512
            )[0]
            
            if len(rms) < 10:
                return []
            
            # Find peaks (sudden energy increases)
            peaks, properties = find_peaks(
                rms, 
                prominence=self.sigh_prominence, 
                width=5
            )
            
            if len(peaks) == 0:
                return []
            
            # Filter for sigh pattern: peak followed by decay
            sighs = []
            for peak_idx in peaks:
                # Check if followed by significant decay
                if peak_idx + 10 < len(rms):
                    decay = rms[peak_idx] - rms[peak_idx + 10]
                    if decay > self.sigh_decay_threshold:
                        # Convert frame index to time
                        sigh_time = librosa.frames_to_time(
                            peak_idx, 
                            sr=sr, 
                            hop_length=512
                        )
                        sighs.append(sigh_time)
            
            return sighs
            
        except Exception as e:
            logger.error(f"Error detecting sighs: {str(e)}")
            return []

    def detect_voice_cracks(
        self, 
        audio: np.ndarray, 
        sr: Optional[int] = None
    ) -> List[Tuple[float, float]]:
        """
        Detect voice cracks (emotion breaking through).
        
        Detects pitch discontinuities where emotion overwhelms voice control,
        characterized by sudden large pitch jumps.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses self.sample_rate if not provided)
            
        Returns:
            List of (timestamp, intensity) tuples where cracks occur
        """
        if sr is None:
            sr = self.sample_rate
            
        try:
            # Extract fundamental frequency
            f0, voiced_flag, _ = librosa.pyin(
                audio,
                fmin=80,  # Lower bound for voice
                fmax=400,  # Upper bound for voice
                sr=sr
            )
            
            # Get voiced segments
            f0_voiced = f0[voiced_flag]
            
            if len(f0_voiced) < 2:
                return []
            
            # Remove NaN values
            f0_voiced = f0_voiced[~np.isnan(f0_voiced)]
            
            if len(f0_voiced) < 2:
                return []
            
            # Calculate pitch differences
            pitch_diff = np.diff(f0_voiced)
            
            # Find large jumps (> threshold Hz)
            crack_indices = np.where(np.abs(pitch_diff) > self.voice_crack_threshold)[0]
            
            if len(crack_indices) == 0:
                return []
            
            # Convert to timestamps and calculate intensities
            cracks = []
            frame_duration = len(audio) / sr / len(f0_voiced)
            
            for idx in crack_indices:
                crack_time = idx * frame_duration
                jump_magnitude = abs(pitch_diff[idx])
                
                # Intensity based on jump magnitude (normalized 0-1)
                intensity = min(1.0, jump_magnitude / self.voice_crack_intensity_scale)
                
                cracks.append((crack_time, intensity))
            
            return cracks
            
        except Exception as e:
            logger.error(f"Error detecting voice cracks: {str(e)}")
            return []

    def detect_hesitations(
        self, 
        audio: np.ndarray, 
        sr: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detect hesitations and pauses (uncertainty patterns).
        
        Detects pauses and hesitations that indicate emotional processing
        or uncertainty, using energy-based voice activity detection.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses self.sample_rate if not provided)
            
        Returns:
            Dictionary with pause statistics:
            - count: Total number of pauses
            - avg_duration: Average pause duration in seconds
            - max_duration: Maximum pause duration
            - long_pauses: Count of pauses > 1.0 second
            - pause_ratio: Ratio of pause time to total time
        """
        if sr is None:
            sr = self.sample_rate
            
        try:
            # Extract energy envelope
            rms = librosa.feature.rms(y=audio).flatten()
            
            if len(rms) == 0:
                return {
                    'count': 0,
                    'avg_duration': 0.0,
                    'max_duration': 0.0,
                    'long_pauses': 0,
                    'pause_ratio': 0.0
                }
            
            # Calculate energy threshold (low energy = pause)
            energy_threshold = np.percentile(rms, self.pause_energy_percentile)
            
            # Identify low-energy segments (pauses)
            is_pause = rms < energy_threshold
            
            if not np.any(is_pause):
                return {
                    'count': 0,
                    'avg_duration': 0.0,
                    'max_duration': 0.0,
                    'long_pauses': 0,
                    'pause_ratio': 0.0
                }
            
            # Find pause segments (consecutive low-energy frames)
            pause_segments = []
            in_pause = False
            pause_start = 0
            
            for i, pause in enumerate(is_pause):
                if pause and not in_pause:
                    # Start of pause
                    pause_start = i
                    in_pause = True
                elif not pause and in_pause:
                    # End of pause
                    pause_duration = (i - pause_start) * (len(audio) / sr / len(rms))
                    pause_segments.append(pause_duration)
                    in_pause = False
            
            # Handle pause at end of audio
            if in_pause:
                pause_duration = (len(is_pause) - pause_start) * (len(audio) / sr / len(rms))
                pause_segments.append(pause_duration)
            
            if len(pause_segments) == 0:
                return {
                    'count': 0,
                    'avg_duration': 0.0,
                    'max_duration': 0.0,
                    'long_pauses': 0,
                    'pause_ratio': 0.0
                }
            
            # Calculate statistics
            pause_count = len(pause_segments)
            avg_duration = np.mean(pause_segments)
            max_duration = np.max(pause_segments)
            long_pauses = sum(1 for p in pause_segments if p > self.long_pause_duration)
            
            # Calculate pause ratio
            total_duration = len(audio) / sr
            pause_time = sum(pause_segments)
            pause_ratio = pause_time / total_duration if total_duration > 0 else 0.0
            
            return {
                'count': pause_count,
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'long_pauses': long_pauses,
                'pause_ratio': pause_ratio
            }
            
        except Exception as e:
            logger.error(f"Error detecting hesitations: {str(e)}")
            return {
                'count': 0,
                'avg_duration': 0.0,
                'max_duration': 0.0,
                'long_pauses': 0,
                'pause_ratio': 0.0
            }

    def analyze_micro_moments(
        self, 
        audio: np.ndarray, 
        sr: Optional[int] = None,
        voice_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Overall analysis combining all micro-moments.
        
        Performs comprehensive analysis of all micro-moments and generates
        interpretation and risk assessment.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses self.sample_rate if not provided)
            voice_features: Optional pre-extracted voice features dict
            
        Returns:
            Complete analysis dictionary with:
            - tremor: {detected, intensity, interpretation}
            - sighs: {count, intensity, interpretation}
            - voice_cracks: {count, intensity, interpretation}
            - hesitations: {count, average_duration, interpretation}
            - overall_risk: "low" | "medium" | "medium-high" | "high"
            - interpretation: Overall interpretation string
        """
        if sr is None:
            sr = self.sample_rate
            
        try:
            # Detect all micro-moments
            tremor_detected, tremor_intensity = self.detect_tremor(audio, sr)
            sighs = self.detect_sighs(audio, sr)
            voice_cracks = self.detect_voice_cracks(audio, sr)
            hesitations = self.detect_hesitations(audio, sr)
            
            # Calculate sigh intensity (based on count and average prominence)
            sigh_count = len(sighs)
            sigh_intensity = min(1.0, sigh_count / 5.0) if sigh_count > 0 else 0.0
            
            # Calculate voice crack intensity (average of all cracks)
            crack_count = len(voice_cracks)
            if crack_count > 0:
                crack_intensities = [intensity for _, intensity in voice_cracks]
                crack_avg_intensity = np.mean(crack_intensities)
            else:
                crack_avg_intensity = 0.0
            
            # Generate interpretations
            tremor_interpretation = "suppressed_crying" if tremor_detected else "none"
            sigh_interpretation = "emotional_burden" if sigh_count > 0 else "none"
            crack_interpretation = "emotion_breaking_through" if crack_count > 0 else "none"
            
            hesitation_count = hesitations.get('count', 0)
            long_pauses = hesitations.get('long_pauses', 0)
            if long_pauses > 2 or hesitation_count > 5:
                hesitation_interpretation = "uncertainty_or_processing"
            elif hesitation_count > 0:
                hesitation_interpretation = "minor_hesitation"
            else:
                hesitation_interpretation = "none"
            
            # Calculate overall risk
            risk_score = 0.0
            
            if tremor_detected:
                risk_score += tremor_intensity * 0.3
            if sigh_count > 0:
                risk_score += sigh_intensity * 0.25
            if crack_count > 0:
                risk_score += crack_avg_intensity * 0.2
            if long_pauses > 2 or hesitation_count > 5:
                risk_score += 0.25
            
            # Determine risk level
            if risk_score >= 0.7:
                overall_risk = "high"
                interpretation = "significant_emotional_suppression"
            elif risk_score >= 0.5:
                overall_risk = "medium-high"
                interpretation = "moderate_emotional_suppression"
            elif risk_score >= 0.3:
                overall_risk = "medium"
                interpretation = "mild_emotional_suppression"
            else:
                overall_risk = "low"
                interpretation = "minimal_emotional_suppression"
            
            # Build result dictionary matching backlog example format
            result = {
                "tremor": {
                    "detected": tremor_detected,
                    "intensity": float(tremor_intensity),
                    "interpretation": tremor_interpretation
                },
                "sighs": {
                    "count": sigh_count,
                    "intensity": float(sigh_intensity),
                    "interpretation": sigh_interpretation
                },
                "voice_cracks": {
                    "count": crack_count,
                    "intensity": float(crack_avg_intensity),
                    "interpretation": crack_interpretation
                },
                "hesitations": {
                    "count": hesitation_count,
                    "average_duration": float(hesitations.get('avg_duration', 0.0)),
                    "interpretation": hesitation_interpretation
                },
                "overall_risk": overall_risk,
                "interpretation": interpretation
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing micro-moments: {str(e)}")
            # Return safe default
            return {
                "tremor": {
                    "detected": False,
                    "intensity": 0.0,
                    "interpretation": "none"
                },
                "sighs": {
                    "count": 0,
                    "intensity": 0.0,
                    "interpretation": "none"
                },
                "voice_cracks": {
                    "count": 0,
                    "intensity": 0.0,
                    "interpretation": "none"
                },
                "hesitations": {
                    "count": 0,
                    "average_duration": 0.0,
                    "interpretation": "none"
                },
                "overall_risk": "low",
                "interpretation": "error"
            }

