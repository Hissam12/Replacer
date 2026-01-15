"""Discord Desktop App Controller - Handles window focus and message sending"""

import subprocess
import time
import logging
import pyautogui

logger = logging.getLogger(__name__)


class DiscordController:
    def __init__(self, guild_id: str, channel_id: str, typing_interval: float = 0.08):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.typing_interval = typing_interval
        self.discord_url = f"discord://-/channels/{guild_id}/{channel_id}"

    def is_discord_running(self) -> bool:
        """Check if Discord is running"""
        script = '''
        tell application "System Events"
            return (name of processes) contains "Discord"
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True
        )
        return result.stdout.strip() == 'true'

    def launch_discord(self):
        """Launch Discord if not running"""
        logger.info("Launching Discord...")
        subprocess.run(['open', '-a', 'Discord'])
        time.sleep(5)

    def activate_discord(self):
        """Bring Discord window to foreground"""
        subprocess.run(['osascript', '-e', 'tell application "Discord" to activate'])
        time.sleep(0.5)

    def navigate_to_channel(self):
        """Navigate to the specific channel using URL scheme"""
        logger.info(f"Navigating to channel: {self.discord_url}")
        subprocess.run(['open', self.discord_url])
        time.sleep(2)

    def is_discord_frontmost(self) -> bool:
        """Check if Discord is the active window"""
        script = '''
        tell application "System Events"
            return name of first application process whose frontmost is true
        end tell
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True
        )
        return 'Discord' in result.stdout

    def type_message(self, message: str):
        """Type message character by character with human-like delays"""
        pyautogui.write(message, interval=self.typing_interval)

    def press_enter(self):
        """Press Enter to send the message"""
        pyautogui.press('enter')
        time.sleep(0.3)

    def send_message(self, message: str, retries: int = 3) -> bool:
        """Full workflow to send a message to the channel with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{retries} to send: {message}")

                # Ensure Discord is running
                if not self.is_discord_running():
                    logger.warning("Discord not running, launching...")
                    self.launch_discord()

                # Navigate to the channel (this also activates Discord)
                self.navigate_to_channel()
                time.sleep(1.5)

                # Ensure Discord is in the foreground
                self.activate_discord()
                time.sleep(0.5)

                # Verify Discord is frontmost
                if not self.is_discord_frontmost():
                    logger.warning("Discord not in foreground, retrying...")
                    continue

                # Type and send the message
                self.type_message(message)
                self.press_enter()

                logger.info(f"Message sent successfully: {message}")
                return True

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)

        logger.error(f"Failed to send message after {retries} attempts")
        return False
