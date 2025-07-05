"""
Configuration settings for the Telegram moderation bot
"""

import os
from telegram import ChatPermissions

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Maximum links allowed before restriction
        self.MAX_LINKS_ALLOWED = int(os.getenv("MAX_LINKS_ALLOWED", "1"))
        
        # Restriction type: "mute" or "kick"
        self.RESTRICTION_TYPE = os.getenv("RESTRICTION_TYPE", "mute").lower()
        
        # Mute duration in seconds (0 for permanent until manually unmuted)
        self.MUTE_DURATION = int(os.getenv("MUTE_DURATION", "0"))
        
        # Whether to delete messages containing links from restricted users
        self.DELETE_LINK_MESSAGES = os.getenv("DELETE_LINK_MESSAGES", "true").lower() == "true"
        
        # Whether to send notification when user is restricted
        self.SEND_RESTRICTION_NOTIFICATION = os.getenv("SEND_RESTRICTION_NOTIFICATION", "true").lower() == "true"
        
        # Log level
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        if self.MAX_LINKS_ALLOWED < 1:
            raise ValueError("MAX_LINKS_ALLOWED must be at least 1")
        
        if self.RESTRICTION_TYPE not in ["mute", "kick"]:
            raise ValueError("RESTRICTION_TYPE must be either 'mute' or 'kick'")
        
        if self.MUTE_DURATION < 0:
            raise ValueError("MUTE_DURATION cannot be negative")
    
    def get_mute_permissions(self) -> ChatPermissions:
        """
        Get ChatPermissions object for muting users
        
        Returns:
            ChatPermissions: Permissions that remove ability to send messages
        """
        return ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
    
    def get_config_info(self) -> str:
        """
        Get human-readable configuration information
        
        Returns:
            str: Formatted configuration details
        """
        return f"""
**Current Configuration:**
• Max links allowed: {self.MAX_LINKS_ALLOWED}
• Restriction type: {self.RESTRICTION_TYPE}
• Mute duration: {"Permanent" if self.MUTE_DURATION == 0 else f"{self.MUTE_DURATION} seconds"}
• Delete link messages: {"Yes" if self.DELETE_LINK_MESSAGES else "No"}
• Send notifications: {"Yes" if self.SEND_RESTRICTION_NOTIFICATION else "No"}
• Log level: {self.LOG_LEVEL}
        """.strip()
