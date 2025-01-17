import os
from dotenv import load_dotenv
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Sam Hinkie quotes - without quotation marks since he's speaking directly
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
    "Trust the Process.",
    "If you want to have real success you have to very often be willing to do something different from the herd.",
    "You don't get to the moon by climbing a tree.",
    "It's about having the longest view in the room.",
    "Fear has been the dominant motivator of the actions of our competitors.",
    "We should attempt to gain a competitive advantage everywhere we can.",
    "Options can be really valuable when they aren't encumbered by wound healing.",
    "Maintain the longest view in the room.",
    "There has to be a willingness to plant seeds that won't grow for a while.",
    "This is a status quo league, and it has been for a long time.",
    "If we all did what everyone else did, the league would be a bell curve.",
    "The illusion of control is an opiate.",
    "You have to be comfortable doing things others aren't.",
    "Value creation takes time.",
    "People talk about process but they don't really mean it.",
    "Innovation is about finding a different path forward.",
    "The gap between what you know and what others believe is often your edge.",
    "Time arbitrage is real.",
    "The NBA demands more than just raw talent.",
    "The only way to get the answers is to ask the right questions.",
    "Losing is not a complete failure if you learn from it."
]

async def start(update, context):
    """Send a message when the command /start is issued."""
    print(f"Start command received")
    await update.message.reply_text(
        'Trust The Process! 🏀\n\n'
        'How to get wisdom from Sam Hinkie:\n'
        '1. Reply to any of my messages\n'
        '2. Say "Hinkie" or "Sam Hinkie" in any message\n'
        '3. Tag @Sam_Hinkie_bot'
    )

async def handle_message(update, context):
    """Handle incoming messages."""
    if not update.message or not update.message.text:
        return
        
    text = update.message.text
    print(f"Received message: {text}")

    reply_to = update.message.reply_to_message
    if reply_to and reply_to.from_user and reply_to.from_user.username == "Sam_Hinkie_bot":
        print("Found reply to bot")
        quote = random.choice(HINKIE_QUOTES)
        await update.message.reply_text(f"{quote} - Sam Hinkie")
        return

    # Check message text (case insensitive)
    text_lower = text.lower()
    if 'hinkie' in text_lower or 'sam hinkie' in text_lower or '@sam_hinkie_bot' in text_lower:
        print(f"Found keyword in: {text}")
        quote = random.choice(HINKIE_QUOTES)
        await update.message.reply_text(f"{quote} - Sam Hinkie")

def main():
    """Start the bot."""
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    # Start the bot
    print("Bot is running! Press Ctrl+C to stop.")
    application.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,
        poll_interval=1.0
    )

if __name__ == "__main__":
    main()