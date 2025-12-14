"""Deterministic tests for the local audio feature extraction pipeline.

These tests avoid external providers and model downloads.
"""

import io

import numpy as np
import soundfile as sf

from src.audio_processor import AudioProcessor
from src.config import settings


def _sine_wave(*, frequency_hz: float, duration_s: float, sample_rate: int) -> np.ndarray:
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    return 0.5 * np.sin(2.0 * np.pi * frequency_hz * t).astype(np.float32)


def test_feature_extraction_is_deterministic_for_fixed_input():
    # Make preprocessing as deterministic as possible.
    settings.NOISE_REDUCTION = False
    settings.NORMALIZATION = True

    processor = AudioProcessor()

    audio = _sine_wave(frequency_hz=440.0, duration_s=2.0, sample_rate=settings.SAMPLE_RATE)

    buf = io.BytesIO()
    sf.write(buf, audio, settings.SAMPLE_RATE, format="WAV")
    audio_bytes = buf.getvalue()

    processed = processor.preprocess_audio(audio_bytes)
    features = processor.extract_features(processed)

    assert "mfcc" in features
    assert "spectral" in features
    assert "prosodic" in features
    assert "temporal" in features
    assert "statistical" in features

    # MFCC is (time, n_mfcc)
    assert features["mfcc"].shape[1] == 13

    # Prosodic pitch should be in a reasonable range around 440Hz.
    pitch_mean = float(features["prosodic"].get("pitch_mean", 0.0))
    assert 350.0 <= pitch_mean <= 550.0
