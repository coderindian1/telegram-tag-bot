"""
Utility functions for the Telegram Tag Bot
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from telegram import Chat, ChatMember, User
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

async def get_chat_members(chat: Chat, limit: int = 200) -> List[ChatMember]:
    """
    Get list of chat members with rate limiting
    """
    members = []
    try:
        # Get administrators first
        admins = await chat.get_administrators()
        members.extend(admins)
        
        # For small groups, try to get all members
        if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            try:
                # This might not work for large groups due to API limitations
                member_count = await chat.get_member_count()
                if member_count <= limit:
                    # We can only get members we can see (recent activity)
                    # Telegram API doesn't allow getting all members for privacy reasons
                    pass
            except TelegramError as e:
                logger.warning(f"Could not get member count: {e}")
        
        return members
    except TelegramError as e:
        logger.error(f"Error getting chat members: {e}")
        return []

def format_user_mention(user: User, emoji: str = "🔔") -> str:
    """
    Format user mention with emoji (simple text format)
    """
    if user.username:
        return f"{emoji} @{user.username}"
    else:
        # Use first name with emoji for users without username
        return f"{emoji} {user.first_name}"

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def is_valid_emoji(text: str) -> bool:
    """
    Basic emoji validation
    """
    if not text:
        return False
    
    # Check if it's a single character and appears to be an emoji
    if len(text) == 1:
        # Basic emoji ranges (this is simplified)
        code_point = ord(text)
        return (0x1F600 <= code_point <= 0x1F64F or  # Emoticons
                0x1F300 <= code_point <= 0x1F5FF or  # Miscellaneous Symbols
                0x1F680 <= code_point <= 0x1F6FF or  # Transport and Map
                0x1F1E6 <= code_point <= 0x1F1FF or  # Regional indicators
                0x2600 <= code_point <= 0x26FF or    # Miscellaneous symbols
                0x2700 <= code_point <= 0x27BF)      # Dingbats
    
    # Allow multi-character emojis (simplified check)
    return len(text) <= 4 and any(ord(c) > 0x1F000 for c in text)

def parse_username(text: str) -> Optional[str]:
    """
    Parse username from text (with or without @)
    """
    if not text:
        return None
    
    text = text.strip()
    if text.startswith('@'):
        return text[1:]
    return text

async def safe_send_message(bot, chat_id: int, text: str, **kwargs) -> bool:
    """
    Safely send message with error handling
    """
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return True
    except TelegramError as e:
        logger.error(f"Error sending message to {chat_id}: {e}")
        return False

async def rate_limited_operation(operations: List, delay: float = 0.1):
    """
    Execute operations with rate limiting
    """
    for operation in operations:
        try:
            await operation
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f"Error in rate limited operation: {e}")

def format_duration(start_time: str) -> str:
    """
    Format duration from AFK start time to current time
    """
    try:
        start_dt = datetime.fromisoformat(start_time)
        now = datetime.now()
        duration = now - start_dt
        
        # Calculate hours and minutes
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
    except Exception as e:
        logger.error(f"Error formatting duration: {e}")
        return "some time"

async def check_bot_admin_status(bot, chat_id: int) -> bool:
    """
    Check if bot is admin in the chat
    """
    try:
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        return bot_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except TelegramError as e:
        logger.error(f"Error checking bot admin status: {e}")
        return False

async def get_all_chat_members(chat: Chat, bot) -> List[User]:
    """
    Get all visible chat members when bot is admin
    """
    try:
        # Check if bot is admin first
        if not await check_bot_admin_status(bot, chat.id):
            return []
        
        members = []
        seen_user_ids = set()
        
        # Get administrators first - these are always visible
        try:
            admins = await chat.get_administrators()
            for admin in admins:
                if not admin.user.is_bot and admin.user.id not in seen_user_ids:
                    members.append(admin.user)
                    seen_user_ids.add(admin.user.id)
        except TelegramError as e:
            logger.warning(f"Could not get administrators: {e}")
        
        # Log member count for reference
        try:
            member_count = await chat.get_member_count()
            logger.info(f"Total member count: {member_count}, found {len(members)} admins")
        except TelegramError as e:
            logger.warning(f"Could not get member count: {e}")
            
        return members
        
    except TelegramError as e:
        logger.error(f"Error getting chat members: {e}")
        return []

async def get_chat_members_extended(chat: Chat, bot, database) -> List[User]:
    """
    Enhanced member fetching using bot's database and aggressive member discovery
    """
    try:
        members = []
        seen_user_ids = set()
        
        # First get admin members
        admin_members = await get_all_chat_members(chat, bot)
        for member in admin_members:
            if member.id not in seen_user_ids:
                members.append(member)
                seen_user_ids.add(member.id)
        
        # Get stored group members from database
        stored_member_ids = database.get_group_members(chat.id)
        
        # Add stored group members with verification
        for user_id in stored_member_ids:
            if user_id not in seen_user_ids and str(user_id) in database.data.get('users', {}):
                user_data = database.data['users'][str(user_id)]
                # Create User object from stored data (trust our database)
                from telegram import User
                user = User(
                    id=user_id,
                    is_bot=False,
                    first_name=user_data.get('first_name', 'User'),
                    username=user_data.get('username')
                )
                members.append(user)
                seen_user_ids.add(user_id)
        
        # Aggressively check ALL known users to discover new group members
        logger.info(f"Checking {len(database.data.get('users', {}))} known users for group membership")
        check_count = 0
        for user_id_str, user_data in database.data.get('users', {}).items():
            user_id = int(user_id_str)
            if user_id not in seen_user_ids:
                try:
                    # Check if user is in the group
                    member_info = await bot.get_chat_member(chat.id, user_id)
                    check_count += 1
                    
                    if member_info.status not in [ChatMember.LEFT, ChatMember.BANNED]:
                        # Add to group members list for future reference
                        database.add_group_member(chat.id, user_id)
                        # Create User object
                        from telegram import User
                        user = User(
                            id=user_id,
                            is_bot=False,
                            first_name=user_data.get('first_name', 'User'),
                            username=user_data.get('username')
                        )
                        members.append(user)
                        seen_user_ids.add(user_id)
                        logger.info(f"Discovered new group member: {user_data.get('first_name', 'User')}")
                    
                    # Rate limiting - small delay between checks
                    if check_count % 5 == 0:
                        await asyncio.sleep(0.1)
                        
                except TelegramError as e:
                    # User not in group or inaccessible
                    if "Bad Request: user not found" not in str(e):
                        logger.debug(f"Could not check user {user_id}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error checking user {user_id}: {e}")
                    continue
        
        logger.info(f"Checked {check_count} users, found {len(members)} total members for tagging in group {chat.id}")
        return members
        
    except Exception as e:
        logger.error(f"Error getting extended chat members: {e}")
        # Fall back to basic method
        return await get_all_chat_members(chat, bot)
