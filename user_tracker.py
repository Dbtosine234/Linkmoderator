"""
User Tracker - Tracks user link posting behavior
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any

class UserTracker:
    """Tracks user link posting behavior and maintains restrictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # User data structure: {user_id: {count, username, last_seen}}
        self.user_data: Dict[int, Dict[str, Any]] = {}
        
        # Whitelisted users (exempt from restrictions)
        self.whitelisted_users: set = set()
        
        # Username to user_id mapping for easier lookups
        self.username_to_id: Dict[str, int] = {}
    
    def add_link(self, user_id: int, username: str) -> int:
        """
        Add a link count for a user
        
        Args:
            user_id (int): Telegram user ID
            username (str): Username or display name
            
        Returns:
            int: Total link count for the user
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'count': 0,
                'username': username,
                'first_seen': current_time,
                'last_seen': current_time
            }
            self.logger.info(f"New user tracked: {username} ({user_id})")
        
        # Update user data
        self.user_data[user_id]['count'] += 1
        self.user_data[user_id]['username'] = username  # Update in case it changed
        self.user_data[user_id]['last_seen'] = current_time
        
        # Update username mapping
        if username:
            clean_username = username.replace('@', '').lower()
            self.username_to_id[clean_username] = user_id
        
        count = self.user_data[user_id]['count']
        self.logger.debug(f"User {username} ({user_id}) link count: {count}")
        
        return count
    
    def get_user_count(self, user_id: int) -> int:
        """
        Get link count for a user
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            int: Link count for the user
        """
        return self.user_data.get(user_id, {}).get('count', 0)
    
    def reset_user(self, user_id: int) -> bool:
        """
        Reset link count for a user
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user was found and reset, False otherwise
        """
        if user_id in self.user_data:
            old_count = self.user_data[user_id]['count']
            self.user_data[user_id]['count'] = 0
            self.user_data[user_id]['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            username = self.user_data[user_id]['username']
            self.logger.info(f"Reset user {username} ({user_id}) from {old_count} links to 0")
            return True
        
        return False
    
    def whitelist_user(self, user_id: int):
        """
        Add user to whitelist
        
        Args:
            user_id (int): Telegram user ID
        """
        self.whitelisted_users.add(user_id)
        username = self.user_data.get(user_id, {}).get('username', 'Unknown')
        self.logger.info(f"User {username} ({user_id}) added to whitelist")
    
    def unwhitelist_user(self, user_id: int) -> bool:
        """
        Remove user from whitelist
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user was in whitelist, False otherwise
        """
        if user_id in self.whitelisted_users:
            self.whitelisted_users.remove(user_id)
            username = self.user_data.get(user_id, {}).get('username', 'Unknown')
            self.logger.info(f"User {username} ({user_id}) removed from whitelist")
            return True
        return False
    
    def is_whitelisted(self, user_id: int) -> bool:
        """
        Check if user is whitelisted
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            bool: True if user is whitelisted
        """
        return user_id in self.whitelisted_users
    
    def get_user_id_by_username(self, username: str) -> Optional[int]:
        """
        Get user ID by username
        
        Args:
            username (str): Username to look up
            
        Returns:
            Optional[int]: User ID if found, None otherwise
        """
        clean_username = username.replace('@', '').lower()
        return self.username_to_id.get(clean_username)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tracked users
        
        Returns:
            Dict: Statistics including user counts, total links, etc.
        """
        total_users = len(self.user_data)
        total_links = sum(data['count'] for data in self.user_data.values())
        
        return {
            'total_users': total_users,
            'total_links': total_links,
            'users': self.user_data.copy(),
            'whitelisted': list(self.whitelisted_users)
        }
    
    def cleanup_old_data(self, days_threshold: int = 30):
        """
        Clean up old user data (optional maintenance function)
        
        Args:
            days_threshold (int): Remove users not seen for this many days
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        users_to_remove = []
        
        for user_id, data in self.user_data.items():
            try:
                last_seen = datetime.strptime(data['last_seen'], "%Y-%m-%d %H:%M:%S")
                if last_seen < cutoff_date:
                    users_to_remove.append(user_id)
            except ValueError:
                # Handle any date parsing errors
                continue
        
        for user_id in users_to_remove:
            username = self.user_data[user_id]['username']
            del self.user_data[user_id]
            
            # Also remove from username mapping
            for uname, uid in list(self.username_to_id.items()):
                if uid == user_id:
                    del self.username_to_id[uname]
            
            self.logger.info(f"Cleaned up old data for user {username} ({user_id})")
        
        if users_to_remove:
            self.logger.info(f"Cleaned up {len(users_to_remove)} old user records")
