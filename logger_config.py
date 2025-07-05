"""
Logging configuration for the Telegram moderation bot
"""

import logging
import sys
from datetime import datetime

def setup_logger():
    """Set up logging configuration"""
    
    # Create custom formatter
    class CustomFormatter(logging.Formatter):
        """Custom formatter with colors for different log levels"""
        
        # Color codes
        COLORS = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
            'RESET': '\033[0m'      # Reset
        }
        
        def format(self, record):
            # Add color to levelname
            if hasattr(record, 'levelname'):
                color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
            
            return super().format(record)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = CustomFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to appropriate levels
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Create application-specific logger
    app_logger = logging.getLogger('telegram_moderation_bot')
    app_logger.setLevel(logging.INFO)
    
    return app_logger

def log_bot_action(action: str, user_id: int, username: str, chat_id: int, details: str = ""):
    """
    Log bot moderation actions with consistent format
    
    Args:
        action (str): The action taken (e.g., "restricted", "whitelisted")
        user_id (int): Telegram user ID
        username (str): Username or display name
        chat_id (int): Chat ID where action occurred
        details (str): Additional details about the action
    """
    logger = logging.getLogger('telegram_moderation_bot.actions')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{action.upper()}] User: {username} ({user_id}) | Chat: {chat_id}"
    
    if details:
        log_message += f" | Details: {details}"
    
    logger.info(log_message)

def log_error_with_context(error: Exception, context: str, user_id: int = None, chat_id: int = None):
    """
    Log errors with additional context information
    
    Args:
        error (Exception): The exception that occurred
        context (str): Context where the error occurred
        user_id (int, optional): User ID if relevant
        chat_id (int, optional): Chat ID if relevant
    """
    logger = logging.getLogger('telegram_moderation_bot.errors')
    
    error_message = f"Error in {context}: {str(error)}"
    
    if user_id:
        error_message += f" | User ID: {user_id}"
    
    if chat_id:
        error_message += f" | Chat ID: {chat_id}"
    
    logger.error(error_message, exc_info=True)
