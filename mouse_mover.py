"""Anti-idle mouse mover - continuous circle, pauses when user is active"""

import threading
import time
import logging
import math
import pyautogui

logger = logging.getLogger(__name__)


class MouseMover:
    def __init__(self, radius: int = 20, idle_check: int = 3):
        self.radius = radius
        self.idle_check = idle_check  # seconds to wait before moving
        self.running = False
        self.thread = None

    def _run_loop(self):
        """Continuously move mouse in circles when user is idle"""
        logger.info("Mouse mover started")

        while self.running:
            # Check if user is idle
            pos1 = pyautogui.position()
            time.sleep(self.idle_check)
            pos2 = pyautogui.position()

            if not self.running:
                break

            if pos1 != pos2:
                # User moved, check again
                continue

            # User is idle - start continuous circle
            anchor_x, anchor_y = pyautogui.position()
            angle = 0

            while self.running:
                x = anchor_x + int(self.radius * math.cos(angle))
                y = anchor_y + int(self.radius * math.sin(angle))

                try:
                    pyautogui.moveTo(x, y, duration=0.02)
                except:
                    break

                # Check if user moved
                current = pyautogui.position()
                if abs(current[0] - x) > 5 or abs(current[1] - y) > 5:
                    # User took control, wait for idle again
                    break

                angle += 0.2
                if angle >= 2 * math.pi:
                    angle = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Mouse mover thread started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Mouse mover stopped")
