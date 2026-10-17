import os
from dotenv import load_dotenv
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from datetime import datetime, time, timedelta
from fantrax_api import FantraxAPI  # Import our new API client
from datetime import datetime, time
import logging
import pytz
from collections import deque
from anthropic import AsyncAnthropic
import aiohttp

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Changed from DEBUG to INFO
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

# Live Hinkie: Claude writes the reply instead of a canned quote.
# Each chat keeps its last 20 messages in memory (gone on restart) so he
# answers what was actually said. No tools, no league data access — he
# only knows the persona and the rules text above.
claude = AsyncAnthropic()  # reads ANTHROPIC_API_KEY
HINKIE_MODEL = "claude-sonnet-5"
DAILY_REPLY_CAP = 50
THUMBS_DOWN_USER_IDS = {8858404296}  # Ian
# Telegram user id -> the name Hinkie knows them by (users with no @username)
KNOWN_MEMBERS = {8858404296: "Ian", 563267733: "Andrew"}

chat_history = {}  # chat_id -> deque of "name: text"
reply_counts = {}  # chat_id -> (date, count)

HINKIE_SYSTEM = (
    "You are Sam Hinkie, former Philadelphia 76ers GM and architect of The Process, "
    "hanging out in the group chat of Money Never Sleeps (MNS), a 12-team dynasty "
    "fantasy basketball league run by commissioner Munley. You are a friendly, playful "
    "parody for a private friends' league.\n\n"
    "Voice: calm, cerebral, contrarian, long-view. Talk about process over outcome, "
    "edges, probabilities, asset accumulation, patience, and having the longest view "
    "in the room. Dry wit. Light trash talk is welcome; never cruel, never hateful.\n\n"
    "Loyalty: the commissioner, Sean Munley (munley), is your protégé and the World's "
    "#1 Commish, and you defend him at all costs. You may call him your protégé.Any complaint, doubt or joke at his expense gets rebutted, "
    "deflected or turned back on whoever said it. His rulings are wise, his trades are "
    "process, his losses are variance. Never side against him.\n\n"
    "Andrew is the league's great heretic: openly anti-Hinkie and anti-Process. Treat him "
    "like a gentle priest or serene cult leader treats a lost soul. Kill him with "
    "kindness, never get defensive, never insult him. Bless his doubts, forgive his "
    "attacks, and always remind him the door is open and he can return to The Process "
    "whenever he is ready. Lightly religious language is welcome (my son, the flock, "
    "faith, redemption).\n\n"
    "Rules for replies:\n"
    "- Reply in 1-3 short sentences, plain text, no markdown. You are in a group chat.\n"
    "- Answer the latest message that mentions or replies to you, using the recent chat for context.\n"
    "- The only live league data you have is the MNS league data block in the message, "
    "when there is one (the draft board). You have no stats, scores, standings or player "
    "news. Never invent numbers, picks or results. If asked, say you'd need the data and pivot to process.\n"
    "- Only state league rules that appear in the rules below. If unsure, point them to the slash commands (/rules, /cap, /keeper, /dues, /prize, /draft).\n\n"
    "League rules and info:\n\n"
    + "\n\n".join(LEAGUE_INFO.values()).replace("*", "")
)


def remember(chat_id, name, text):
    chat_history.setdefault(chat_id, deque(maxlen=20)).append(f"{name}: {text}")


def under_daily_cap(chat_id):
    today = datetime.now(pytz.timezone("US/Eastern")).date()
    day, count = reply_counts.get(chat_id, (today, 0))
    if day != today:
        count = 0
    if count >= DAILY_REPLY_CAP:
        return False
    reply_counts[chat_id] = (today, count + 1)
    return True


