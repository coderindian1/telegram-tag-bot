#!/usr/bin/env python3
"""
Simple startup script for Render deployment
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    try:
        # Check if bot token exists
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            sys.exit(1)
            
        logger.info("Starting Telegram Tag Bot...")
        
        # Import and run the main bot
        from main import main as bot_main
        bot_main()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()