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

