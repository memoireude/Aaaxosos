# Overview

A Discord moderation bot written in Python that provides essential server moderation capabilities. The bot features core moderation commands (ban, kick, ping, test) with comprehensive permission checking, action logging, and user notifications. Currently running successfully using simple_bot.py architecture.

## Recent Changes (August 2025)
- **Fixed command registration conflict**: Resolved 'help' command duplicate by renaming to 'commandes' in simple_bot.py
- **Corrected parameter typing**: Made Member parameters required to eliminate None type issues
- **Improved error handling**: Bot no longer responds to unknown commands to prevent spam
- **Added unban command**: New +unban command using user ID for unbanning users
- **Enhanced command help**: Updated help system with proper command syntax
- **Flexible moderation targeting**: Ban and kick commands now support both @mention and reply-to-message methods
- **Removed mute command**: Mute command removed to avoid conflicts with other bots
- **Enhanced prefix filtering**: Bot now completely ignores invalid + commands to prevent interference with other bots
- **Role restoration feature**: Unmute command restores users' original roles or assigns base role
- **Bot Status**: Successfully running and connected to Discord servers
- **Active Commands**: +ping, +test, +ban, +unban, +kick, +unmute, +commandes

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Discord.py Library**: Uses the discord.py library for Discord API interactions
- **Commands Extension**: Implements discord.ext.commands for structured command handling
- **Custom Bot Class**: Extends commands.Bot with ModerationBot class for specialized functionality

## Command System
- **Prefix-based Commands**: Uses "+" as the command prefix for all bot interactions
- **Permission Hierarchy**: Implements role-based permission checking to prevent privilege escalation
- **Error Handling**: Global error handler for common command errors (missing permissions, member not found)

## Modular Design
- **Utilities Package**: Separates cross-cutting concerns into dedicated modules
- **Permissions Module**: Centralized permission checking logic for all moderation actions
- **Logging Module**: Dedicated logging system with both console and file output

## Logging System
- **Dual Output**: Logs to both console and daily rotating log files
- **Separate Moderation Logs**: Dedicated logging for moderation actions separate from general bot logs
- **Structured Format**: Timestamped logs with clear formatting for debugging and audit trails

## Security Features
- **Role Hierarchy Enforcement**: Prevents users from moderating others with equal or higher roles
- **Self-Protection**: Prevents self-moderation and bot moderation attempts
- **Server Owner Protection**: Special handling for server ownership privileges

## Configuration
- **Environment Variables**: Uses DISCORD_TOKEN environment variable for secure token storage
- **Intent Configuration**: Explicitly enables required Discord intents (message_content, members, guilds)

# External Dependencies

## Discord API
- **discord.py**: Primary library for Discord bot functionality and API communication
- **Discord Intents**: Requires message content, members, and guilds intents for full functionality

## Python Standard Library
- **logging**: Built-in logging system for application logs and moderation audit trails
- **datetime**: Time-based operations for log file rotation and timestamps
- **pathlib**: Modern file system path handling for log directory management
- **os**: Environment variable access for secure token management
- **asyncio**: Asynchronous runtime for Discord bot operations

## File System
- **Local Log Storage**: Stores daily rotating log files in local "logs" directory
- **UTF-8 Encoding**: Ensures proper character encoding for international usernames and messages