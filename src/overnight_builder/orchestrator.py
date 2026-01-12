"""
Overnight Builder Orchestrator

Main orchestrator for nightly interface builds.
Coordinates all components to generate personalized UIs for all active users.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from src.database.pattern_storage import PatternStorageService
from src.pattern_analysis.pattern_aggregator import PatternAggregator, AggregatedPatterns
from .ui_config_generator import UIConfigGenerator, UIConfig
from .encryption_service import EncryptionService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OvernightBuilder:
    """
    Orchestrates nightly interface builds for all active users

    Process:
    1. Identify users who need interface rebuild (active in last 24h)
    2. For each user:
       a. Fetch current patterns from database
       b. Fetch previous UI config
       c. Generate new UI config
       d. Detect changes
       e. Encrypt config
       f. Store to database
       g. Store changes for user notification
    3. Generate summary report
    """

    def __init__(
        self,
        pattern_storage: Optional[PatternStorageService] = None,
        ui_generator: Optional[UIConfigGenerator] = None,
        encryption_service: Optional[EncryptionService] = None
    ):
        """
        Initialize orchestrator

        Args:
            pattern_storage: Pattern storage service (creates default if None)
            ui_generator: UI config generator (creates default if None)
            encryption_service: Encryption service (creates default if None)
        """
        self.pattern_storage = pattern_storage or PatternStorageService()
        self.ui_generator = ui_generator or UIConfigGenerator()
        self.encryption_service = encryption_service or EncryptionService()

    async def run_nightly_build(
        self,
        target_timezone: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Run the nightly build process

        Args:
            target_timezone: Timezone to target (e.g., 'Africa/Nairobi')
            dry_run: If True, don't actually save configs (for testing)

        Returns:
            Build summary report
        """

        logger.info(f"Starting nightly build (timezone={target_timezone}, dry_run={dry_run})")

        start_time = datetime.utcnow()

        # 1. Get users needing rebuild
        users = await self.get_users_for_build(target_timezone)
        logger.info(f"Found {len(users)} users for rebuild")

        if not users:
            return {
                'status': 'success',
                'total': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'duration_seconds': 0
            }

        # 2. Build interfaces for all users (parallel)
        results = await asyncio.gather(*[
            self.build_interface_for_user(user, dry_run=dry_run)
            for user in users
        ], return_exceptions=True)

        # 3. Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
        failed = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, dict) and r.get('status') == 'failed'))
        skipped = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'skipped')

        # 4. Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"Nightly build complete: {successful} successful, {failed} failed, {skipped} skipped ({duration:.2f}s)")

        return {
            'status': 'success',
            'total': len(users),
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'duration_seconds': duration,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def build_interface_for_user(
        self,
        user: Dict,
        dry_run: bool = False
    ) -> Dict:
        """
        Build interface for a single user

        Args:
            user: User dict with user_id and metadata
            dry_run: If True, don't save to database

        Returns:
            Build result dict
        """

        user_id = user['user_id']

        try:
            logger.info(f"Building interface for user {user_id}")

            # 1. Fetch current patterns
            patterns_dict = await self.pattern_storage.get_current_patterns(user_id)

            if not patterns_dict:
                logger.warning(f"No patterns found for user {user_id}, skipping")
                return {'status': 'skipped', 'reason': 'no_patterns', 'user_id': user_id}

            # Convert dict to AggregatedPatterns object
            # (Assuming PatternAggregator has a from_dict method)
            patterns = self._patterns_from_dict(patterns_dict)

            # 2. Fetch previous UI config
            previous_config = await self.get_previous_config(user_id)

            # 3. Generate new UI config
            new_config = await self.ui_generator.generate(
                user_id=user_id,
                patterns=patterns,
                previous_config=previous_config
            )

            # 4. Convert config to dict
            config_dict = self.ui_generator.config_to_dict(new_config)

            if dry_run:
                logger.info(f"[DRY RUN] Would save config for user {user_id}")
                return {
                    'status': 'success',
                    'user_id': user_id,
                    'changes_count': len(new_config.changes),
                    'dry_run': True
                }

            # 5. Encrypt config
            encrypted_config, salt = self.encryption_service.encrypt_for_storage(
                config=config_dict,
                user_id=user_id,
                user_passphrase=user.get('passphrase')  # May be None
            )

            # 6. Store to database
            await self.store_config(
                user_id=user_id,
                encrypted_config=encrypted_config,
                salt=salt,
                metadata={
                    'risk_level': new_config.metadata['risk_level'],
                    'trajectory': new_config.metadata['trajectory'],
                    'changes_count': len(new_config.changes)
                }
            )

            # 7. Store changes for user notification
            if new_config.changes:
                await self.store_changes(user_id, new_config.changes)

            logger.info(f"Successfully built interface for user {user_id} ({len(new_config.changes)} changes)")

            return {
                'status': 'success',
                'user_id': user_id,
                'changes_count': len(new_config.changes),
                'risk_level': new_config.metadata['risk_level']
            }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Failed to build interface for user {user_id}: {e}")
            logger.error(f"Full traceback:\n{error_trace}")
            return {
                'status': 'failed',
                'user_id': user_id,
                'error': str(e),
                'traceback': error_trace
            }

    async def get_users_for_build(
        self,
        target_timezone: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of users who need interface rebuild

        Criteria:
        - Active in last 24 hours (recorded at least one session)
        - Has sufficient patterns (at least 3 sessions total)
        - Not already built today

        Args:
            target_timezone: Optional timezone filter

        Returns:
            List of user dicts
        """

        # Use PatternStorage method
        users = await self.pattern_storage.get_users_for_overnight_build()

        # Filter by timezone if specified
        if target_timezone:
            users = [u for u in users if u.get('timezone') == target_timezone]

        return users

    async def get_previous_config(self, user_id: str) -> Optional[Dict]:
        """
        Get user's previous UI configuration

        Args:
            user_id: User identifier

        Returns:
            Previous config dict or None
        """

        # Query interface_configs table for most recent config
        try:
            # This would use a database method
            # For now, placeholder
            config = await self.pattern_storage.get_latest_interface_config(user_id)
            return config
        except Exception as e:
            logger.warning(f"Could not fetch previous config for {user_id}: {e}")
            return None

    async def store_config(
        self,
        user_id: str,
        encrypted_config: str,
        salt: str,
        metadata: Dict
    ) -> None:
        """
        Store encrypted UI config to database

        Args:
            user_id: User identifier
            encrypted_config: Encrypted config string
            salt: Encryption salt
            metadata: Config metadata
        """

        # Store to interface_configs table
        await self.pattern_storage.store_interface_config(
            user_id=user_id,
            encrypted_config=encrypted_config,
            salt=salt,
            metadata=metadata
        )

    async def store_changes(
        self,
        user_id: str,
        changes: List[Dict]
    ) -> None:
        """
        Store interface changes for user notification

        Args:
            user_id: User identifier
            changes: List of change dicts
        """

        # Store to interface_changes table
        await self.pattern_storage.store_interface_changes(
            user_id=user_id,
            changes=changes
        )

    def _patterns_from_dict(self, patterns_dict: Dict) -> AggregatedPatterns:
        """
        Convert patterns dict to AggregatedPatterns object

        Args:
            patterns_dict: Patterns as dictionary

        Returns:
            AggregatedPatterns object
        """

        # This would use PatternAggregator.from_dict() method
        # For now, placeholder - assumes the dict structure matches AggregatedPatterns
        from src.pattern_analysis.emotional_pattern_analyzer import EmotionalPattern
        from src.pattern_analysis.dissonance_detector import DissonanceResult
        from src.pattern_analysis.cultural_context_analyzer import CulturalContext
        from src.pattern_analysis.trigger_detector import TriggerPattern
        from src.pattern_analysis.coping_effectiveness_tracker import CopingProfile
        from src.pattern_analysis.baseline_tracker import VoiceBaseline
        from src.pattern_analysis.risk_assessment_engine import RiskAssessment
        from src.pattern_analysis.mental_health_profiler import MentalHealthProfile

        # Reconstruct AggregatedPatterns from dict
        # Map cultural_context fields properly
        cultural_dict = patterns_dict.get('cultural_context', {})
        cultural_context = CulturalContext(
            primary_language=cultural_dict.get('primary_language', 'english'),
            code_switching_detected=cultural_dict.get('code_switching', False),
            code_switching_pattern=cultural_dict.get('code_switching_pattern'),
            deflection_phrases_used=cultural_dict.get('deflection_phrases', []),
            deflection_frequency=cultural_dict.get('deflection_frequency', 0.0),
            stoicism_level=cultural_dict.get('stoicism_level', 'medium'),
            stoicism_markers=[],
            cultural_stressors=cultural_dict.get('cultural_stressors', []),
            recommended_approach=cultural_dict.get('communication_style', 'balanced')
        )
        
        # Map coping profile fields
        coping_dict = patterns_dict.get('coping', {})
        coping_profile = CopingProfile(
            effective_strategies=coping_dict.get('effective_strategies', {}),
            ineffective_strategies=coping_dict.get('ineffective_strategies', {}),
            untried_suggestions=coping_dict.get('untried_suggestions', []),
            coping_consistency=coping_dict.get('coping_consistency', 0.5),
            primary_coping_style=coping_dict.get('primary_coping_style', 'unknown')
        )
        
        # Map current risk from current_state
        current_state = patterns_dict.get('current_state', {})
        current_risk = RiskAssessment(
            risk_level=current_state.get('risk_level', 'unknown'),
            risk_score=current_state.get('risk_score', 0.0),
            risk_factors=current_state.get('risk_factors', []),
            protective_factors=[],
            trajectory='stable',
            recommended_action='monitor',
            alert_counselor=False
        )
        
        # Map emotional patterns
        emotional_dict = patterns_dict.get('emotional_patterns', {})
        emotional_patterns = EmotionalPattern(
            primary_emotions=emotional_dict.get('primary_emotions', []),
            emotion_distribution=emotional_dict.get('emotion_distribution', {}),
            temporal_patterns=emotional_dict.get('temporal_patterns', {}),
            trajectory=emotional_dict.get('trajectory', 'insufficient_data'),
            trajectory_confidence=emotional_dict.get('trajectory_confidence', 0.0),
            variability_score=emotional_dict.get('variability_score', 0.5),
            recent_shift=emotional_dict.get('recent_shift')
        )
        
        # Map mental health profile
        mh_dict = patterns_dict.get('mental_health_profile', {})
        mental_health_profile = MentalHealthProfile(
            user_id=patterns_dict.get('user_id'),
            primary_concerns=mh_dict.get('primary_concerns', []),
            secondary_concerns=[],
            current_state=mh_dict.get('current_state', 'unknown'),
            current_risk='low',
            support_needs=mh_dict.get('support_needs', []),
            communication_style='balanced',
            effective_coping=[],
            ineffective_patterns=[],
            identified_strengths=mh_dict.get('identified_strengths', []),
            identified_challenges=mh_dict.get('identified_challenges', [])
        )
        
        # Map trigger pattern
        trigger_dict = patterns_dict.get('triggers', {})
        if isinstance(trigger_dict, dict) and 'triggers' in trigger_dict:
            # Already has the right structure
            trigger_pattern = TriggerPattern(**trigger_dict)
        else:
            # Need to extract from the JSON structure
            trigger_pattern = TriggerPattern(
                triggers=trigger_dict.get('triggers', []),
                trigger_count=trigger_dict.get('trigger_count', 0),
                most_severe_trigger=trigger_dict.get('most_severe_trigger'),
                trigger_combinations=trigger_dict.get('trigger_combinations', [])
            )
        
        return AggregatedPatterns(
            emotional_patterns=emotional_patterns,
            current_dissonance=DissonanceResult(**patterns_dict.get('current_dissonance', {})) if patterns_dict.get('current_dissonance') else None,
            cultural_context=cultural_context,
            triggers=trigger_pattern,
            coping_profile=coping_profile,
            voice_baseline=VoiceBaseline(
                user_id=patterns_dict.get('user_id'),
                sessions_analyzed=patterns_dict.get('sessions_analyzed', 0),
                baseline_established=True,
                typical_pitch_mean=150.0,
                typical_pitch_std=20.0,
                typical_pitch_range=100.0,
                typical_energy_mean=0.5,
                typical_energy_std=0.1,
                typical_speech_rate=3.0,
                typical_pause_ratio=0.2,
                typical_prosody_variance=0.5,
                typical_emotion_distribution={'neutral': 0.5, 'happy': 0.3, 'sad': 0.2},
                stress_markers={}
            ),
            current_risk=current_risk,
            mental_health_profile=mental_health_profile,
            user_id=patterns_dict.get('user_id'),
            generated_at=patterns_dict.get('generated_at'),
            sessions_analyzed=patterns_dict.get('sessions_analyzed', 0),
            data_confidence=patterns_dict.get('data_confidence', 0.0)
        )