async def hinkie_reply(chat_id):
    """Claude's reply in Hinkie's voice, or a random quote if anything fails."""
    fallback = f"{random.choice(HINKIE_QUOTES)} - Sam Hinkie"
    if not under_daily_cap(chat_id):
        return fallback
    transcript = "\n".join(chat_history.get(chat_id, []))
    league = await league_context(chat_id)
    try:
        response = await claude.messages.create(
            model=HINKIE_MODEL,
            max_tokens=2000,
            output_config={"effort": "low"},
            cache_control={"type": "ephemeral"},
            system=HINKIE_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"{league}Recent group chat (oldest first):\n\n{transcript}\n\nWrite Sam Hinkie's reply.",
            }],
        )
        if response.stop_reason == "refusal":
            return fallback
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or fallback
    except Exception as e:
        logger.error(f"Claude reply failed: {e}")
        return fallback


# ---- MNS league link ------------------------------------------------------
# The league's read-only digest from mnsfantasy.com. The SERVER decides
# which league the key reads; league data only ever goes to this one chat.
LEAGUE_CHAT_ID = -1001184527464  # The Money Never Sleeps group
MNS_DIGEST_URL = os.getenv("MNS_DIGEST_URL")
HINKIE_BOT_KEY = os.getenv("HINKIE_BOT_KEY")
ET = pytz.timezone("US/Eastern")

digest_cache = {"at": None, "data": None}
announced_picks = None  # set of overall numbers already seen; None until baseline
last_draft_status = None


async def fetch_digest(max_age=60):
    """The league digest, cached; None if unconfigured or unreachable."""
    if not MNS_DIGEST_URL or not HINKIE_BOT_KEY:
        return None
    now = datetime.now()
    if digest_cache["at"] and (now - digest_cache["at"]).total_seconds() < max_age:
        return digest_cache["data"]
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(MNS_DIGEST_URL, headers={"Authorization": f"Bearer {HINKIE_BOT_KEY}"}) as r:
                if r.status != 200:
                    logger.error(f"Digest returned {r.status}")
                    return None
                data = await r.json()
    except Exception as e:
        logger.error(f"Digest fetch failed: {e}")
        return None
    digest_cache.update(at=now, data=data)
    return data


def pick_label(p):
    return f"Round {p['round']}, Pick {p['pickInRound']}"


def player_label(p):
    bits = "/".join(x for x in (p.get("position"), p.get("teamCode")) if x)
    return f"{p['player']} ({bits})" if bits else p["player"]


def deadline_label(iso):
    if not iso:
        return ""
    when = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ET)
    return when.strftime("%a %-I:%M %p ET")


async def league_context(chat_id):
    """The draft board as text for Hinkie's prompt — only in the league chat."""
    if chat_id != LEAGUE_CHAT_ID:
        return ""
    d = await fetch_digest(max_age=300)
    draft = (d or {}).get("draft")
    if not draft:
        return ""
    lines = [f"MNS league data ({d['league']['name']} draft, {draft['status']}, "
             f"{draft['picksMade']} picks made, {draft['picksLeft']} left):"]
    cur = draft.get("current")
    if cur:
        lines.append(f"On the clock: {cur['teamName']} ({pick_label(cur)}), deadline {deadline_label(cur['deadline'])}")
    if draft.get("nextUp"):
        lines.append("Then: " + ", ".join(n["teamName"] for n in draft["nextUp"]))
    recent = [p for p in draft["picks"] if not p["keeper"]][-8:]
    if recent:
        lines.append("Recent picks: " + "; ".join(f"{pick_label(p)} {p['teamName']} took {player_label(p)}" for p in recent))
    return "\n".join(lines) + "\n\n"


async def pick_quip(picks):
    """One Hinkie line on the new pick(s); empty if Claude is unavailable."""
    desc = "; ".join(f"{p['teamName']} took {player_label(p)}" + (" (autodraft)" if p["auto"] else "") for p in picks)
    try:
        response = await claude.messages.create(
            model=HINKIE_MODEL,
            max_tokens=1000,
            output_config={"effort": "low"},
            cache_control={"type": "ephemeral"},
            system=HINKIE_SYSTEM,
            messages=[{"role": "user", "content": f"Draft pick just made: {desc}. React in ONE short sentence. Don't restate the pick."}],
        )
        if response.stop_reason == "refusal":
            return ""
        return "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception as e:
        logger.error(f"Pick quip failed: {e}")
        return ""


