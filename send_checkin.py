#!/usr/bin/env python3
"""Standalone check-in script for launchd scheduling"""
import sys
sys.path.insert(0, '/Users/hissam/Desktop/projects/auto_check')

import config
from discord_controller import DiscordController

discord = DiscordController(config.GUILD_ID, config.CHANNEL_ID, config.TYPING_INTERVAL)
discord.send_message(config.CHECK_IN_MESSAGE)
