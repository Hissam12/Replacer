#!/usr/bin/env python3
import argparse
import logging
import signal
import sys
import time
import os

# Disable pyautogui fail-safe (prevents crash when mouse hits corner)
import pyautogui
pyautogui.FAILSAFE = False

import config
from discord_controller import DiscordController
from scheduler import CheckScheduler
from mouse_mover import MouseMover

# Setup logging
LOG_FILE = os.path.join(os.path.dirname(__file__), 'autocheck.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global references for cleanup
scheduler = None
mouse_mover = None


def signal_handler(_signum, _frame):
    """Handle shutdown signals gracefully"""
    logger.info("Shutdown signal received (Ctrl+C)")
    cleanup()
    sys.exit(0)


def cleanup():
    """Clean up resources"""
    global scheduler, mouse_mover
    logger.info("Cleaning up...")
    if scheduler:
        scheduler.shutdown()
    if mouse_mover:
        mouse_mover.stop()


def test_mode(discord):
    """Test mode - sends check in message immediately"""
    logger.info("=== TEST MODE ===")
    logger.info("Sending 'check in' in 3 seconds...")
    logger.info("Make sure Discord is open!")
    time.sleep(3)

    success = discord.send_message(config.CHECK_IN_MESSAGE)
    if success:
        logger.info("Test successful!")
    else:
        logger.error("Test failed. Check accessibility permissions.")
    return success


def main():
    global scheduler, mouse_mover

    # Parse arguments
    parser = argparse.ArgumentParser(description='Discord Auto Check-in/out')
    parser.add_argument('--test', action='store_true', help='Run in test mode (send message immediately)')
    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check configuration
    if config.GUILD_ID == "YOUR_GUILD_ID" or config.CHANNEL_ID == "YOUR_CHANNEL_ID":
        logger.error("Please update config.py with your Guild ID and Channel ID!")
        logger.error("See config.py for instructions on how to get these.")
        sys.exit(1)

    logger.info("=" * 50)
    logger.info("Discord Auto Check-in/out Starting")
    logger.info("=" * 50)
    logger.info(f"Timezone: {config.TIMEZONE}")
    logger.info(f"Check-in: {config.CHECK_IN_HOUR:02d}:{config.CHECK_IN_MINUTE:02d} (Mon-Fri)")
    logger.info(f"Check-out: {config.CHECK_OUT_HOUR:02d}:{config.CHECK_OUT_MINUTE:02d} (Mon-Fri)")
    logger.info(f"Log file: {LOG_FILE}")

    # Initialize Discord controller
    discord = DiscordController(
        config.GUILD_ID,
        config.CHANNEL_ID,
        config.TYPING_INTERVAL
    )

    # Test mode
    if args.test:
        success = test_mode(discord)
        sys.exit(0 if success else 1)

    # Initialize scheduler and mouse mover
    scheduler = CheckScheduler(discord, config)
    mouse_mover = MouseMover(radius=20)

    # Start services
    scheduler.start()
    mouse_mover.start()

    logger.info("=" * 50)
    logger.info("All services running. Press Ctrl+C to stop.")
    logger.info("=" * 50)

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == '__main__':
    main()