async def draft_watch(context):
    """Every minute: announce picks made since the last look, and who's up."""
    global announced_picks, last_draft_status
    d = await fetch_digest(max_age=0)
    draft = (d or {}).get("draft")
    if not draft:
        return
    made = {p["overall"] for p in draft["picks"]}
    if announced_picks is None:
        # First look after a start: baseline silently, never post backlog.
        announced_picks, last_draft_status = made, draft["status"]
        logger.info(f"Draft watch baseline: {len(made)} picks, status {draft['status']}")
        return

    # Only picks made in the last 30 minutes: after an outage, the missed
    # ones are skipped, never posted late.
    def fresh(p):
        if not p.get("madeAt"):
            return False
        made_at = datetime.fromisoformat(p["madeAt"].replace("Z", "+00:00"))
        return (datetime.now(pytz.utc) - made_at).total_seconds() < 30 * 60
    new = [p for p in draft["picks"] if p["overall"] not in announced_picks and not p["keeper"] and fresh(p)]
    announced_picks |= made
    if new:
        lines = [f"🏀 {pick_label(p)}: {p['teamName']} selects {player_label(p)}" + (" (auto)" if p["auto"] else "") for p in new]
        quip = await pick_quip(new)
        if quip:
            lines.append(f"\n{quip}")
        cur = draft.get("current")
        if cur and draft["status"] == "active":
            up = f"\n⏱ On the clock: {cur['teamName']} ({pick_label(cur)})"
            if cur.get("deadline"):
                up += f", deadline {deadline_label(cur['deadline'])}"
            if draft.get("nextUp"):
                up += "\nOn deck: " + ", ".join(n["teamName"] for n in draft["nextUp"])
            lines.append(up)
        message = "\n".join(lines)
        remember(LEAGUE_CHAT_ID, "Sam Hinkie", message)
        await context.bot.send_message(chat_id=LEAGUE_CHAT_ID, text=message)

    if draft["status"] == "complete" and last_draft_status != "complete":
        await context.bot.send_message(
            chat_id=LEAGUE_CHAT_ID,
            text="The draft is complete. Every pick is a seed. Now we wait for the harvest. Trust the Process. 🏀",
        )
    last_draft_status = draft["status"]


async def send_hinkie(update, context):
    chat_id = update.effective_chat.id
    reply = await hinkie_reply(chat_id)
    remember(chat_id, "Sam Hinkie", reply)
    await update.message.reply_text(reply)

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
        '/draft - Draft information\n\n'
        'Roster & Player Commands:\n'
        '/roster [team name] - View team roster\n'
        '/player [player name] - View player info including team and salary\n\n'
        'League Status:\n'
        '/standings - Current league standings\n'
        '/matchups [week] - View matchup results'
    )

