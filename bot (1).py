"""
Main Bot Class for Telegram Tag Bot
Handles bot initialization, command registration, and application lifecycle
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from database import BotDatabase
# Attendance system removed for simplicity
from handlers import BotHandlers
from config import DATABASE_PATH
import os

logger = logging.getLogger(__name__)

class TelegramTagBot:
    """Main bot class that orchestrates all components"""
    
    def __init__(self, token: str):
        self.token = token
        self.database = BotDatabase(DATABASE_PATH)
        
        # Initialize handlers
        self.handlers = BotHandlers(self.database)
        self.application = None
        
    def _register_handlers(self):
        """Register all command and message handlers"""
        app = self.application
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.handlers.start_handler))
        app.add_handler(CommandHandler("help", self.handlers.help_handler))
        app.add_handler(CommandHandler("tag", self.handlers.tag_handler))
        app.add_handler(CommandHandler("afk", self.handlers.afk_handler))
        app.add_handler(CommandHandler("back", self.handlers.back_handler))
        app.add_handler(CommandHandler("setemoji", self.handlers.setemoji_handler))
        app.add_handler(CommandHandler("addadmin", self.handlers.addadmin_handler))
        app.add_handler(CommandHandler("removeadmin", self.handlers.removeadmin_handler))
        app.add_handler(CommandHandler("broadcast", self.handlers.broadcast_handler))
        
        # Attendance commands removed for simplicity
        
        # Message handler for AFK detection and mentions
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handlers.message_handler
        ))
        
        logger.info("All handlers registered successfully")
    
    def run(self):
        """Start the bot"""
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Register handlers
            self._register_handlers()
            
            logger.info("Bot started successfully")
            
            # Start polling
            self.application.run_polling(allowed_updates=['message', 'edited_message'])
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def _set_bot_commands(self):
        """Set bot commands for Telegram UI"""
        from telegram import BotCommand
        
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("tag", "Tag members in group"),
            BotCommand("afk", "Set AFK status"),
            BotCommand("back", "Remove AFK status"),
            BotCommand("setemoji", "Set custom tag emoji"),
            BotCommand("broadcast", "Broadcast message"),
            BotCommand("addadmin", "Add admin (Owner only)"),
            BotCommand("removeadmin", "Remove admin (Owner only)")
        ]
        
        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
