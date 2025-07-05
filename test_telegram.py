#!/usr/bin/env python3

import sys
import os

# Test basic imports first
try:
    import telegram
    print("✓ telegram module imported successfully")
    print(f"  Version: {telegram.__version__}")
except ImportError as e:
    print(f"✗ Failed to import telegram: {e}")
    sys.exit(1)

# Test specific imports
try:
    from telegram import Update, Bot
    print("✓ Basic telegram classes imported")
except ImportError as e:
    print(f"✗ Failed to import telegram classes: {e}")
    sys.exit(1)

try:
    from telegram.ext import Application, MessageHandler, CommandHandler, filters
    print("✓ telegram.ext imported successfully")
except ImportError as e:
    print(f"✗ Failed to import telegram.ext: {e}")
    sys.exit(1)

# Test bot token
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not bot_token:
    print("✗ TELEGRAM_BOT_TOKEN environment variable not set")
    sys.exit(1)

print("✓ TELEGRAM_BOT_TOKEN found")

# Test basic bot creation
try:
    application = Application.builder().token(bot_token).build()
    print("✓ Bot application created successfully")
except Exception as e:
    print(f"✗ Failed to create bot application: {e}")
    sys.exit(1)

print("✓ All imports and basic setup working correctly!")