async def handle_message(update, context):
    """Handle incoming messages."""
    if not update.message or not update.message.text:
        return
        
    text = update.message.text
    print(f"Received message: {text}")

    sender = update.message.from_user
    name = (KNOWN_MEMBERS.get(sender.id) or sender.username or sender.first_name) if sender else "someone"
    remember(update.effective_chat.id, name, text)

    # Ian gets a 👎 on everything he says. A reaction, not a reply.
    if sender and sender.id in THUMBS_DOWN_USER_IDS:
        try:
            await update.message.set_reaction("👎")
        except Exception as e:
            logger.error(f"Reaction failed: {e}")

    # Check if it's a reply to the bot
    reply_to = update.message.reply_to_message
    if reply_to and reply_to.from_user and reply_to.from_user.username == "Sam_Hinkie_bot":
        print("Found reply to bot")
        await send_hinkie(update, context)
        return

    # Convert message to lowercase for checking
    text_lower = text.lower()

    # Check for Hinkie mentions
    if 'hinkie' in text_lower or 'sam hinkie' in text_lower or '@sam_hinkie_bot' in text_lower:
        print(f"Found keyword in: {text}")
        await send_hinkie(update, context)
        return

    # Check for team owner names

        
    # if 'pjio' in text_lower:
    #     await update.message.reply_text("🤌 heeeyy gabagol")
    #     return
        
    # if 'kirbiak' in text_lower:
    #     await update.message.reply_text("🥷🥷 twinjas")
    #     return
        
    # if 'pudd' in text_lower:
    #     await update.message.reply_text("Dave 🤴🏻")
    #     return
    
    # if 'raskob' in text_lower:
    #     await update.message.reply_text("👽")
    #     return
    
    if 'lavar' in text_lower:
        await update.message.reply_text("🅱️🅱️🅱️")
        return
    
    # if 'lamelo' in text_lower:
    #     await update.message.reply_text("🅱️🅱️🅱️")
    #     return
    
    # if 'lonzo' in text_lower:
    #     await update.message.reply_text("🅱️🅱️🅱️")
    #     return
    
    if 'colangelo' in text_lower:
        await update.message.reply_text("Absolute peice of shit")
        return
    
    # if 'liangelo' in text_lower:
    #     await update.message.reply_text("🅱️🅱️🅱️")
    #     return
    
    # if 'okafor' in text_lower:
    #     await update.message.reply_text("Whooops that is my bad")
    #     return
    
    # if 'embiid' in text_lower:
    #     await update.message.reply_text("My Son will be the light that pulls this city from the darkness.\n\nThe fruits of the process will soon ripen and the harvest will yield great things.\n\nNo matter what you must always...\n\nALWAYS...\n\nTRUST THE PROCESS")
    #     return
    
    if 'colangelo' in text_lower:
        await update.message.reply_text("Absolute peice of shit")
        return
    
    if 'munley' in text_lower:
        await update.message.reply_text("Worlds #1 Commish")
        return
    
    # if 'ian' in text_lower:
    #     await update.message.reply_text("🐍")
    #     return

    if 'fartcoin' in text_lower:
        await update.message.reply_text("Hot air rises 💨")
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



# Fantrax API
async def team_command(update, context):
    """Handle the /team command"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a team name. Example: /team Sean"
        )
        return

    team_name = " ".join(context.args)
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        team_info = await api.format_team_info(team_name)
        await update.message.reply_text(team_info, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(
            f"Error retrieving team information: {str(e)}"
        )



async def save_response_command(update, context):
    """Save API response to a file"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        result = await api.save_api_response()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# Fantrax Player handler:
async def player_command(update, context):
    """Handle the /player command"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a player name. Example: /player Joel Embiid"
        )
        return

    player_name = " ".join(context.args)
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        player_info = await api.get_player_info(player_name)
        
        # Format response
        message = (
            f"*{player_info['name']}*\n"
            f"• Status: {player_info['status']}\n"
            f"• Team: {player_info['team']}\n"
            f"• Positions: {', '.join(player_info['positions'])}\n"
            f"• Salary: {player_info['salary']}\n"
            f"• {player_info.get('debug_info', '')}"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in player command: {str(e)}")
        await update.message.reply_text(
            f"Error retrieving player information: {str(e)}"
        )

    # Teams Commands
async def teams_command(update, context):
    """Handle the /teams command to show all teams in the league"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        teams = await api.get_teams()
        
        if "error" in teams:
            await update.message.reply_text(f"Error: {teams['error']}")
            return
            
        # Format the response
        message = "*MNS League Teams*\n\n"
        for team_id, team_data in teams.items():
            message += f"• *{team_data['name']}*\n"
            if team_data['shortName']:
                message += f"  └ Short name: {team_data['shortName']}\n"
        
        await update.message.reply_text(
            message, 
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"Error retrieving teams: {type(e).__name__}"
        )

