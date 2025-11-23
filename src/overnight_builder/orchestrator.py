"""
Overnight Builder Orchestrator

Main orchestrator for nightly interface builds.
Coordinates all components to generate personalized UIs for all active users.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.pattern_storage import PatternStorageService
from pattern_analysis.pattern_aggregator import PatternAggregator, AggregatedPatterns
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
            logger.error(f"Failed to build interface for user {user_id}: {e}")
            return {
                'status': 'failed',
                'user_id': user_id,
                'error': str(e)
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
        from pattern_analysis.pattern_aggregator import (
            EmotionalPattern,
            DissonanceResult,
            CulturalContext,
            TriggerProfile,
            CopingProfile,
            BaselineProfile,
            RiskAssessment,
            MentalHealthProfile
        )

        # Reconstruct AggregatedPatterns from dict
        # This is a simplified version - real implementation would be more robust
        return AggregatedPatterns(
            emotional_patterns=EmotionalPattern(**patterns_dict.get('emotional_patterns', {})),
            current_dissonance=DissonanceResult(**patterns_dict.get('current_dissonance', {})),
            cultural_context=CulturalContext(**patterns_dict.get('cultural_context', {})),
            triggers=TriggerProfile(**patterns_dict.get('triggers', {})),
            coping_profile=CopingProfile(**patterns_dict.get('coping_profile', {})),
            baseline=BaselineProfile(**patterns_dict.get('baseline', {})),
            current_risk=RiskAssessment(**patterns_dict.get('current_risk', {})),
            mental_health_profile=MentalHealthProfile(**patterns_dict.get('mental_health_profile', {}))
        )
