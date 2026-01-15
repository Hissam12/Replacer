#!/usr/bin/env python3
"""Continuous circle mouse movement - resumes from where user leaves cursor"""

import math
import time
import pyautogui

pyautogui.FAILSAFE = False

RADIUS = 20
IDLE_CHECK = 3  # seconds to wait before starting

print("Continuous circle mouse mover. Press Ctrl+C to stop.")
print("Move your mouse anytime - it resumes when you stop.")

try:
    while True:
        # Check if user is idle (hasn't moved for 3 seconds)
        pos1 = pyautogui.position()
        time.sleep(IDLE_CHECK)
        pos2 = pyautogui.position()

        if pos1 != pos2:
            # User moved, check again
            continue

        # User is idle - start continuous circle from current position
        anchor_x, anchor_y = pyautogui.position()
        angle = 0

        while True:
            # Calculate next point on circle
            x = anchor_x + int(RADIUS * math.cos(angle))
            y = anchor_y + int(RADIUS * math.sin(angle))

            pyautogui.moveTo(x, y, duration=0.02)

            # Check if user moved the mouse away from expected position
            current = pyautogui.position()
            if abs(current[0] - x) > 5 or abs(current[1] - y) > 5:
                # User took control, break out and wait for idle again
                break

            angle += 0.2  # smooth rotation
            if angle >= 2 * math.pi:
                angle = 0

except KeyboardInterrupt:
    print("\nStopped")