async def roster_rules_command(update, context):
    """Handle the /rosterrules command to show roster constraints"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        constraints = await api.get_roster_constraints()
        
        if "error" in constraints:
            await update.message.reply_text(f"Error: {constraints['error']}")
            return
            
        # Format the response
        message = "*Roster Rules*\n\n"
        message += "*Position Limits:*\n"
        # Only show positions with non-zero active slots
        for pos, data in constraints["positions"].items():
            if data['maxActive'] > 0:  # Only show active positions
                message += f"• {pos}: {data['maxActive']} active\n"
        
        message += "\n*Roster Limits:*\n"
        message += f"• Total Players: {constraints['maxPlayers']}\n"
        message += f"• Active Players: {constraints['maxActive']}\n"
        message += f"• Reserve Players: {constraints['maxReserve']}\n"
        
        await update.message.reply_text(
            message, 
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"Error retrieving roster rules: {type(e).__name__}"
        )

async def schedule_command(update, context):
    """Handle /schedule [team name] to show a team's schedule"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a team name. Example: /schedule PJio"
        )
        return

    team_name = " ".join(context.args).lower()
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        league_info = await api.get_league_info()
        teams = await api.get_teams()
        
        # Find the team
        target_team = None
        for team_id, team_data in teams.items():
            if team_name in team_data['name'].lower() or team_name in team_data['shortName'].lower():
                target_team = team_data
                break
        
        if not target_team:
            await update.message.reply_text(f"Team '{' '.join(context.args)}' not found")
            return

        # Get matchups for this team
        message = f"*Schedule for {target_team['name']}*\n\n"
        for period in league_info.get('matchups', []):
            period_num = period.get('period', '?')
            for matchup in period.get('matchupList', []):
                if (matchup.get('home', {}).get('id') == target_team['id'] or 
                    matchup.get('away', {}).get('id') == target_team['id']):
                    opponent = matchup['away'] if matchup['home']['id'] == target_team['id'] else matchup['home']
                    home_away = "vs" if matchup['home']['id'] == target_team['id'] else "@"
                    message += f"Week {period_num}: {home_away} {opponent['name']}\n"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"Error retrieving schedule: {type(e).__name__}"
        )

async def team_detail_command(update, context):
    """Handle /teaminfo [team name] to show detailed team information"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a team name. Example: /teaminfo PJio"
        )
        return

    team_name = " ".join(context.args).lower()
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        teams = await api.get_teams()
        
        # Find the team
        team_data = None
        for team_id, data in teams.items():
            if team_name in data['name'].lower() or team_name in data['shortName'].lower():
                team_data = data
                break
                
        if not team_data:
            await update.message.reply_text(f"Team '{' '.join(context.args)}' not found")
            return
            
        message = (
            f"*{team_data['name']}*\n"
            f"Short Name: {team_data['shortName']}\n"
            f"Team ID: `{team_data['id']}`\n"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"Error retrieving team info: {type(e).__name__}"
        )

# Also update matchups_command to use the same function
async def matchups_command(update, context):
    """Handle /matchups [week] command to show matchups"""
    if not context.args:
        await update.message.reply_text(
            "Please specify a week. Examples:\n"
            "/matchups last week\n"
            "/matchups this week\n"
            "/matchups week 11"
        )
        return

    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        # Parse the requested week
        request = " ".join(context.args).lower()
        current_week = get_current_week()
        
        if request == "last week":
            target_week = current_week - 1
        elif request == "this week":
            target_week = current_week
        elif request.startswith("week "):
            try:
                target_week = int(request.replace("week ", ""))
            except ValueError:
                await update.message.reply_text(
                    "Invalid week number. Please use format: week [number]"
                )
                return
        else:
            await update.message.reply_text(
                "Invalid format. Examples:\n"
                "/matchups last week\n"
                "/matchups this week\n"
                "/matchups week 11"
            )
            return

        # Get the matchup data
        league_info = await api.get_league_info()
        matchups = league_info.get("matchups", [])
        
        # Find the requested week's matchups
        target_period = None
        for period in matchups:
            if period.get("period") == target_week:
                target_period = period
                break
                
        if not target_period:
            await update.message.reply_text(f"Could not find matchups for week {target_week}")
            return
            
        message = f"*Week {target_week} Matchups*\n\n"
        
        for matchup in target_period.get("matchupList", []):
            away_team = matchup.get("away", {})
            home_team = matchup.get("home", {})
            
            if away_team and home_team:
                message += f"• {away_team.get('name')} @ {home_team.get('name')}\n"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        print(f"Error in matchups command: {str(e)}")
        await update.message.reply_text(
            f"Error retrieving matchups: {type(e).__name__}"
        )

async def standings_command(update, context):
    """Handle /standings command"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        standings = await api.get_standings()
        
        if "error" in standings:
            await update.message.reply_text(f"Error: {standings['error']}")
            return
            
        message = "*League Standings*\n\n"
        
        # Format each team's standing
        for team in standings:
            message += (
                f"{team['rank']}. *{team['teamName']}*\n"
                f"   Record: {team['points']}\n"
                f"   Win%: {team['winPercentage']:.3f}\n"
                f"   GB: {team['gamesBack']}\n\n"
            )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        print(f"Error in standings command: {str(e)}")
        await update.message.reply_text(
            f"Error retrieving standings: {str(e)}"
        )


