"""
Bot Handler - Main bot logic and command handlers
"""

import logging
from datetime import datetime
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from link_detector import LinkDetector
from user_tracker import UserTracker
from config import Config

class BotHandler:
    """Handles all bot interactions and moderation logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.link_detector = LinkDetector()
        self.user_tracker = UserTracker()
        self.config = Config()
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages and check for links"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            user = message.from_user
            chat = message.chat
            
            # Only process group and supergroup chats
            if chat.type not in ['group', 'supergroup']:
                return
            
            # Check if user is whitelisted
            if self.user_tracker.is_whitelisted(user.id):
                return
            
            # Check if message contains links
            links = self.link_detector.extract_links(message.text)
            if not links:
                return
            
            # Track link for user
            link_count = self.user_tracker.add_link(user.id, user.username or user.first_name)
            
            self.logger.info(
                f"User {user.username or user.first_name} ({user.id}) posted link(s) in chat {chat.id}. "
                f"Total links: {link_count}. Links: {links}"
            )
            
            # Check if user exceeded limit
            if link_count > self.config.MAX_LINKS_ALLOWED:
                await self._restrict_user(update, context, user, chat, link_count)
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
    
    async def _restrict_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                           user, chat, link_count):
        """Restrict user who exceeded link limit"""
        try:
            # Check if bot has admin permissions
            bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR]:
                self.logger.warning(f"Bot is not admin in chat {chat.id}, cannot restrict users")
                return
            
            # Check if user is admin
            user_member = await context.bot.get_chat_member(chat.id, user.id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                self.logger.info(f"User {user.username or user.first_name} is admin, skipping restriction")
                return
            
            # Restrict user based on configuration
            if self.config.RESTRICTION_TYPE == "mute":
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=user.id,
                    permissions=self.config.get_mute_permissions()
                )
                action = "muted"
            else:  # kick
                await context.bot.ban_chat_member(
                    chat_id=chat.id,
                    user_id=user.id
                )
                await context.bot.unban_chat_member(
                    chat_id=chat.id,
                    user_id=user.id
                )
                action = "kicked"
            
            # Delete the message that triggered the restriction
            try:
                await context.bot.delete_message(
                    chat_id=chat.id,
                    message_id=update.message.message_id
                )
            except Exception as e:
                self.logger.warning(f"Could not delete message: {str(e)}")
            
            # Send notification
            notification_text = (
                f"⚠️ User @{user.username or user.first_name} has been {action} "
                f"for posting {link_count} links (limit: {self.config.MAX_LINKS_ALLOWED})"
            )
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=notification_text
            )
            
            self.logger.info(
                f"User {user.username or user.first_name} ({user.id}) {action} "
                f"in chat {chat.id} for {link_count} links"
            )
            
        except Exception as e:
            self.logger.error(f"Error restricting user {user.id}: {str(e)}")
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics about link posts"""
        try:
            # Check if user is admin
            if not await self._is_user_admin(update, context):
                await update.message.reply_text("❌ This command is only available to administrators.")
                return
            
            stats = self.user_tracker.get_stats()
            
            if not stats['users']:
                await update.message.reply_text("📊 No link statistics available.")
                return
            
            text = "📊 **Link Statistics:**\n\n"
            
            # Top users by link count
            sorted_users = sorted(stats['users'].items(), key=lambda x: x[1]['count'], reverse=True)
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                username = data['username']
                count = data['count']
                last_seen = data['last_seen']
                text += f"{i}. {username}: {count} links (last: {last_seen})\n"
            
            text += f"\n**Total users tracked:** {stats['total_users']}"
            text += f"\n**Total links posted:** {stats['total_links']}"
            text += f"\n**Whitelisted users:** {len(stats['whitelisted'])}"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error showing stats: {str(e)}")
            await update.message.reply_text("❌ Error retrieving statistics.")
    
    async def reset_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset link count for a user"""
        try:
            # Check if user is admin
            if not await self._is_user_admin(update, context):
                await update.message.reply_text("❌ This command is only available to administrators.")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /reset_user <user_id or @username>")
                return
            
            target = context.args[0]
            
            # Try to parse as user ID
            try:
                user_id = int(target)
            except ValueError:
                # Try to get user ID from username
                if target.startswith('@'):
                    target = target[1:]
                
                user_id = self.user_tracker.get_user_id_by_username(target)
                if not user_id:
                    await update.message.reply_text(f"❌ User {target} not found.")
                    return
            
            if self.user_tracker.reset_user(user_id):
                await update.message.reply_text(f"✅ Link count reset for user ID {user_id}")
            else:
                await update.message.reply_text(f"❌ User ID {user_id} not found in tracking.")
                
        except Exception as e:
            self.logger.error(f"Error resetting user: {str(e)}")
            await update.message.reply_text("❌ Error resetting user.")
    
    async def whitelist_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add user to whitelist"""
        try:
            # Check if user is admin
            if not await self._is_user_admin(update, context):
                await update.message.reply_text("❌ This command is only available to administrators.")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /whitelist <user_id or @username>")
                return
            
            target = context.args[0]
            
            # Try to parse as user ID
            try:
                user_id = int(target)
            except ValueError:
                # Try to get user ID from username
                if target.startswith('@'):
                    target = target[1:]
                
                user_id = self.user_tracker.get_user_id_by_username(target)
                if not user_id:
                    await update.message.reply_text(f"❌ User {target} not found.")
                    return
            
            self.user_tracker.whitelist_user(user_id)
            await update.message.reply_text(f"✅ User ID {user_id} added to whitelist")
            
        except Exception as e:
            self.logger.error(f"Error whitelisting user: {str(e)}")
            await update.message.reply_text("❌ Error whitelisting user.")
    
    async def unwhitelist_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove user from whitelist"""
        try:
            # Check if user is admin
            if not await self._is_user_admin(update, context):
                await update.message.reply_text("❌ This command is only available to administrators.")
                return
            
            if not context.args:
                await update.message.reply_text("Usage: /unwhitelist <user_id or @username>")
                return
            
            target = context.args[0]
            
            # Try to parse as user ID
            try:
                user_id = int(target)
            except ValueError:
                # Try to get user ID from username
                if target.startswith('@'):
                    target = target[1:]
                
                user_id = self.user_tracker.get_user_id_by_username(target)
                if not user_id:
                    await update.message.reply_text(f"❌ User {target} not found.")
                    return
            
            if self.user_tracker.unwhitelist_user(user_id):
                await update.message.reply_text(f"✅ User ID {user_id} removed from whitelist")
            else:
                await update.message.reply_text(f"❌ User ID {user_id} was not in whitelist")
                
        except Exception as e:
            self.logger.error(f"Error unwhitelisting user: {str(e)}")
            await update.message.reply_text("❌ Error unwhitelisting user.")
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
🤖 **Telegram Moderation Bot**

This bot automatically restricts users who post more than one link message.

**Admin Commands:**
• `/stats` - Show link posting statistics
• `/reset_user <user_id|@username>` - Reset link count for a user
• `/whitelist <user_id|@username>` - Add user to whitelist (bypass restrictions)
• `/unwhitelist <user_id|@username>` - Remove user from whitelist
• `/help` - Show this help message

**Features:**
• Automatically detects URLs in messages
• Tracks link count per user
• Restricts users after posting more than 1 link
• Admin whitelist functionality
• Detailed logging and statistics

**Note:** Bot must be administrator to restrict users.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _is_user_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if user is admin in the chat"""
        try:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            
        except Exception as e:
            self.logger.error(f"Error checking admin status: {str(e)}")
            return False
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Update {update} caused error {context.error}")
