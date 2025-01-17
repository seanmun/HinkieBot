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
    "Trust the Process.",
    # ... (keeping other quotes)
]

# League Information
LEAGUE_INFO = {
    "rules": (
        "Money Never Sleeps (MNS) League Rules:\n\n"
        "• Teams must stay under the NBA salary cap\n"
        "• Weekly head-to-head matchups\n"
        "• Over-cap teams face monetary penalties\n"
        "[Add specific rules here]"
    ),
    "settings": (
        "League Settings:\n\n"
        "• Platform: Fantrax\n"
        "• Scoring Type: Head-to-Head\n"
        "• Salary Cap: Current NBA cap\n"
        "[Add specific settings here]"
    ),
    "prize": (
        "Prize Structure:\n\n"
        "[Add prize pool and distribution details]"
    ),
    "keeper": (
        "Keeper Rules:\n\n"
        "[Add keeper rules and restrictions]"
    ),
    "redshirt": (
        "Redshirt Rules:\n\n"
        "[Add redshirt eligibility and rules]"
    ),
    "cap": (
        "Salary Cap Information:\n\n"
        "• Current NBA Cap: $[amount]\n"
        "• Penalty for exceeding: [details]\n"
        "[Add cap rules and details]"
    ),
    "dues": (
        "League Dues:\n\n"
        "[Add dues amount and payment details]"
    ),
    "franchise": (
        "Franchise Rules:\n\n"
        "[Add franchise player rules and limitations]"
    ),
    "draft": (
        "Draft Information:\n\n"
        "[Add draft format, order, and rules]"
    )
}

async def start(update, context):
    """Send a message when the command /start is issued."""
    print(f"Start command received")
    await update.message.reply_text(
        'Trust The Process! 🏀\n\n'
        'How to get wisdom from Sam Hinkie:\n'
        '1. Reply to any of my messages\n'
        '2. Say "Hinkie" or "Sam Hinkie" in any message\n'
        '3. Tag @Sam_Hinkie_bot\n\n'
        'League Commands:\n'
        '/rules - League rules\n'
        '/settings - League settings\n'
        '/prize - Prize structure\n'
        '/keeper - Keeper rules\n'
        '/redshirt - Redshirt rules\n'
        '/cap - Salary cap info\n'
        '/dues - League dues\n'
        '/franchise - Franchise rules\n'
        '/draft - Draft information'
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

async def league_command(update, context):
    """Handle league information commands."""
    command = update.message.text[1:].lower()  # Remove the / and convert to lowercase
    if command in LEAGUE_INFO:
        await update.message.reply_text(LEAGUE_INFO[command])
    else:
        await update.message.reply_text("Command not found. Use /start to see available commands.")

def main():
    """Start the bot."""
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add handlers for all league commands
    for command in LEAGUE_INFO.keys():
        application.add_handler(CommandHandler(command, league_command))
    
    # Add message handler for Hinkie quotes
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