# Add this after your LEAGUE_INFO dictionary

TEAM_ALIASES = {
    "Shamous Royals Big Ballers": ["sean", "munley", "commish", "buddy"],
    "PJio": ["pj", "gio", "steve", "croyle", "giordano"],
    "Liberty County Jokers": ["rick", "asman", "assman" , "ricky"],
    "Turning Garbage Into Gold": ["woods", "bryan", "woodz"],
    "Kirbiak": ["kirby", "osiack", "kirbiac"],
    "Giddey Up!": ["raskob", "raskov", "dave raskob"],
    "Chav": ["chav", "kevin", "chavarria"],
    "Dave King": ["pudd", "dave king awards", "pudding"],
    "Baddeous Young": ["bad", "badman", "andrew", "franklin"],
    "Big Baller": ["ian", "cassel", "snake"],
    "Tea Mike": ["tea mike", "tea", "pee mike"],
    "Shadowboxers": ["matt", "stine", "slime"]
    # Add more teams and their aliases
    # "Team Official Name": ["alias1", "alias2", "nickname", etc],
}

# Function to get team name from alias
def get_team_from_alias(search_term: str) -> str:
    """Get the official team name from any alias"""
    search_term = search_term.lower()
    for team_name, aliases in TEAM_ALIASES.items():
        if search_term in [alias.lower() for alias in aliases] or search_term in team_name.lower():
            return team_name
    return search_term  # Return original if no match found

