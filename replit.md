# Telegram Moderation Bot

## Overview

This is a Python-based Telegram moderation bot designed to automatically monitor group chats and restrict users who post excessive links. The bot detects links in messages and takes configurable moderation actions (muting or kicking) when users exceed the allowed link threshold.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Bot Handler**: Main orchestrator handling Telegram interactions and moderation logic
- **Link Detection**: Pattern-based URL extraction from text messages
- **User Tracking**: In-memory storage of user behavior and restrictions
- **Configuration**: Environment-based settings management
- **Logging**: Colored console logging with customizable levels

The system uses the `python-telegram-bot` library for Telegram API integration and operates as a webhook-based or polling bot.

## Key Components

### BotHandler (`bot_handler.py`)
- **Purpose**: Central controller for all bot interactions
- **Responsibilities**: Message processing, user restriction enforcement, admin commands
- **Integration**: Coordinates between link detection, user tracking, and Telegram API

### LinkDetector (`link_detector.py`)
- **Purpose**: Identifies URLs in text messages using regex patterns
- **Approach**: Multi-pattern matching for various URL formats (HTTP/HTTPS, common domains, Telegram links, short URLs)
- **Output**: Returns list of detected links from message text

### UserTracker (`user_tracker.py`)
- **Purpose**: Maintains user state and link counting
- **Storage**: In-memory dictionary structure with user data (count, username, timestamps)
- **Features**: Whitelist management, username-to-ID mapping, persistent tracking across sessions

### Config (`config.py`)
- **Purpose**: Centralized configuration management
- **Source**: Environment variables with sensible defaults
- **Validation**: Runtime validation of configuration values
- **Settings**: Link thresholds, restriction types, mute duration, notification preferences

### Logger Config (`logger_config.py`)
- **Purpose**: Custom logging setup with colored output
- **Features**: Color-coded log levels, custom formatting, console output
- **Integration**: Used across all modules for consistent logging

## Data Flow

1. **Message Reception**: Bot receives messages from Telegram groups
2. **Link Detection**: Messages are scanned for URLs using regex patterns
3. **User Tracking**: Link counts are incremented for users posting links
4. **Threshold Check**: System evaluates if user exceeded allowed link count
5. **Moderation Action**: Bot applies restrictions (mute/kick) and optionally deletes messages
6. **Notification**: Configurable notifications sent to group about restrictions

## External Dependencies

### Core Dependencies
- `python-telegram-bot`: Telegram Bot API wrapper
- `re`: Built-in regex module for link detection
- `logging`: Built-in logging framework
- `datetime`: Built-in date/time handling
- `os`: Environment variable access

### Telegram API Integration
- **Bot Token**: Required environment variable for authentication
- **Webhook/Polling**: Supports both deployment modes
- **Chat Permissions**: Uses Telegram's permission system for user restrictions

## Deployment Strategy

### Environment Configuration
- `TELEGRAM_BOT_TOKEN`: Required bot authentication token
- `MAX_LINKS_ALLOWED`: Link threshold before restriction (default: 1)
- `RESTRICTION_TYPE`: Action type - "mute" or "kick" (default: mute)
- `MUTE_DURATION`: Mute length in seconds (default: 0 for permanent)
- `DELETE_LINK_MESSAGES`: Whether to delete link messages (default: true)
- `SEND_RESTRICTION_NOTIFICATION`: Notification setting (default: true)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

### Data Persistence
- **Current State**: All data stored in memory (resets on restart)
- **Consideration**: In-memory storage means user data is lost on bot restart
- **Future Enhancement**: Could be extended with database persistence

### Scalability Considerations
- Single-instance design suitable for moderate group sizes
- Memory usage grows with unique user count
- No database requirements for simple deployments

## Changelog

```
Changelog:
- July 05, 2025. Initial setup
- July 05, 2025. Fixed telegram library compatibility issues and bot is now running successfully
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```