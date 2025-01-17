import os
from dotenv import load_dotenv
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
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
        "*Money Never Sleeps (MNS) League Rules:*\n\n"
        "League fee is $50. Twelve team league. Each team will have a salary cap of $170,000,000. The combination of your teams' player salaries cannot surpass $170M without penalty. If you surpass salary cap, you will have to pay an additional $50 that goes to the prize pool. If you surpass and pay your penalty, you can stay above $170M for the remainder of the season. The hard cap of $210,000,000.\n\n"
        "Starting in the 2024-25 season, MNS will be taking it's talents to the Fantrax app. Fantrax includes player salary and team salary caps. Fantrax salary will be set to $210,000,000. It will not let you execute any roster moves that go over this amount. Fantrax offers an option to trade salary cap between teams. This will be enabled. All teams must staty above 170m in salary cap. This means they can trade up to $40m in cap space at a maximum. The most cap space you can trade for is also $40m, bringing the max cap to $250,000,000. A team that exceeds the the second apron cap of $210m, will pay a penalty of $2 per million (rounded up). So if you trade for $4m and have a cap of $214, you will pay an additional $8 into the prize pool pot. if you trade for $40m, you will pay an additional $80 into the pot.\n\n"

    ),
    "settings": (
        "*League Settings:*\n\n"
        "*Platform*: Fantrax\n\n"
        "*Scoring Type*: weekly head-to-head with one opponent each week, earning a win or loss for each stat category. The regular season is 14 weeks. There are 9 stat categories in total: Points, Blocks, Steals, Assists, Rebounds, Ast/TO Ratio, Three-Pointers Made, Field Goal Percentage, and Free Throw Percentage.\n\n"
        "*Roster*: There will be 10 spots for active players each night and they can play unlimited games each week. There will also be 4 bench spots which equate to 14 players per team. In addition, there is 1 IR spot for injured players only. The IR spots WILL count against your cap.\n\n"
        "*Playoffs*: Six teams make the playoffs. The top two have a bye. Six teams who don't make playoffs will be placed in the consolation bracket where they will battle for rights to the top Rookie Draft lottery odds.\n\n"
        "*This is a dynasty league*: You can keep up to 8 players season to season. So as you draft, make sure to have the longest view in the room. You are now a General Manager and solely responsible for the future of your franchise."
    ),
    "prize": (
        "*Prize Structure:*\n\n"
        "*Boiler Room Rule* — prize pool declines:\n"
        "• If the prize pool falls below the initial investment, the payout will be 80% to first and 20% to second place.\n"
        "• If the prize pool falls below $300 payout will be 100% to first.\n"
        "• If the prize pool falls to $150, we cash out, 100% to first.\n\n"
        "*Gordon Gekko Rule* — prize pool grows:\n"
        "• 70% to first\n"
        "• 20% to second\n"
        "• 10% to third\n\n"
        "*Bernie Sanders Rule* — prize pool grows to $10,000+:\n"
        "• 40% to first\n"
        "• 15% to second\n"
        "• 9% to third\n"
        "• 4% to the remaining teams"
    ),
    "keeper": (
        "*Keeper Rules:*\n\n"
        "•	One week prior to the free-agent draft, each team will have the option to select their keepers. Each team can keep up to 8 but do not have to keep any. Keepers will be assigned to a draft round based on the previous years draft placement minus 1 round (exceptions with keeper stacking).\n\n"
        "*Keeper Stacking Rules*:\n"
        "_Rookies Keepers:_\n"
        "•	The rookie draft is 4 rounds. 1st round picks 1-3 will be a 5th round keeper. 1st round picks 4-6 will be a 6th round keeper. 1st round picks 7-9 will be a 7th round keeper. 1st round picks 10-12 will be an 8th round keeper.\n"
        "•	Rookies drafted in rounds 2 and 3 will be the 14th round regular season keeper.\n"
        "•	If redshirted, keeper rounds will stay the same for the following year.\n\n"
        "_Bottom of Draft:_\n"
        "•	If more than one player has the same keeper round, then the owner must assign a draft round to each player working their way down from 14-1. If while working your way down, you reach the top of the draft, you can follow Top of Draft rules.\n\n"
        "_Top of Draft:_\n"
        "•	First Round Keeper: Each team can only keep one 1st round keeper. With the exception to the Franchise Tag Fee.\n"
        "•	Each team can use a Franchise Tag Fee to keep additional 1st round keepers. The Franchise Tag costs $15 per additional 1st round keeper. The $15 will be placed into the prize pool.\n"
        "•	If a team keeps more than one 1st round Keeper, they will work backward in assigning the draft round for the regular season draft from 1-14.[EXAMPLE] PJ keeps LeBron and Durant, he can assign LeBron to the 1st round and Durant to the 2nd round. If he already has a second-round keeper, that player will move back to a 3rd round keeper, and so on."

    ),
    "redshirt": (
        "*Redshirt Rules:*\n\n"
        "•	Each team has the option to redshirt any drafted rookie for $10 each.\n"
        "•	Redshirt rookies must be submitted before the keeper deadline. Redshirt players salary will not count against the cap, not count as a keeper. Only players in their first contact year are eligible to be redshirted.\n"
        "•	The team of the redshirt player may pay a fee of $25 to activate the redshirt anytime during the season.\n"
        "•	If redshirted, keeper rounds will stay the same for the following year."
    ),
    "cap": (
        "*Salary Cap Information:*\n\n"
        "*Salary Cap*: $170,000,000\n"
        "*First Apron*: $210,000,000\n"
        "*Second Apron*: $250,000,000\n\n"
        "/dues to see cap related fee structure"
    ),
    "dues": (
        "*League Dues:*\n\n"
        "*Buy-in:*: $50\n"
        "*Into First Apron*: $50\n"
        "*nto Second Apron*: $2 ever 1mil over 210m\n"
        "*Franchise fee*: $15\n"
        "*Redshirt fee*: $10\n"
        "*Activate redshirt*: $25\n"
        "*Disrespecting Commish*: $1-5"
    ),
    "franchise": (
        "*Franchise Rules:*\n\n"
        "To keep more than one 1st round keeper, you must pay $15 for each additional first-round keeper. "
    ),
    "draft": (
        "*Draft Information:*\n\n"
        "/rookie \n"
        "/regular "
    ),
    "rookie": (
        "*Rookie Draft Information:*\n\n"
        "Each year we will have a three round rookie draft in the month of July. The first round will proceed the day of the actual NBA draft (starting a midnight 00:00 EST) and finishing prior to the actual NBA draft at 15:00 EST. All picks in the first round must be completed before the first pick in the actual NBA draft is made. This will add some suspense to see which team your drafted player lands on. Last two rounds happen immediately following the conclusion of the NBA draft. \n\n"
        "The MNS rookie draft order will be a similar to the actual NBA lottery, with a slight twist. Only teams who did not finish in the money are eligible for the lottery (unless a pick was traded to you). For those eligible, the lottery is weighted so that the team with the worst record, or the team that holds the draft rights of the team with the worst record, has the best chance to obtain a higher draft pick. However, instead of the worst team winning the best odds, MNS will award the best lottery odds to the team who wins the most match-ups in the consolation playoff bracket. Once odds are assigned, draftpicklottery.com will determine the draft order. \n\n"
        "International prospects are eligible. If you pick an international prospect, you own his rights until his first NBA contract begins. At which point, you will have the option to keep, trade or drop your international player. So make sure your scouting department has a global reach. \n\n"
        "Draft picks and international player stashes can be traded at any point in the season or off season. Future rookie draft picks can be traded up to 3 years in advance."
    ),
    "regular": (
        "*Regular Season Draft Information:*\n\n"
        "The regular season draft is a 14 round snake draft. Draft order will be randomized. One week prior to the free agent draft, each team will have the option to select their keepers. Each team can keep up to 8 but do not have to keep any. Keepers will be assigned to a draft round based on the previous year’s draft placement minus 1 round (exceptions with keeper stacking). \n\n"
    ),
    "recordbook": (
        "*All time records:*\n\n"
        "*1st places*: \n"
        "•	Kirbiak 3\n"
        "•	Sean 2\n"
        "•	Rick 2\n"
        "•	Tea Mike \n"
        "•	Ian\n"
        "•	Woods\n"
        "•	Bad \n"
        "•	Stine \n\n"

        "*2nd places*:\n"
        "•	Sean 3\n"
        "•	Bad 3\n"
        "•	Woods 2\n"
        "•	Kirbiak\n"
        "•	Tea Mike\n"
        "•	Pudd\n"
        "•	Rick\n\n"

        "*3rd places*:\n"
        "•	Sean 3\n"
        "•	Stine 3\n"
        "•	Rick 2 \n"
        "•	Kirbiak 2\n"
        "•	Ian \n"
        "•	PJ\n\n"
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

    # Check if it's a reply to the bot
    reply_to = update.message.reply_to_message
    if reply_to and reply_to.from_user and reply_to.from_user.username == "Sam_Hinkie_bot":
        print("Found reply to bot")
        quote = random.choice(HINKIE_QUOTES)
        await update.message.reply_text(f"{quote} - Sam Hinkie",
         parse_mode=ParseMode.MARKDOWN
         )
        return

    # Convert message to lowercase for checking
    text_lower = text.lower()

    # Check for Hinkie mentions
    if 'hinkie' in text_lower or 'sam hinkie' in text_lower or '@sam_hinkie_bot' in text_lower:
        print(f"Found keyword in: {text}")
        quote = random.choice(HINKIE_QUOTES)
        await update.message.reply_text(f"{quote} - Sam Hinkie",
        parse_mode=ParseMode.MARKDOWN
        )
        return

    # Check for team owner names
    if 'ian' in text_lower:
        await update.message.reply_text("🐍")
        return
        
    if 'pjio' in text_lower:
        await update.message.reply_text("🤌🤌 heeeyy gabagol")
        return
        
    if 'kirbiak' in text_lower:
        await update.message.reply_text("🥷🥷 twinjas")
        return
        
    if 'pudd' in text_lower:
        await update.message.reply_text("Dave 🤴🏻")
        return


    # league commands
async def league_command(update, context):
    """Handle league information commands."""
    command = update.message.text[1:].lower()  # Remove the / and convert to lowercase
    if command in LEAGUE_INFO:
        await update.message.reply_text(
            LEAGUE_INFO[command],
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "Command not found. Use /start to see available commands.",
            parse_mode=ParseMode.MARKDOWN  # Add parse_mode here too
        )

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