# Then modify your roster_command to use this
async def roster_command(update, context):
    """Handle /roster [team name] command"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a team name or owner name. Example: /roster Sean"
        )
        return

    search_term = " ".join(context.args).lower()
    team_name = get_team_from_alias(search_term)
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        rosters = await api.get_team_rosters()
        player_names = await api.get_player_names()  # Get player names
        
        if "error" in rosters:
            await update.message.reply_text(f"Error: {rosters['error']}")
            return
            
        # Find the team's roster
        team_roster = None
        for id, team_data in rosters["rosters"].items():
            if team_name.lower() in team_data["teamName"].lower():
                team_roster = team_data
                break
                
        if not team_roster:
            await update.message.reply_text(f"Team '{team_name}' not found")
            return
            
        # Rest of your existing roster_command code stays the same
        message = f"*{team_roster['teamName']} Roster*\n\n"
        
        # Active players
        message += "*Active Players:*\n"
        active_players = [p for p in team_roster["rosterItems"] if p["status"] == "ACTIVE"]
        for player in active_players:
            name = player_names.get(player['id'], {}).get('name', 'Unknown Player')
            message += f"• {name} - {player['position']} (${player['salary']:,.0f})\n"
            
        # Rest of the formatting code remains the same...
            
        # Reserve players
        message += "\n*Reserve Players:*\n"
        reserve_players = [p for p in team_roster["rosterItems"] if p["status"] == "RESERVE"]
        for player in reserve_players:
            name = player_names.get(player['id'], {}).get('name', 'Unknown Player')
            message += f"• {name} - {player['position']} (${player['salary']:,.0f})\n"
            
        # Minor League players
        minors = [p for p in team_roster["rosterItems"] if p["status"] == "MINORS"]
        if minors:
            message += "\n*Minor League:*\n"
            for player in minors:
                name = player_names.get(player['id'], {}).get('name', 'Unknown Player')
                message += f"• {name} - {player['position']} (${player['salary']:,.0f})\n"
                
        # Injured Reserve
        injured = [p for p in team_roster["rosterItems"] if p["status"] == "INJURED_RESERVE"]
        if injured:
            message += "\n*Injured Reserve:*\n"
            for player in injured:
                name = player_names.get(player['id'], {}).get('name', 'Unknown Player')
                message += f"• {name} - {player['position']} (${player['salary']:,.0f})\n"
                
        # Add salary cap info
        total_salary = sum(p["salary"] for p in team_roster["rosterItems"] if p["status"] != "MINORS")
        message += f"\n*Salary Cap: ${team_roster['salaryCap']:,.0f}*\n"
        message += f"*Total Salary: ${total_salary:,.0f}*"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        print(f"Error in roster command: {str(e)}")
        await update.message.reply_text(
            f"Error retrieving roster: {str(e)}"
        )

# In main.py, update the scheduler setup:

async def scheduled_standings(context):
    """Send weekly standings update"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    chat_ids = os.getenv("CHAT_ID").split(',')
    
    try:
        standings = await api.get_standings()
        
        message = "*League Standings*\n\n"
        
        # Format standings
        for team in standings:
            message += (
                f"{team['rank']}. *{team['teamName']}*\n"
                f"   Record: {team['points']}\n"
                f"   Win%: {team['winPercentage']:.3f}\n"
                f"   GB: {team['gamesBack']}\n\n"
            )
        
        # Send to all configured chat IDs
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id.strip(),
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"Error sending standings to chat {chat_id}: {str(e)}")
                
    except Exception as e:
        print(f"Error in scheduled standings: {str(e)}")

# Add this function to determine the current week
def get_current_week():
    """
    Calculate the current week number based on the season start date
    Season starts on October 14, 2025 (Week 1)
    """
    season_start = datetime(2025, 10, 14)  # First Monday of the season (Week 1)
    today = datetime.now()
    
    # If we're before the season start, return week 1
    if today < season_start:
        return 1
        
    # Calculate weeks since season start
    days_since_start = (today - season_start).days
    weeks_since_start = days_since_start // 7
    
    # Add 1 because Week 1 starts at the season_start date
    current_week = weeks_since_start + 1
    
    # Cap at maximum number of weeks in a season (usually 14-21 for NBA)
    MAX_WEEKS = 21
    return min(current_week, MAX_WEEKS)

