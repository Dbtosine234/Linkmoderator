#!/usr/bin/env python3
"""
Telegram Moderation Bot - Main Entry Point
Monitors messages and restricts users who post more than one link.
"""

import os
import logging
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from bot_handler import BotHandler
from logger_config import setup_logger

def main():
    """Main function to start the Telegram bot"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Get bot token from environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Initialize bot handler
    bot_handler = BotHandler()
    
    # Add handlers
    # Message handler for all text messages (including links)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        bot_handler.handle_message
    ))
    
    # Admin command handlers
    application.add_handler(CommandHandler("stats", bot_handler.show_stats))
    application.add_handler(CommandHandler("reset_user", bot_handler.reset_user))
    application.add_handler(CommandHandler("whitelist", bot_handler.whitelist_user))
    application.add_handler(CommandHandler("unwhitelist", bot_handler.unwhitelist_user))
    application.add_handler(CommandHandler("help", bot_handler.show_help))
    application.add_handler(CommandHandler("start", bot_handler.show_help))
    
    # Error handler
    application.add_error_handler(bot_handler.error_handler)
    
    logger.info("Starting Telegram Moderation Bot...")
    
    # Start the bot
    application.run_polling(
        allowed_updates=["message", "edited_message"]
    )

if __name__ == "__main__":
    main()
