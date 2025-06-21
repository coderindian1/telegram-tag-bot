"""
Configuration settings for the Telegram Tag Bot
"""

import os

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Database Configuration
DATABASE_PATH = 'bot_data.json'

# Default Settings
DEFAULT_TAG_EMOJI = '🔔'
TAG_BATCH_SIZE = 10
MAX_BROADCAST_DELAY = 0.5  # seconds between broadcasts to avoid rate limiting

# Command Configuration
COMMANDS = {
    'start': 'Start the bot',
    'tag': 'Tag members in group (10 at a time)',
    'afk': 'Set AFK status with optional reason',
    'back': 'Remove AFK status',
    'setemoji': 'Set custom emoji for tags (Owner/Admin only)',
    'broadcast': 'Send message to all users/groups (Owner/Admin only)',
    'addadmin': 'Add admin (Owner only)',
    'removeadmin': 'Remove admin (Owner only)',
    'help': 'Show available commands'
}

# Rate Limiting
RATE_LIMIT_DELAY = 0.1  # seconds between API calls