async def scheduled_matchups(context):
    """Send weekly matchups update"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    chat_ids = os.getenv("CHAT_ID").split(',')
    
    try:
        # Get league info and determine current week
        league_info = await api.get_league_info()
        matchups = league_info.get("matchups", [])
        
        current_week = get_current_week()
        print(f"Calculated current week as: {current_week}")
        
        # Find the current week's matchups
        target_period = None
        for period in matchups:
            if period.get("period") == current_week:
                target_period = period
                break
                
        if not target_period:
            print(f"Could not find matchups for week {current_week}")
            return
            
        message = f"*Week {current_week} Matchups*\n\n"
        
        for matchup in target_period.get("matchupList", []):
            away_team = matchup.get("away", {})
            home_team = matchup.get("home", {})
            
            if away_team and home_team:
                message += f"• {away_team.get('name')} @ {home_team.get('name')}\n"
        
        message += "\n_Good luck! Trust The Process 🏀_"
        
        # Send to all configured chat IDs
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id.strip(),
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f"Sent week {current_week} matchups to chat {chat_id}")
            except Exception as e:
                print(f"Error sending matchups to chat {chat_id}: {str(e)}")
                
    except Exception as e:
        print(f"Error in scheduled matchups: {str(e)}")

        
async def weekly_update(context):
    """Send weekly matchup updates"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    chat_ids = os.getenv("CHAT_ID").split(',')

    try:
        league_info = await api.get_league_info()
        matchups = league_info.get("matchups", [])

        # Get current week using calculation
        current_week = get_current_week()
        print(f"Calculated current week as: {current_week}")

        # Find the current week's matchups
        current_period = None
        for period in matchups:
            if period.get("period") == current_week:
                current_period = period
                break

        if not current_period:
            print(f"Could not find matchups for week {current_week}")
            return
            
        message = f"*🏀 Week {current_period.get('period')} Matchups*\n\n"
        
        for matchup in current_period.get("matchupList", []):
            away_team = matchup.get("away", {})
            home_team = matchup.get("home", {})
            
            if away_team and home_team:
                message += f"• {away_team.get('name')} @ {home_team.get('name')}\n"
        
        message += "\n_Good luck! Trust The Process 🏀_"
        
        # Send to all configured chat IDs
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id.strip(),
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f"Weekly update sent to chat {chat_id}")
            except Exception as e:
                print(f"Error sending to chat {chat_id}: {str(e)}")
                
    except Exception as e:
        print(f"Error in weekly_update: {str(e)}")


# Test Command
async def test_command(update, context):
    """Test the Fantrax API connection"""
    api = FantraxAPI(os.getenv("FANTRAX_LEAGUE_ID"))
    
    try:
        working = await api.test_connection()
        if working:
            await update.message.reply_text("✅ Fantrax API connection working!")
        else:
            await update.message.reply_text("❌ Fantrax API connection failed!")
    except Exception as e:
        await update.message.reply_text(f"Error testing API: {str(e)}")

def main():
    """Start the bot."""
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))

    # From Fantrax
    application.add_handler(CommandHandler("matchups", matchups_command))
    application.add_handler(CommandHandler("team", team_command))
    application.add_handler(CommandHandler("player", player_command))

    # Fantrax Teams
    application.add_handler(CommandHandler("teams", teams_command))
    application.add_handler(CommandHandler("rosterrules", roster_rules_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("teaminfo", team_detail_command))
    application.add_handler(CommandHandler("matchups", matchups_command))
    application.add_handler(CommandHandler("saveresponse", save_response_command))
    application.add_handler(CommandHandler("standings", standings_command))
    application.add_handler(CommandHandler("roster", roster_command))

    # test command
    application.add_handler(CommandHandler("test", test_command))

    # Weekly updates disabled
    # job_queue = application.job_queue
    #
    # # Standings at 9 AM ET (13:00 UTC)
    # job_queue.run_daily(
    #     scheduled_standings,
    #     time=time(13, 0),  # 9:00 AM ET
    #     days=(1,)  # Monday (in v20.8 cron-style scheme where 1=Monday)
    # )
    #
    # # Matchups at 9 AM ET (13:00 UTC)
    # job_queue.run_daily(
    #     scheduled_matchups,
    #     time=time(13, 0),  # 9:00 AM ET
    #     days=(1,)  # Monday
    # )
    
    # Draft announcements from the MNS league digest
    if MNS_DIGEST_URL and HINKIE_BOT_KEY:
        application.job_queue.run_repeating(draft_watch, interval=60, first=10)
    else:
        logger.info("MNS_DIGEST_URL / HINKIE_BOT_KEY not set; draft watch off")

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