#!/usr/bin/env python3
"""
Telegram Tag Bot - Main Entry Point
A comprehensive Telegram bot for group management with tagging, AFK status, admin system, and broadcasting features.
"""

import os
import logging
import sys
import asyncio
from bot import TelegramTagBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Get bot token from environment variable
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
            return
        
        # Create and start the bot
        bot = TelegramTagBot(bot_token)
        logger.info("Starting Telegram Tag Bot...")
        bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()
