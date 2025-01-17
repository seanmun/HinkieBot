import os
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Sam Hinkie quotes
HINKIE_QUOTES = [
    "The goal is not to be the richest guy in the cemetery.",
    "We focus on process rather than outcome.",
    "You have to be willing to get uncomfortable to get comfortable.",
    "The first step in a process is to understand the end goal.",
    "You don't get to the moon by climbing a tree.",
    "A competitive advantage can be found in many places.",
    "The longest view in the room.",
    "We want to be the best at getting better.",
    "Progress isn't linear.",
    "Trust the Process."
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Trust The Process! 🏀\nTag me in any message to get a Sam Hinkie quote.')

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to mentions with a random Hinkie quote."""
    quote = random.choice(HINKIE_QUOTES)
    await update.message.reply_text(f'"{quote}" - Sam Hinkie')

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set!")

    # Create application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.MENTION | filters.Regex(r'@Sam_Hinkie_bot'),
        handle_mention
    ))

    # Start the bot
    logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()