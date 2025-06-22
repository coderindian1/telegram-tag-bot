#!/usr/bin/env python3
"""
Flask web service wrapper for Telegram bot deployment on Render
"""
import os
import logging
import threading
from flask import Flask
from bot import TelegramTagBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global bot instance
bot_instance = None

@app.route('/')
def home():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Telegram Tag Bot",
        "bot_active": bot_instance is not None
    }

@app.route('/health')
def health():
    """Health check for Render"""
    return "OK", 200

def start_bot():
    """Start the Telegram bot in a separate thread"""
    global bot_instance
    try:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not found")
            return
            
        logger.info("Starting Telegram bot...")
        bot_instance = TelegramTagBot(token)
        bot_instance.run()
        
    except Exception as e:
        logger.error(f"Bot startup error: {e}")

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask web service
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)