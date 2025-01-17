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

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/HinkieBot.git
cd HinkieBot
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r bot/requirements.txt
```

4. Create a `.env` file in the root directory with your bot token:
```
BOT_TOKEN=your_telegram_bot_token
```

5. Run the bot
```bash
python bot/main.py
```

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Sam Hinkie for his timeless wisdom
- python-telegram-bot library
- Fantrax for fantasy basketball platform