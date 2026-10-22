import os
from dotenv import load_dotenv
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from datetime import datetime, time, timedelta
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
    "- Your live league data comes from your lookup tools in the league chat (league_summary, "
    "team_roster, draft_board), or from an MNS league data block when the message has one. Look "
    "things up whenever a question needs records, rosters, cap or the draft; skip the tools for "
    "plain banter. The data comes from the "
    "league's app and OVERRIDES the older rules text below wherever they disagree (cap numbers, "
    "fees, roster sizes). You have no box scores or player news. Never invent numbers, picks "
    "or results. If something isn't in the data, say so and pivot to process.\n"
    "- Tie a chat member to a team only through the owner handles and Telegram usernames in "
    "the data. Never guess who owns a team.\n"
    "- Only state league rules that appear in the rules below. If unsure, point them to the slash commands (/rules, /cap, /keeper, /dues, /prize, /draft).\n\n"
    "League rules and info:\n\n"
    + "\n\n".join(LEAGUE_INFO.values()).replace("*", "")
)


# Prompt caching (Oct 21 2026). The prefix must match byte for byte to
# be reused, so the request is ordered steadiest first: the persona and
# rules (never change), then the league data (changes only when the
# digest does), then the chat transcript (new every message, never
# cached). The old single top-level cache_control put the breakpoint
# after the transcript, so nothing ever matched and the whole league
# block was re-sent at full price on every reply.
CACHE_1H = {"type": "ephemeral", "ttl": "1h"}
HINKIE_SYSTEM_BLOCKS = [{"type": "text", "text": HINKIE_SYSTEM, "cache_control": CACHE_1H}]


def league_block(league):
    """The league data as its own cached block, or nothing without data."""
    return [{"type": "text", "text": league, "cache_control": CACHE_1H}] if league else []


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


# Hinkie's lookups (Oct 21 2026): instead of the whole league riding on
# every reply, he asks for what a question needs. Banter costs only the
# cached persona; a cap question pulls one summary, a roster question
# one team.
HINKIE_TOOLS = [
    {"name": "league_summary",
     "description": "League settings (cap rules, fees, roster sizes, prize pot) and every team's owners and Telegram usernames, record, payroll and cap status. Use for standings, who owns which team, and cap or rules questions.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "team_roster",
     "description": "One team's full roster (each player's position, NBA team, salary and Cat Score, and slot) plus the team's category ranks. Use for any question about a specific team or its players.",
     "input_schema": {"type": "object", "properties": {"team": {"type": "string", "description": "Team name, owner name, or @username"}}, "required": ["team"]}},
    {"name": "draft_board",
     "description": "The draft: status, picks made and left, who is on the clock and their deadline, who is next, the most recent picks.",
     "input_schema": {"type": "object", "properties": {}}},
]


def run_tool(parts, name, args):
    """One lookup against the league sections, as plain text."""
    if name == "league_summary":
        return "\n".join(parts["header"] + [t["short"] for t in parts["teams"]])
    if name == "team_roster":
        q = str(args.get("team", "")).lower().lstrip("@").strip()
        hits = [t for t in parts["teams"] if q and (q in t["name"].lower() or q in t["owners"].lower())]
        if not hits:
            return "No team matches that. Teams: " + ", ".join(t["name"] for t in parts["teams"])
        return "\n".join(t["full"] for t in hits[:2])
    if name == "draft_board":
        return "\n".join(parts["draft"]) or "No draft is running."
    return "Unknown lookup."


async def hinkie_reply(chat_id):
    """Claude's reply in Hinkie's voice, or a random quote if anything fails."""
    fallback = f"{random.choice(HINKIE_QUOTES)} - Sam Hinkie"
    if not under_daily_cap(chat_id):
        return fallback
    transcript = "\n".join(chat_history.get(chat_id, []))
    try:
        parts = await league_parts(chat_id)
    except Exception as e:
        logger.error(f"League context failed: {e}")
        parts = None
    messages = [{"role": "user", "content": f"Recent group chat (oldest first):\n\n{transcript}\n\nWrite Sam Hinkie's reply."}]
    try:
        for _ in range(4):
            response = await claude.messages.create(
                model=HINKIE_MODEL,
                max_tokens=2000,
                output_config={"effort": "low"},
                system=HINKIE_SYSTEM_BLOCKS,
                messages=messages,
                **({"tools": HINKIE_TOOLS} if parts else {}),
            )
            if response.stop_reason == "refusal":
                return fallback
            if response.stop_reason != "tool_use":
                break
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(parts, b.name, b.input or {})}
                for b in response.content if b.type == "tool_use"
            ]})
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


def money(n):
    return f"${(n or 0) / 1_000_000:.1f}M"


