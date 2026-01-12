"""
Property-Based Test for Data Generation Completeness

This module tests Property 1: Data Generation Completeness
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import sys
import tempfile
import shutil
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.demo_data_generator.models import DemoConfig, UserProfile, EmotionType
from scripts.demo_data_generator.generators.user_generator import UserGenerator


@st.composite
def demo_config_strategy(draw):
    num_users = draw(st.integers(min_value=5, max_value=20))
    return DemoConfig(
        num_users=num_users,
        output_directory=tempfile.mkdtemp()
    )


@settings(max_examples=100, deadline=None)
@given(config=demo_config_strategy())
def test_user_profile_generation_completeness(config: DemoConfig):
    """Feature: demo-data-generator, Property 1: Data Generation Completeness"""
    user_generator = UserGenerator(config)
    profiles: List[UserProfile] = []
    
    for i in range(config.num_users):
        user_id = f"test_user_{i+1:03d}"
        profile = user_generator.generate_user_profile(user_id)
        profiles.append(profile)
    
    assert len(profiles) == config.num_users
    
    for profile in profiles:
        assert profile.id
        assert 13 <= profile.age <= 100
        assert profile.gender in ["male", "female"]
        assert profile.location
        assert profile.baseline_data
        assert profile.baseline_data.voice_patterns.average_pitch > 0
        assert len(profile.session_history) >= 1
    
    if config.num_users >= 5:
        assert user_generator.ensure_demographic_diversity(profiles)
    
    if Path(config.output_directory).exists():
        shutil.rmtree(config.output_directory)
