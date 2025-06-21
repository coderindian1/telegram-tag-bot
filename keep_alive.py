"""
Keep the bot running with automatic restart capabilities
Used for 24/7 deployment on cloud services like Render
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main
import asyncio

logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self, max_restarts=10, restart_delay=30):
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.start_time = datetime.now()
        
    async def run_with_restart(self):
        """Run the bot with automatic restart on failure"""
        while self.restart_count < self.max_restarts:
            try:
                logger.info(f"Starting bot (Attempt {self.restart_count + 1}/{self.max_restarts})")
                await main()
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
                
            except Exception as e:
                self.restart_count += 1
                logger.error(f"Bot crashed: {e}")
                
                if self.restart_count < self.max_restarts:
                    logger.info(f"Restarting in {self.restart_delay} seconds...")
                    await asyncio.sleep(self.restart_delay)
                    
                    # Reset restart count if bot has been running for more than 1 hour
                    runtime = datetime.now() - self.start_time
                    if runtime.total_seconds() > 3600:  # 1 hour
                        self.restart_count = 0
                        self.start_time = datetime.now()
                        logger.info("Runtime exceeded 1 hour, resetting restart counter")
                else:
                    logger.error("Maximum restart attempts reached")
                    break
    
    def run(self):
        """Entry point for running the bot"""
        try:
            asyncio.run(self.run_with_restart())
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check for required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Start the bot runner
    runner = BotRunner()
    runner.run()