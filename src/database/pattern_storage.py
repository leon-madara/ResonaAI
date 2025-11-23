"""
Pattern Storage Service

Handles storing and retrieving patterns from database
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
import json

from .models import (
    User, UserPattern, VoiceBaseline, VoiceSession,
    InterfaceConfig, InterfaceChange, RiskAlert,
    PatternHistory
)
from ..pattern_analysis.pattern_aggregator import AggregatedPatterns

class PatternStorageService:
    """
    Service for storing and retrieving patterns
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    # ========================================================================
    # STORE PATTERNS
    # ========================================================================

    async def store_patterns(
        self,
        user_id: str,
        patterns: AggregatedPatterns
    ) -> UserPattern:
        """
        Store aggregated patterns to database

        Args:
            user_id: User identifier
            patterns: AggregatedPatterns from PatternAggregator

        Returns:
            UserPattern database record
        """
        # Get current version
        current = self.db.query(UserPattern).filter(
            and_(
                UserPattern.user_id == user_id,
                UserPattern.is_current == True
            )
        ).first()

        next_version = (current.version + 1) if current else 1

        # Create new pattern record
        pattern_record = UserPattern(
            user_id=user_id,
            version=next_version,
            sessions_analyzed=patterns.sessions_analyzed,
            data_confidence=patterns.data_confidence,

            # Emotional patterns
            primary_emotions=patterns.emotional_patterns.primary_emotions,
            emotion_distribution=patterns.emotional_patterns.emotion_distribution,
            temporal_patterns=patterns.emotional_patterns.temporal_patterns,
            trajectory=patterns.emotional_patterns.trajectory,
            trajectory_confidence=patterns.emotional_patterns.trajectory_confidence,
            variability_score=patterns.emotional_patterns.variability_score,
            recent_shift=patterns.emotional_patterns.recent_shift,

            # Cultural context
            primary_language=patterns.cultural_context.primary_language,
            code_switching=patterns.cultural_context.code_switching_detected,
            code_switching_pattern=patterns.cultural_context.code_switching_pattern,
            deflection_phrases=patterns.cultural_context.deflection_phrases_used,
            deflection_frequency=patterns.cultural_context.deflection_frequency,
            stoicism_level=patterns.cultural_context.stoicism_level,
            cultural_stressors=patterns.cultural_context.cultural_stressors,
            communication_style=patterns.cultural_context.recommended_approach,

            # Triggers
            triggers=self._serialize_triggers(patterns.triggers),
            trigger_count=patterns.triggers.trigger_count,
            most_severe_trigger=patterns.triggers.most_severe_trigger,
            trigger_combinations=patterns.triggers.trigger_combinations,

            # Coping
            effective_strategies=self._serialize_coping(patterns.coping_profile.effective_strategies),
            ineffective_strategies=self._serialize_coping(patterns.coping_profile.ineffective_strategies),
            untried_suggestions=patterns.coping_profile.untried_suggestions,
            coping_consistency=patterns.coping_profile.coping_consistency,
            primary_coping_style=patterns.coping_profile.primary_coping_style,

            # Current state
            current_dissonance=self._serialize_dissonance(patterns.current_dissonance) if patterns.current_dissonance else None,
            current_risk_level=patterns.current_risk.risk_level,
            current_risk_score=patterns.current_risk.risk_score,
            current_risk_factors=patterns.current_risk.risk_factors,

            # Mental health profile
            primary_concerns=patterns.mental_health_profile.primary_concerns,
            current_state=patterns.mental_health_profile.current_state,
            support_needs=patterns.mental_health_profile.support_needs,
            identified_strengths=patterns.mental_health_profile.identified_strengths,
            identified_challenges=patterns.mental_health_profile.identified_challenges,

            # Metadata
            is_current=True,
            generated_at=patterns.generated_at
        )

        self.db.add(pattern_record)
        self.db.commit()
        self.db.refresh(pattern_record)

        return pattern_record

    async def store_baseline(
        self,
        user_id: str,
        baseline: 'VoiceBaseline'  # From baseline_tracker
    ) -> VoiceBaseline:
        """Store voice baseline"""
        # Get current version
        current = self.db.query(VoiceBaseline).filter(
            and_(
                VoiceBaseline.user_id == user_id,
                VoiceBaseline.is_current == True
            )
        ).first()

        next_version = (current.version + 1) if current else 1

        baseline_record = VoiceBaseline(
            user_id=user_id,
            version=next_version,
            sessions_analyzed=baseline.sessions_analyzed,
            baseline_established=baseline.baseline_established,
            typical_pitch_mean=baseline.typical_pitch_mean,
            typical_pitch_std=baseline.typical_pitch_std,
            typical_pitch_range=baseline.typical_pitch_range,
            typical_energy_mean=baseline.typical_energy_mean,
            typical_energy_std=baseline.typical_energy_std,
            typical_speech_rate=baseline.typical_speech_rate,
            typical_pause_ratio=baseline.typical_pause_ratio,
            typical_prosody_variance=baseline.typical_prosody_variance,
            typical_emotion_distribution=baseline.typical_emotion_distribution,
            stress_markers=baseline.stress_markers,
            is_current=True
        )

        self.db.add(baseline_record)
        self.db.commit()
        self.db.refresh(baseline_record)

        return baseline_record

    # ========================================================================
    # RETRIEVE PATTERNS
    # ========================================================================

    async def get_current_patterns(
        self,
        user_id: str
    ) -> Optional[Dict]:
        """
        Get current patterns for user

        Returns: Dict with patterns, baseline, and config
        """
        # Get current pattern
        pattern = self.db.query(UserPattern).filter(
            and_(
                UserPattern.user_id == user_id,
                UserPattern.is_current == True
            )
        ).first()

        if not pattern:
            return None

        # Get current baseline
        baseline = self.db.query(VoiceBaseline).filter(
            and_(
                VoiceBaseline.user_id == user_id,
                VoiceBaseline.is_current == True
            )
        ).first()

        # Get current config
        config = self.db.query(InterfaceConfig).filter(
            and_(
                InterfaceConfig.user_id == user_id,
                InterfaceConfig.is_current == True
            )
        ).first()

        return {
            'pattern': self._pattern_to_dict(pattern),
            'baseline': self._baseline_to_dict(baseline) if baseline else None,
            'config': self._config_to_dict(config) if config else None
        }

    async def get_users_for_overnight_build(self) -> List[Dict]:
        """
        Get all users who had activity in last 24 hours

        Returns: List of user data for overnight processing
        """
        # Find users with recent sessions
        cutoff = datetime.now() - timedelta(hours=24)

        users_with_activity = self.db.query(
            User.user_id,
            User.anonymous_id,
            User.timezone
        ).join(
            VoiceSession,
            User.user_id == VoiceSession.user_id
        ).filter(
            and_(
                User.account_status == 'active',
                VoiceSession.session_start > cutoff,
                VoiceSession.processed == True
            )
        ).distinct().all()

        return [
            {
                'user_id': str(u.user_id),
                'anonymous_id': u.anonymous_id,
                'timezone': u.timezone
            }
            for u in users_with_activity
        ]

    async def get_session_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get session history for pattern analysis

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns: List of session dictionaries
        """
        cutoff = datetime.now() - timedelta(days=days)

        sessions = self.db.query(VoiceSession).filter(
            and_(
                VoiceSession.user_id == user_id,
                VoiceSession.session_start > cutoff,
                VoiceSession.processed == True
            )
        ).order_by(VoiceSession.session_start.asc()).all()

        return [self._session_to_dict(s) for s in sessions]

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _serialize_triggers(self, trigger_pattern) -> Dict:
        """Convert TriggerPattern to JSON"""
        return {
            'triggers': [
                {
                    'topic': t.topic,
                    'frequency': t.frequency,
                    'severity': t.severity,
                    'voice_markers': t.voice_markers,
                    'sample_phrases': t.sample_phrases
                }
                for t in trigger_pattern.triggers
            ]
        }

    def _serialize_coping(self, strategies: List) -> Dict:
        """Convert coping strategies to JSON"""
        return {
            'strategies': [
                {
                    'name': s.name,
                    'category': s.category,
                    'effectiveness_score': s.effectiveness_score,
                    'evidence': s.evidence,
                    'mention_count': s.mention_count
                }
                for s in strategies
            ]
        }

    def _serialize_dissonance(self, dissonance) -> Dict:
        """Convert DissonanceResult to JSON"""
        return {
            'stated_emotion': dissonance.stated_emotion,
            'voice_emotion': dissonance.voice_emotion,
            'dissonance_score': dissonance.dissonance_score,
            'dissonance_type': dissonance.dissonance_type,
            'truth_signal': dissonance.truth_signal,
            'risk_level': dissonance.risk_level,
            'risk_interpretation': dissonance.risk_interpretation,
            'micro_moments': dissonance.micro_moments,
            'baseline_deviation': dissonance.baseline_deviation
        }

    def _pattern_to_dict(self, pattern: UserPattern) -> Dict:
        """Convert UserPattern to dict"""
        return {
            'pattern_id': str(pattern.pattern_id),
            'user_id': str(pattern.user_id),
            'version': pattern.version,
            'generated_at': pattern.generated_at.isoformat(),
            'sessions_analyzed': pattern.sessions_analyzed,
            'data_confidence': pattern.data_confidence,
            'emotional_patterns': {
                'primary_emotions': pattern.primary_emotions,
                'emotion_distribution': pattern.emotion_distribution,
                'temporal_patterns': pattern.temporal_patterns,
                'trajectory': pattern.trajectory,
                'trajectory_confidence': pattern.trajectory_confidence,
                'variability_score': pattern.variability_score,
                'recent_shift': pattern.recent_shift
            },
            'cultural_context': {
                'primary_language': pattern.primary_language,
                'code_switching': pattern.code_switching,
                'code_switching_pattern': pattern.code_switching_pattern,
                'deflection_phrases': pattern.deflection_phrases,
                'deflection_frequency': pattern.deflection_frequency,
                'stoicism_level': pattern.stoicism_level,
                'cultural_stressors': pattern.cultural_stressors,
                'communication_style': pattern.communication_style
            },
            'triggers': pattern.triggers,
            'coping': {
                'effective_strategies': pattern.effective_strategies,
                'ineffective_strategies': pattern.ineffective_strategies,
                'untried_suggestions': pattern.untried_suggestions,
                'coping_consistency': pattern.coping_consistency,
                'primary_coping_style': pattern.primary_coping_style
            },
            'current_state': {
                'dissonance': pattern.current_dissonance,
                'risk_level': pattern.current_risk_level,
                'risk_score': pattern.current_risk_score,
                'risk_factors': pattern.current_risk_factors
            },
            'mental_health_profile': {
                'primary_concerns': pattern.primary_concerns,
                'current_state': pattern.current_state,
                'support_needs': pattern.support_needs,
                'identified_strengths': pattern.identified_strengths,
                'identified_challenges': pattern.identified_challenges
            }
        }

    def _baseline_to_dict(self, baseline: VoiceBaseline) -> Dict:
        """Convert VoiceBaseline to dict"""
        return {
            'baseline_id': str(baseline.baseline_id),
            'user_id': str(baseline.user_id),
            'version': baseline.version,
            'established': baseline.baseline_established,
            'sessions_analyzed': baseline.sessions_analyzed,
            'prosodic': {
                'typical_pitch_mean': baseline.typical_pitch_mean,
                'typical_pitch_std': baseline.typical_pitch_std,
                'typical_pitch_range': baseline.typical_pitch_range
            },
            'energy': {
                'typical_energy_mean': baseline.typical_energy_mean,
                'typical_energy_std': baseline.typical_energy_std
            },
            'temporal': {
                'typical_speech_rate': baseline.typical_speech_rate,
                'typical_pause_ratio': baseline.typical_pause_ratio
            },
            'emotional': {
                'typical_prosody_variance': baseline.typical_prosody_variance,
                'typical_emotion_distribution': baseline.typical_emotion_distribution
            },
            'stress_markers': baseline.stress_markers
        }

    def _config_to_dict(self, config: InterfaceConfig) -> Dict:
        """Convert InterfaceConfig to dict"""
        return {
            'config_id': str(config.config_id),
            'version': config.version,
            'generated_at': config.generated_at.isoformat(),
            'theme': config.theme,
            'primary_components': config.primary_components,
            'hidden_components': config.hidden_components,
            'crisis_prominence': config.crisis_prominence,
            'deployed': config.deployed,
            'ui_config_encrypted': config.ui_config_encrypted
        }

    def _session_to_dict(self, session: VoiceSession) -> Dict:
        """Convert VoiceSession to dict"""
        return {
            'session_id': str(session.session_id),
            'user_id': str(session.user_id),
            'timestamp': session.session_start.isoformat(),
            'duration_seconds': session.duration_seconds,
            'voice_emotion': session.voice_emotion,
            'emotion_confidence': session.emotion_confidence,
            'voice_features': session.voice_features,
            'transcript': None,  # Encrypted, not returned
            'language': session.transcript_language
        }
