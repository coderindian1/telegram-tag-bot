#!/usr/bin/env python3
"""
Simplified startup for Render deployment
"""
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    try:
        # Check environment
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not found")
            sys.exit(1)
            
        logger.info("Importing bot...")
        
        # Direct import and run
        from bot import TelegramTagBot
        
        logger.info("Starting bot...")
        bot = TelegramTagBot(token)
        bot.run()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()