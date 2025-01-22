# Sam Hinkie Bot (@Sam_Hinkie_bot)

A Telegram bot for fantasy basketball league management, powered by the wisdom of Sam Hinkie. This bot helps manage league information, provides Hinkie quotes, and facilitates league communication while maintaining the spirit of "Trust the Process."

## Features

### Sam Hinkie Quotes
Get inspirational quotes from Sam Hinkie by:
- Replying to any bot message
- Mentioning "Hinkie" in chat
- Tagging @Sam_Hinkie_bot

### League Information Commands
- `/rules` - League rules
- `/settings` - League settings
- `/prize` - Prize structure
- `/keeper` - Keeper rules
- `/redshirt` - Redshirt rules
- `/cap` - Salary cap info
- `/dues` - League dues
- `/franchise` - Franchise rules
- `/draft` - Draft information

## Project Structure
```
HinkieBot/
├── bot/
│   ├── main.py              # Main bot code
│   └── requirements.txt     # Python dependencies
├── Procfile                 # Railway deployment config
└── .env                     # Environment variables
```

## Deployment

This bot is configured for deployment on Railway. The `Procfile` contains the necessary commands for Railway to run the bot.

## Coming Soon

- Weekly matchup reports
- Real-time transaction announcements
- Player information lookup
- Team information tracking
- Fantrax API integration

## Acknowledgments

- Sam Hinkie for his timeless wisdom
- python-telegram-bot library
- Fantrax for fantasy basketball platform

## Fantrax Telegram Bot Project Brief
### Project Overview

A Telegram bot (@Sam_Hinkie_bot) that integrates with Fantrax fantasy basketball platform. The bot provides league information and Sam Hinkie quotes while maintaining the theme of "Trust The Process."
Project Structure

CopyHinkieBot/
├── bot/
│   ├── main.py              # Main bot code
│   └── requirements.txt     # Python dependencies
├── Procfile                 # Railway deployment config
└── .env                     # Environment variables

### Key Dependencies
Copypython-telegram-bot==20.8
python-telegram-bot[job-queue]
python-dotenv==1.0.1
aiohttp==3.9.1

### Environment Variables

BOT_TOKEN: Telegram bot token
FANTRAX_LEAGUE_ID: League ID from Fantrax
CHAT_ID: Telegram chat ID

### Fantrax API Integration

Base URL: https://www.fantrax.com/fxpa/req
Authentication: Uses JSESSIONID cookie
Key Endpoints:

getAdp: Gets player information
leagueInfo: Gets league information
getPlayerIds: Gets all player IDs



## Current Features

League information commands (/rules, /settings, etc.)
Sam Hinkie quote responses
Basic Fantrax integration for player/team info

Current Challenges

Fantrax API authentication and session management
Player data retrieval and formatting
API endpoint structure discovery

API Response Format Example
Player data comes in this format:
jsonCopy{
    "pos": "PG",
    "name": "Player Name",
    "id": "12345",
    "ADP": 123.4
}
Important Notes

The bot runs on Railway
Authentication uses cookie-based sessions
All API responses need error handling
Responses should maintain Sam Hinkie's persona

Development Status
Currently implementing Fantrax API integration, specifically focusing on player information retrieval and proper error handling.