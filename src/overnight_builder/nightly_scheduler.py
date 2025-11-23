"""
Nightly Scheduler

Schedules and runs overnight interface builds using cron-like scheduling.
Supports multiple timezones to build interfaces during local night hours.
"""

import asyncio
import schedule
import time
from datetime import datetime, time as dt_time
from typing import Optional, Callable, Dict, List
import logging
import pytz

from .orchestrator import OvernightBuilder

logger = logging.getLogger(__name__)


class NightlyScheduler:
    """
    Schedules nightly interface builds across timezones

    Strategy:
    - Runs builds at 3 AM local time for each timezone
    - Stagger builds to avoid server load spikes
    - East Africa (UTC+3) at 00:00 UTC
    - West Africa (UTC+0) at 03:00 UTC
    - Etc.
    """

    def __init__(
        self,
        builder: Optional[OvernightBuilder] = None,
        timezones: Optional[List[str]] = None
    ):
        """
        Initialize scheduler

        Args:
            builder: OvernightBuilder instance (creates default if None)
            timezones: List of timezones to schedule for (default: East African timezones)
        """
        self.builder = builder or OvernightBuilder()

        # Default to East African timezones
        self.timezones = timezones or [
            'Africa/Nairobi',      # Kenya, Uganda (UTC+3)
            'Africa/Dar_es_Salaam', # Tanzania (UTC+3)
            'Africa/Kampala',      # Uganda (UTC+3)
            'Africa/Addis_Ababa',  # Ethiopia (UTC+3)
            'Africa/Kigali',       # Rwanda (UTC+2)
        ]

        self.running = False

    def schedule_builds(self) -> None:
        """
        Schedule nightly builds for all configured timezones

        Builds run at 3:00 AM local time for each timezone
        """

        for tz_name in self.timezones:
            # Calculate UTC time for 3:00 AM in this timezone
            utc_time = self._calculate_utc_time_for_local_3am(tz_name)

            # Schedule the build
            schedule.every().day.at(utc_time).do(
                self._run_build_async,
                timezone=tz_name
            )

            logger.info(f"Scheduled nightly build for {tz_name} at {utc_time} UTC (3:00 AM local)")

    def _calculate_utc_time_for_local_3am(self, timezone_name: str) -> str:
        """
        Calculate UTC time for 3:00 AM in given timezone

        Args:
            timezone_name: Timezone name (e.g., 'Africa/Nairobi')

        Returns:
            UTC time string in HH:MM format
        """

        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)

        # Create 3:00 AM time in this timezone
        local_3am = now.replace(hour=3, minute=0, second=0, microsecond=0)

        # Convert to UTC
        utc_time = local_3am.astimezone(pytz.UTC)

        return utc_time.strftime("%H:%M")

    def _run_build_async(self, timezone: str) -> None:
        """
        Run async build in sync context (for schedule library)

        Args:
            timezone: Timezone to build for
        """

        logger.info(f"Starting scheduled build for {timezone}")

        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async build
            result = loop.run_until_complete(
                self.builder.run_nightly_build(target_timezone=timezone)
            )

            logger.info(f"Build complete for {timezone}: {result}")

        except Exception as e:
            logger.error(f"Build failed for {timezone}: {e}")

        finally:
            loop.close()

    def run_forever(self) -> None:
        """
        Run scheduler forever (blocking)

        Use this for production deployment
        """

        logger.info("Starting nightly scheduler (running forever)")
        self.running = True

        # Schedule all builds
        self.schedule_builds()

        # Run scheduler loop
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_once_now(self, timezone: Optional[str] = None, dry_run: bool = False) -> Dict:
        """
        Run build immediately (for testing)

        Args:
            timezone: Optional timezone filter
            dry_run: If True, don't save configs

        Returns:
            Build result
        """

        logger.info(f"Running immediate build (timezone={timezone}, dry_run={dry_run})")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                self.builder.run_nightly_build(
                    target_timezone=timezone,
                    dry_run=dry_run
                )
            )
            return result

        finally:
            loop.close()

    def stop(self) -> None:
        """Stop the scheduler"""
        logger.info("Stopping nightly scheduler")
        self.running = False
        schedule.clear()

    def add_timezone(self, timezone_name: str) -> None:
        """
        Add a new timezone to schedule

        Args:
            timezone_name: Timezone name (e.g., 'Africa/Lagos')
        """

        if timezone_name not in self.timezones:
            self.timezones.append(timezone_name)

            # If already running, schedule this new timezone
            if self.running:
                utc_time = self._calculate_utc_time_for_local_3am(timezone_name)
                schedule.every().day.at(utc_time).do(
                    self._run_build_async,
                    timezone=timezone_name
                )
                logger.info(f"Added and scheduled {timezone_name} at {utc_time} UTC")

    def get_next_build_times(self) -> Dict[str, str]:
        """
        Get next scheduled build time for each timezone

        Returns:
            Dict mapping timezone to next build time
        """

        next_times = {}

        for tz_name in self.timezones:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)

            # Next 3:00 AM
            next_3am = now.replace(hour=3, minute=0, second=0, microsecond=0)

            # If it's already past 3 AM today, schedule for tomorrow
            if now.hour >= 3:
                next_3am = next_3am.replace(day=now.day + 1)

            next_times[tz_name] = next_3am.strftime("%Y-%m-%d %H:%M %Z")

        return next_times


# ============================================================================
# CLI for running scheduler
# ============================================================================

def main():
    """
    CLI entry point for running the nightly scheduler

    Usage:
        python -m overnight_builder.nightly_scheduler [--once] [--timezone TIMEZONE] [--dry-run]
    """

    import argparse

    parser = argparse.ArgumentParser(description='Run overnight interface builder')
    parser.add_argument('--once', action='store_true', help='Run once immediately instead of scheduling')
    parser.add_argument('--timezone', type=str, help='Filter to specific timezone')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t save configs)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create scheduler
    scheduler = NightlyScheduler()

    if args.once:
        # Run once immediately
        result = scheduler.run_once_now(
            timezone=args.timezone,
            dry_run=args.dry_run
        )
        print(f"\nBuild Result:\n{result}")

    else:
        # Run forever
        try:
            scheduler.run_forever()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            scheduler.stop()


if __name__ == '__main__':
    main()
