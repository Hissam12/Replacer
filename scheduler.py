"""Scheduler for check-in/check-out jobs using APScheduler"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class CheckScheduler:
    def __init__(self, discord_controller, config):
        """
        Args:
            discord_controller: DiscordController instance
            config: Config module with schedule settings
        """
        self.discord = discord_controller
        self.config = config
        self.scheduler = BackgroundScheduler(timezone=config.TIMEZONE)

    def _check_in_job(self):
        """Job executed at check-in time"""
        logger.info("=== CHECK-IN JOB TRIGGERED ===")
        try:
            success = self.discord.send_message(self.config.CHECK_IN_MESSAGE)
            if success:
                logger.info("Check-in completed successfully")
            else:
                logger.error("Check-in failed")
        except Exception as e:
            logger.error(f"Check-in job error: {e}")

    def _check_out_job(self):
        """Job executed at check-out time"""
        logger.info("=== CHECK-OUT JOB TRIGGERED ===")
        try:
            success = self.discord.send_message(self.config.CHECK_OUT_MESSAGE)
            if success:
                logger.info("Check-out completed successfully")
            else:
                logger.error("Check-out failed")
        except Exception as e:
            logger.error(f"Check-out job error: {e}")

    def setup_jobs(self):
        """Configure scheduled jobs - weekdays only"""
        # Check-in at configured time, Monday-Friday
        self.scheduler.add_job(
            self._check_in_job,
            CronTrigger(
                hour=self.config.CHECK_IN_HOUR,
                minute=self.config.CHECK_IN_MINUTE,
                day_of_week='mon-fri'
            ),
            id='check_in',
            name='Daily Check-In',
            replace_existing=True
        )
        logger.info(f"Check-in scheduled: {self.config.CHECK_IN_HOUR:02d}:{self.config.CHECK_IN_MINUTE:02d} (Mon-Fri)")

        # Check-out at configured time, Monday-Friday
        self.scheduler.add_job(
            self._check_out_job,
            CronTrigger(
                hour=self.config.CHECK_OUT_HOUR,
                minute=self.config.CHECK_OUT_MINUTE,
                day_of_week='mon-fri'
            ),
            id='check_out',
            name='Daily Check-Out',
            replace_existing=True
        )
        logger.info(f"Check-out scheduled: {self.config.CHECK_OUT_HOUR:02d}:{self.config.CHECK_OUT_MINUTE:02d} (Mon-Fri)")

    def start(self):
        """Start the scheduler"""
        self.setup_jobs()
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        """Gracefully shutdown the scheduler"""
        self.scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")