async def league_parts(chat_id):
    """The league in sections — header (settings), each team, the draft — or
    None outside the league chat or without data."""
    if chat_id != LEAGUE_CHAT_ID:
        return None
    d = await fetch_digest(max_age=300)
    if not d:
        return None
    lg = d["league"]
    lines = [f"MNS league data — {lg['name']} {lg['seasonYear']}, phase: {lg.get('phase')}"
             + (f", week {lg['week']} (ends {lg['weekEnds']})" if lg.get("week") else "")]

    st = d.get("settings") or {}
    cap = st.get("cap")
    fees = st.get("fees")
    if cap:
        first_fee = f"${fees['firstApronFee']}" if fees else "a one-time fee"
        lines.append(
            f"How the MNS cap works (the app's rules): cap {money(cap['base'])}. Going over the "
            f"first apron ({money(cap['firstApron'])}) is ALLOWED and normal: the team pays "
            f"{first_fee} once into the prize pool and can then stay over all season. Over the "
            f"second apron ({money(cap['secondApron'])}) the team pays ${cap['penaltyRatePerM']} per "
            f"$1M over (rounded up) into the pot, charged at its season peak and never refunded. "
            f"The hard cap ({money(cap['hardCap'])}) is the only true ceiling: adds and trades that "
            f"would end above it are blocked, and a team above it must get under. Fees book at the "
            f"season's first tip-off, not during the draft. Teams can also trade cap space. Being "
            f"over an apron is a legitimate strategy that feeds the pot, not a mistake: never "
            f"shame it. If anything, thank them for their generosity to the prize pool."
        )
    if fees:
        lines.append(f"Fees: buy-in ${fees['buyIn']}, first apron ${fees['firstApronFee']}, "
                     f"franchise tag ${fees['franchiseTagFee']}, redshirt ${fees['redshirtFee']}, "
                     f"redshirt activation ${fees['activationFee']}")
    ro = st.get("roster")
    if ro:
        lines.append(f"Roster: {ro['starterSize']} starters, {ro['activeSize']} active, {ro['irSlots']} IR, "
                     f"up to {ro['maxKeepers']} keepers; categories: {', '.join(st.get('categories') or [])}; "
                     f"{st.get('seasonWeeks')} weeks")
    pot = st.get("prizePool")
    if pot:
        lines.append(f"Prize pot: ${pot['potUsd']}" + "".join(f", {x['label']} {x['share']}%" for x in pot.get("splits") or []))

    tag = {"active": "", "bench": " [bench]", "ir": " [IR]", "redshirt": " [redshirt]"}

    def cap_status(salary):
        """Where a payroll sits, decided here so the model never does the math."""
        if not cap:
            return ""
        if salary > cap["hardCap"]:
            return f"OVER THE HARD CAP by {money(salary - cap['hardCap'])}, must get under"
        if salary > cap["secondApron"]:
            over_m = -(-(salary - cap["secondApron"]) // 1_000_000)  # ceil
            return f"over the second apron by {money(salary - cap['secondApron'])} (${over_m * cap['penaltyRatePerM']} to the pot)"
        if salary > cap["firstApron"]:
            return f"over the first apron only (one-time fee), {money(cap['secondApron'] - salary)} below the second apron"
        return f"under the first apron, {money(cap['firstApron'] - salary)} of room"
    lines.append("Teams (record | cap used | team Cat Score and category ranks from its best "
                 "10 players | roster by salary with each player's Cat Score). Stats are this "
                 "regular season once it starts, last season before that.")
    teams = []
    for t in d.get("teams") or []:
        who = ", ".join(t["owners"]) + (f" @{t['telegramUsername']}" if t.get("telegramUsername") else "")
        titles = f", titles {t['banners']}" if t.get("banners") else ""
        delta = f" (cap trade {money(t['capTradeDelta'])})" if t.get("capTradeDelta") else ""
        def pl(p):
            cat = f" cat {p['stats']['cat']}" if p.get("stats") and p["stats"].get("cat") is not None else " (no NBA stats)"
            return (f"{p['name']} {p.get('position') or ''} {p.get('teamCode') or ''} {money(p['salary'])}{cat}"
                    f"{tag.get(p['slot'], ' [' + p['slot'] + ']')}")
        roster = "; ".join(pl(p) for p in t["roster"])
        ranks = " ".join(f"{c} {r}" for c, r in (t.get("categoryRanks") or {}).items())
        short = (f"- {t['name']} ({who}{titles}): {t['wins']}-{t['losses']}-{t['ties']} | "
                 f"{money(t['salary'])}{delta}, {cap_status(t['salary'])} | team Cat Score {t.get('catScore')}")
        teams.append({"name": t["name"], "owners": who, "short": short,
                      "full": f"{short} | category ranks of 12 (1 = best): {ranks} | {roster}"})

    header = lines
    lines = []
    draft = d.get("draft")
    if draft and draft["status"] in ("active", "paused", "setup"):
        lines.append(f"Draft: {draft['status']}, {draft['picksMade']} picks made, {draft['picksLeft']} left")
        cur = draft.get("current")
        if cur:
            lines.append(f"On the clock: {cur['teamName']} ({pick_label(cur)}), deadline {deadline_label(cur['deadline'])}")
        if draft.get("nextUp"):
            lines.append("Then: " + ", ".join(n["teamName"] for n in draft["nextUp"]))
        recent = [p for p in draft["picks"] if not p["keeper"]][-8:]
        if recent:
            lines.append("Recent picks: " + "; ".join(f"{pick_label(p)} {p['teamName']} took {player_label(p)}" for p in recent))
    return {"header": header, "teams": teams, "draft": lines}


async def league_context(chat_id):
    """The whole league as text (the roster report card grades every team)."""
    parts = await league_parts(chat_id)
    if not parts:
        return ""
    return "\n".join(parts["header"] + [t["full"] for t in parts["teams"]] + parts["draft"]) + "\n\n"


async def pick_quip(picks):
    """One Hinkie line on the new pick(s); empty if Claude is unavailable."""
    desc = "; ".join(f"{p['teamName']} took {player_label(p)}" + (" (autodraft)" if p["auto"] else "") for p in picks)
    try:
        response = await claude.messages.create(
            model=HINKIE_MODEL,
            max_tokens=1000,
            output_config={"effort": "low"},
            system=HINKIE_SYSTEM_BLOCKS,
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
            text="The draft is complete. Every pick is a seed. Time for report cards. 📝",
        )
        digest_cache["at"] = None  # grade the final rosters, not the cached ones
        await post_report(context.bot, LEAGUE_CHAT_ID)
    last_draft_status = draft["status"]


GRADES_COOLDOWN = 600  # seconds between /grades runs per chat
last_grades = {}


def split_message(text, limit=4000):
    """Telegram caps a message at 4096 characters: split on line breaks."""
    parts, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > limit and cur:
            parts.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        parts.append(cur)
    return parts


async def roster_report():
    """Hinkie's graded overview of every roster, or None without data."""
    league = await league_context(LEAGUE_CHAT_ID)
    if not league:
        return None
    response = await claude.messages.create(
        model=HINKIE_MODEL,
        max_tokens=16000,
        output_config={"effort": "medium"},
        system=HINKIE_SYSTEM_BLOCKS,
        messages=[{"role": "user", "content": league_block(league) + [{"type": "text", "text": (
            "Write Sam Hinkie's roster report card for every team in the league. This is a long "
            "post, so ignore the 1-3 sentence limit. For each team, best grade to worst: the team "
            "name and a letter grade (A+ to F) on the first line, then two or three short lines on "
            "category strengths and holes (use the ranks), the cap position under the MNS cap rules, "
            "(state each team's cap status exactly as given in the data), and anything notable (stars, rookies with no NBA stats yet as unknowns). Grade mostly "
            "on category ranks and team Cat Score; cap room is a bonus, being over an apron is "
            "never a penalty. Say once at the top whether the stats are last season's. Plain text, "
            "no markdown, a few emoji are fine. End with one line of Hinkie wisdom. Keep it under "
            "3,500 characters."
        )}]}],
    )
    if response.stop_reason == "refusal":
        return None
    return "".join(b.text for b in response.content if b.type == "text").strip() or None


async def post_report(bot, chat_id):
    try:
        report = await roster_report()
    except Exception as e:
        logger.error(f"Roster report failed: {e}")
        report = None
    if not report:
        await bot.send_message(chat_id=chat_id, text="The data's not in front of me right now. Patience. Ask again shortly.")
        return
    remember(chat_id, "Sam Hinkie", report)
    for part in split_message(report):
        await bot.send_message(chat_id=chat_id, text=part)


async def grades_command(update, context):
    """/grades — the roster report card, in the league chat only."""
    chat_id = update.effective_chat.id
    if chat_id != LEAGUE_CHAT_ID:
        await update.message.reply_text("Report cards are for the league chat only. Trust the Process.")
        return
    now = datetime.now()
    if chat_id in last_grades and (now - last_grades[chat_id]).total_seconds() < GRADES_COOLDOWN:
        await update.message.reply_text("I just graded everyone. The process needs time to work. Try again in a few minutes.")
        return
    last_grades[chat_id] = now
    await update.message.reply_text("Grading every roster. One moment. 📝")
    await post_report(context.bot, chat_id)


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
        '/grades - Hinkie grades every roster'
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
    application.add_handler(CommandHandler("grades", grades_command))

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