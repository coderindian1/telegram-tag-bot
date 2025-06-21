"""
Database management for the Telegram Tag Bot
Handles persistent storage of user data, AFK statuses, and bot settings
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BotDatabase:
    """Manages bot data persistence using JSON files"""
    
    def __init__(self, db_path: str = 'bot_data.json'):
        self.db_path = db_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {e}")
        
        # Return default structure if file doesn't exist or error occurred
        return {
            'owner_id': None,
            'admins': [],
            'users': {},
            'groups': {},
            'afk_users': {},
            'settings': {
                'default_emoji': '🔔'
            }
        }
    
    def _save_data(self) -> bool:
        """Save data to JSON file"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            return False
    
    def set_owner(self, user_id: int) -> bool:
        """Set the bot owner (first user to interact)"""
        if self.data['owner_id'] is None:
            self.data['owner_id'] = user_id
            return self._save_data()
        return False
    
    def get_owner(self) -> Optional[int]:
        """Get the bot owner ID"""
        return self.data['owner_id']
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the owner"""
        return self.data['owner_id'] == user_id
    
    def add_admin(self, user_id: int) -> bool:
        """Add a user as admin"""
        if user_id not in self.data['admins']:
            self.data['admins'].append(user_id)
            return self._save_data()
        return False
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove a user from admins"""
        if user_id in self.data['admins']:
            self.data['admins'].remove(user_id)
            return self._save_data()
        return False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in self.data['admins']
    
    def is_owner_or_admin(self, user_id: int) -> bool:
        """Check if user is owner or admin"""
        return self.is_owner(user_id) or self.is_admin(user_id)
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add or update user information"""
        self.data['users'][str(user_id)] = {
            'username': username,
            'first_name': first_name,
            'last_seen': datetime.now().isoformat()
        }
        self._save_data()
    
    def add_group(self, group_id: int, group_title: str = None):
        """Add or update group information"""
        self.data['groups'][str(group_id)] = {
            'title': group_title,
            'last_active': datetime.now().isoformat(),
            'members': []  # Store member IDs for enhanced tagging
        }
        self._save_data()
    
    def add_group_member(self, group_id: int, user_id: int):
        """Add a member to group's member list"""
        group_key = str(group_id)
        if group_key not in self.data['groups']:
            self.add_group(group_id)
        
        if 'members' not in self.data['groups'][group_key]:
            self.data['groups'][group_key]['members'] = []
        
        if user_id not in self.data['groups'][group_key]['members']:
            self.data['groups'][group_key]['members'].append(user_id)
            self._save_data()
    
    def get_group_members(self, group_id: int) -> List[int]:
        """Get stored member IDs for a group"""
        group_key = str(group_id)
        if group_key in self.data['groups'] and 'members' in self.data['groups'][group_key]:
            return self.data['groups'][group_key]['members']
        return []
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs"""
        return [int(user_id) for user_id in self.data['users'].keys()]
    
    def get_all_groups(self) -> List[int]:
        """Get all group IDs"""
        return [int(group_id) for group_id in self.data['groups'].keys()]
    
    def set_afk(self, user_id: int, reason: str = None):
        """Set user as AFK"""
        self.data['afk_users'][str(user_id)] = {
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        self._save_data()
    
    def remove_afk(self, user_id: int) -> bool:
        """Remove user from AFK"""
        if str(user_id) in self.data['afk_users']:
            del self.data['afk_users'][str(user_id)]
            self._save_data()
            return True
        return False
    
    def get_afk_status(self, user_id: int) -> Optional[Dict[str, str]]:
        """Get user's AFK status"""
        return self.data['afk_users'].get(str(user_id))
    
    def is_afk(self, user_id: int) -> bool:
        """Check if user is AFK"""
        return str(user_id) in self.data['afk_users']
    
    def set_default_emoji(self, emoji: str) -> bool:
        """Set default tagging emoji"""
        self.data['settings']['default_emoji'] = emoji
        return self._save_data()
    
    def get_default_emoji(self) -> str:
        """Get default tagging emoji"""
        return self.data['settings'].get('default_emoji', '🔔')
    
    def get_admins(self) -> List[int]:
        """Get list of admin IDs"""
        return self.data['admins']
