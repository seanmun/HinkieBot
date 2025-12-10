"""
Test script to manually trigger all three scheduled messages
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# Add bot directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from fantrax_api import FantraxAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID").split(',')[0].strip()
LEAGUE_ID = os.getenv("FANTRAX_LEAGUE_ID")

def get_current_week():
    """Calculate the current week number based on season start date"""
    season_start = datetime(2024, 10, 28)  # Oct 28, 2024
    current_date = datetime.now()
    days_elapsed = (current_date - season_start).days
    current_week = (days_elapsed // 7) + 1
    return current_week

async def test_weekly_update():
    """Test the weekly_update message"""
    print("\n=== Testing Weekly Update Message ===")
    bot = Bot(token=BOT_TOKEN)
    api = FantraxAPI(LEAGUE_ID)

    try:
        league_info = await api.get_league_info()

        # Find current period
        today = datetime.now()
        current_period = None
        for period in league_info.get("matchups", []):
            start_date = period.get("startDate")
            end_date = period.get("endDate")

            if start_date and end_date:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

                if start <= today <= end:
                    current_period = period
                    break

        if not current_period:
            print("No current period found for weekly update")
            return

        message = f"*🏀 Week {current_period.get('period')} Matchups*\n\n"

        for matchup in current_period.get("matchupList", []):
            away_team = matchup.get("away", {})
            home_team = matchup.get("home", {})

            if away_team and home_team:
                message += f"• {away_team.get('name')} @ {home_team.get('name')}\n"

        message += "\n_Good luck! Trust The Process 🏀_"

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        print(f"✓ Weekly update sent to chat {CHAT_ID}")
        print(f"Message:\n{message}")

    except Exception as e:
        print(f"✗ Error sending weekly update: {str(e)}")

async def test_scheduled_standings():
    """Test the scheduled_standings message"""
    print("\n=== Testing Scheduled Standings Message ===")
    bot = Bot(token=BOT_TOKEN)
    api = FantraxAPI(LEAGUE_ID)

    try:
        standings_data = await api.get_standings()

        if not standings_data:
            print("Could not fetch standings data")
            return

        message = "*📊 Current Standings*\n\n"

        for i, team in enumerate(standings_data, 1):
            name = team.get('name', 'Unknown')
            wins = team.get('wins', 0)
            losses = team.get('losses', 0)
            ties = team.get('ties', 0)

            if ties > 0:
                record = f"{wins}-{losses}-{ties}"
            else:
                record = f"{wins}-{losses}"

            message += f"{i}. {name}: {record}\n"

        message += "\n_Trust The Process 🏀_"

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        print(f"✓ Standings sent to chat {CHAT_ID}")
        print(f"Message:\n{message}")

    except Exception as e:
        print(f"✗ Error sending standings: {str(e)}")

async def test_scheduled_matchups():
    """Test the scheduled_matchups message"""
    print("\n=== Testing Scheduled Matchups Message ===")
    bot = Bot(token=BOT_TOKEN)
    api = FantraxAPI(LEAGUE_ID)

    try:
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

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        print(f"✓ Matchups sent to chat {chat_id}")
        print(f"Message:\n{message}")

    except Exception as e:
        print(f"✗ Error sending matchups: {str(e)}")

async def main():
    """Run all three test messages"""
    print("="*50)
    print("Testing All Three Scheduled Messages")
    print(f"Chat ID: {CHAT_ID}")
    print("="*50)

    await test_weekly_update()
    await asyncio.sleep(2)  # Wait 2 seconds between messages

    await test_scheduled_standings()
    await asyncio.sleep(2)

    await test_scheduled_matchups()

    print("\n" + "="*50)
    print("All tests complete! Check your Telegram chat.")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
