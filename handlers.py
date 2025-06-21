"""
Command and message handlers for the Telegram Tag Bot
"""

import asyncio
import logging
from typing import List
from telegram import Update, Chat, ChatMember, User
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database import BotDatabase
# Attendance system removed
from utils import get_chat_members, format_user_mention, chunk_list, is_valid_emoji, parse_username, safe_send_message, format_duration, check_bot_admin_status, get_all_chat_members, get_chat_members_extended

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handles all bot commands and messages"""
    
    def __init__(self, database: BotDatabase):
        self.db = database
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Add user to database
        self.db.add_user(user.id, user.username, user.first_name)
        
        # Set as owner if first user
        if self.db.set_owner(user.id):
            await update.message.reply_text(
                f"🎉 Welcome {user.first_name}!\n\n"
                "You are now the **Owner** of this bot!\n\n"
                "Available commands:\n"
                "👑 **Owner Commands:**\n"
                "/addadmin @username - Add admin\n"
                "/removeadmin @username - Remove admin\n\n"
                "🔧 **General Commands:**\n"
                "/tag - Tag members in group\n"
                "/afk [reason] - Set AFK status\n"
                "/back - Remove AFK status\n"
                "/setemoji <emoji> - Set tag emoji\n"
                "/broadcast <message> - Send to all users\n"
                "/help - Show this help",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"👋 Hello {user.first_name}!\n\n"
                "I'm a group management bot with tagging features!\n\n"
                "🔧 **Available Commands:**\n"
                "/tag - Tag members in group\n"
                "/afk [reason] - Set AFK status\n"
                "/back - Remove AFK status\n"
                "/help - Show help\n\n"
                "Add me to your group to use tagging features!",
                parse_mode='Markdown'
            )
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user = update.effective_user
        
        help_text = "🤖 **Telegram Tag Bot Help**\n\n"
        help_text += "🔧 **General Commands:**\n"
        help_text += "/tag - Tag 10 members at a time\n"
        help_text += "/afk [reason] - Set yourself as AFK\n"
        help_text += "/back - Remove AFK status\n"
        help_text += "/help - Show this help\n\n"
        
        # Attendance commands removed for simplicity
        
        if self.db.is_owner_or_admin(user.id):
            help_text += "👨‍💻 **Admin Commands:**\n"
            help_text += "/setemoji <emoji> - Set custom tag emoji\n"
            help_text += "/broadcast <message> - Send to all users/groups\n\n"
        
        if self.db.is_owner(user.id):
            help_text += "👑 **Owner Commands:**\n"
            help_text += "/addadmin @username - Add admin\n"
            help_text += "/removeadmin @username - Remove admin\n\n"
        
        help_text += "💡 **Tips:**\n"
        help_text += "• Use /tag as reply to tag on specific message\n"
        help_text += "• Bot works in groups and private chats\n"
        help_text += "• AFK auto-replies when someone mentions you\n"
        # Attendance tracking removed
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def tag_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tag command"""
        chat = update.effective_chat
        user = update.effective_user
        message = update.message
        
        # Only work in groups
        if chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
            await message.reply_text("❌ Tag command only works in groups!")
            return
        
        try:
            # Check if bot is admin for automatic tagging
            is_bot_admin = await check_bot_admin_status(context.bot, chat.id)
            
            if is_bot_admin:
                # Auto-tagging mode: get all members using enhanced method
                members = await get_chat_members_extended(chat, context.bot, self.db)
                # Filter out the command sender
                members = [member for member in members if member.id != user.id]
            else:
                # Regular tagging mode - limited to admins and recent members
                chat_members = await get_chat_members(chat)
                members = [member.user for member in chat_members 
                         if (member.user.id != user.id and 
                             not member.user.is_bot and 
                             member.status not in [ChatMember.LEFT, ChatMember.BANNED])]
            
            if not members:
                if not is_bot_admin:
                    await message.reply_text("❌ I need admin rights to tag all members in this group!")
                else:
                    await message.reply_text("❌ No members to tag!")
                return
            
            # Get custom message if provided
            tag_message = " ".join(context.args) if context.args else ""
            
            # Get default emoji
            emoji = self.db.get_default_emoji()
            
            # Split into chunks of 10
            member_chunks = chunk_list(members, 10)
            
            # Determine if this is a reply tag
            reply_to_message = message.reply_to_message
            
            # Send tag message first if provided
            if tag_message:
                if reply_to_message:
                    await reply_to_message.reply_text(f"📢 {tag_message}")
                else:
                    await message.reply_text(f"📢 {tag_message}")
            
            for i, chunk in enumerate(member_chunks):
                tag_text = " ".join([format_user_mention(member, emoji) for member in chunk])
                
                try:
                    if reply_to_message and i == 0 and not tag_message:
                        # First chunk replies to the original message (only if no custom message)
                        await reply_to_message.reply_text(tag_text)
                    else:
                        # Subsequent chunks or regular tags
                        await message.reply_text(tag_text)
                    
                    # Rate limiting
                    if i < len(member_chunks) - 1:
                        await asyncio.sleep(0.5)
                        
                except TelegramError as e:
                    logger.error(f"Error sending tag message: {e}")
                    await message.reply_text(f"❌ Error tagging members: {str(e)}")
                    break
            
            # Add group to database
            self.db.add_group(chat.id, chat.title)
            
        except Exception as e:
            logger.error(f"Error in tag handler: {e}")
            await message.reply_text("❌ An error occurred while tagging members!")
    
    async def afk_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /afk command"""
        user = update.effective_user
        message = update.message
        
        # Get AFK reason from command arguments
        reason = " ".join(context.args) if context.args else None
        
        # Set user as AFK
        self.db.set_afk(user.id, reason)
        
        if reason:
            await message.reply_text(f"😴 {user.first_name} is now AFK: {reason}")
        else:
            await message.reply_text(f"😴 {user.first_name} is now AFK")
    
    async def back_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /back command"""
        user = update.effective_user
        message = update.message
        
        # Get AFK status before removing
        afk_status = self.db.get_afk_status(user.id)
        
        if self.db.remove_afk(user.id) and afk_status:
            # Calculate AFK duration
            duration = format_duration(afk_status['timestamp'])
            await message.reply_text(f"✅ Welcome back {user.first_name}!\nYou were AFK for {duration}.")
        else:
            await message.reply_text("❌ You are not AFK!")
    
    async def setemoji_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setemoji command"""
        user = update.effective_user
        message = update.message
        
        if not self.db.is_owner_or_admin(user.id):
            await message.reply_text("❌ Only owners and admins can set emoji!")
            return
        
        if not context.args:
            await message.reply_text("❌ Please provide an emoji!\nUsage: /setemoji 🔥")
            return
        
        emoji = context.args[0]
        
        if not is_valid_emoji(emoji):
            await message.reply_text("❌ Please provide a valid emoji!")
            return
        
        if self.db.set_default_emoji(emoji):
            await message.reply_text(f"✅ Tag emoji set to: {emoji}")
        else:
            await message.reply_text("❌ Failed to set emoji!")
    
    async def addadmin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command"""
        user = update.effective_user
        message = update.message
        
        if not self.db.is_owner(user.id):
            await message.reply_text("❌ Only the owner can add admins!")
            return
        
        if not context.args:
            await message.reply_text("❌ Please provide a username!\nUsage: /addadmin @username")
            return
        
        username = parse_username(context.args[0])
        if not username:
            await message.reply_text("❌ Please provide a valid username!")
            return
        
        # Try to find user by username (this is limited by Telegram API)
        await message.reply_text(
            f"⚠️ Please ask @{username} to send /start to the bot first, "
            "then use /addadmin with their user ID or have them use the bot in this chat."
        )
    
    async def removeadmin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeadmin command"""
        user = update.effective_user
        message = update.message
        
        if not self.db.is_owner(user.id):
            await message.reply_text("❌ Only the owner can remove admins!")
            return
        
        if not context.args:
            await message.reply_text("❌ Please provide a username!\nUsage: /removeadmin @username")
            return
        
        username = parse_username(context.args[0])
        if not username:
            await message.reply_text("❌ Please provide a valid username!")
            return
        
        # Similar limitation as addadmin
        await message.reply_text(
            f"⚠️ Admin removal requires the user ID. "
            f"Currently, you can only remove admins by their user ID due to API limitations."
        )
    
    async def broadcast_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        user = update.effective_user
        message = update.message
        
        if not self.db.is_owner_or_admin(user.id):
            await message.reply_text("❌ Only owners and admins can broadcast!")
            return
        
        if not context.args:
            await message.reply_text("❌ Please provide a message to broadcast!\nUsage: /broadcast <message>")
            return
        
        broadcast_message = " ".join(context.args)
        
        # Get all users and groups
        users = self.db.get_all_users()
        groups = self.db.get_all_groups()
        
        success_count = 0
        total_count = len(users) + len(groups)
        
        await message.reply_text(f"📢 Broadcasting to {total_count} chats...")
        
        # Broadcast to users
        for user_id in users:
            if user_id != user.id:  # Don't send to the broadcaster
                if await safe_send_message(context.bot, user_id, f"📢 **Broadcast:**\n{broadcast_message}", parse_mode='Markdown'):
                    success_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
        
        # Broadcast to groups
        for group_id in groups:
            if await safe_send_message(context.bot, group_id, f"📢 **Broadcast:**\n{broadcast_message}", parse_mode='Markdown'):
                success_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        
        await message.reply_text(f"✅ Broadcast sent to {success_count}/{total_count} chats!")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages (for AFK detection)"""
        user = update.effective_user
        message = update.message
        chat = update.effective_chat
        
        # Add user to database
        self.db.add_user(user.id, user.username, user.first_name)
        
        # If this is a group chat, track the user as a group member and mark attendance
        if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            self.db.add_group_member(chat.id, user.id)
            
            # Attendance tracking removed for simplicity
        
        # If user is AFK and sends a message, remove AFK status and announce return
        if self.db.is_afk(user.id):
            afk_status = self.db.get_afk_status(user.id)
            self.db.remove_afk(user.id)
            
            if afk_status:
                duration = format_duration(afk_status['timestamp'])
                await message.reply_text(f"✅ Welcome back {user.first_name}!\nYou were AFK for {duration}.")
        
        # Check for mentions of AFK users (replies and mentions)
        if message.entities:
            for entity in message.entities:
                if entity.type == 'mention':
                    # Extract username from mention
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length][1:]  # Remove @
                    
                    # Find user by username (this is limited - we can only check our database)
                    for user_id_str, user_data in self.db.data['users'].items():
                        if user_data.get('username') == mentioned_username:
                            user_id = int(user_id_str)
                            afk_status = self.db.get_afk_status(user_id)
                            
                            if afk_status:
                                duration = format_duration(afk_status['timestamp'])
                                afk_reason = afk_status.get('reason', '')
                                if afk_reason:
                                    await message.reply_text(f"💤 @{mentioned_username} is AFK for {duration}\nReason: {afk_reason}")
                                else:
                                    await message.reply_text(f"💤 @{mentioned_username} is AFK for {duration}")
                            break
                
                elif entity.type == 'text_mention':
                    # Direct user mention
                    mentioned_user = entity.user
                    afk_status = self.db.get_afk_status(mentioned_user.id)
                    
                    if afk_status:
                        duration = format_duration(afk_status['timestamp'])
                        afk_reason = afk_status.get('reason', '')
                        name = mentioned_user.username or mentioned_user.first_name
                        if afk_reason:
                            await message.reply_text(f"💤 {name} is AFK for {duration}\nReason: {afk_reason}")
                        else:
                            await message.reply_text(f"💤 {name} is AFK for {duration}")
        
        # Check if this is a reply to an AFK user
        if message.reply_to_message and message.reply_to_message.from_user:
            replied_user = message.reply_to_message.from_user
            afk_status = self.db.get_afk_status(replied_user.id)
            
            if afk_status:
                duration = format_duration(afk_status['timestamp'])
                afk_reason = afk_status.get('reason', '')
                name = replied_user.username or replied_user.first_name
                if afk_reason:
                    await message.reply_text(f"💤 {name} is AFK for {duration}\nReason: {afk_reason}")
                else:
                    await message.reply_text(f"💤 {name} is AFK for {duration}")
        
        # Add group to database if it's a group chat
        if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            self.db.add_group(chat.id, chat.title)
    
    # Attendance commands removed for simplicity
