import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

class FantraxAPI:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.base_url = "https://www.fantrax.com/fxea/general"  # Make sure this matches
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": (
                "JSESSIONID=node019nai7p8vp87h1ui707m1unieq317498.node0; "
                "FX_RM=_qpxzAxxSBx1eABMOAQMGXgNJUgZUV1oRClgIB0cHCwJRWgI=; "
                "uuid=8336809E-6D6B-43AA-9E78-F5765AC67D72"
            ),
            "Origin": "https://www.fantrax.com",
            "Referer": f"https://www.fantrax.com/fantasy/league/{league_id}/home",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.session = None
        
    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make a POST request to the Fantrax API"""
        url = f"{self.base_url}/{endpoint}?leagueId={self.league_id}"  # Add leagueId as query param
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                print(f"\nMaking request to {url}")
                print(f"Headers: {self.headers}")
                print(f"Data: {data}")
                
                async with session.post(url, json=data) as response:
                    text = await response.text()
                    print(f"Response text: {text}")  # Show full response
                    return json.loads(text)
                    
        except Exception as e:
            print(f"Request error: {str(e)}")
            return {"error": str(e)}


    async def get_league_info(self) -> Dict:
        """Get league information"""
        return await self._make_request("getLeagueInfo", {
            "leagueId": self.league_id,
            "sport": "NBA"
        })
    

    async def get_player_info(self, player_name: str) -> Dict:
        try:
            # Get ADP data
            result = await self._make_request("getAdp", {
                "sport": "NBA"
            })
            
            # Get rosters to check team ownership
            rosters = await self.get_team_rosters()
            
            # Try both name formats
            search_name = player_name.lower()
            name_parts = search_name.split()
            
            if ',' not in search_name and len(name_parts) > 1:
                reversed_name = f"{name_parts[-1]}, {' '.join(name_parts[:-1])}"
            else:
                reversed_name = search_name
                
            for player in result:
                player_name_lower = player['name'].lower()
                if search_name in player_name_lower or reversed_name in player_name_lower:
                    safe_name = player['name'].replace("*", "\\*").replace("_", "\\_")
                    player_id = player['id']
                    
                    # Find fantasy team ownership and salary
                    fantasy_team = "FA"
                    salary = 0
                    if "rosters" in rosters:
                        for team_id, team_data in rosters["rosters"].items():
                            for roster_player in team_data.get("rosterItems", []):
                                if roster_player.get("id") == player_id:
                                    fantasy_team = team_data.get("teamName", "FA")
                                    salary = roster_player.get("salary", 0)
                                    break
                            if fantasy_team != "FA":
                                break
                    
                    # Format salary with commas
                    salary_str = f"${salary:,.0f}" if salary > 0 else "N/A"
                    
                    # Print debug info to console
                    print(f"Found player: {player['name']}")
                    print(f"Player ID: {player_id}")
                    print(f"Fantasy Team: {fantasy_team}")
                    print(f"Salary: {salary_str}")
                    print(f"Full player data: {player}")
                    
                    return {
                        "name": safe_name,
                        "positions": [player['pos']],
                        "team": fantasy_team,
                        "salary": salary_str,
                        "status": "Active",
                        "debug_info": f"ID: {player_id}"
                    }
                    
            return {
                "name": player_name,
                "positions": [],
                "team": "FA",
                "salary": "N/A",
                "status": "Player not found"
            }
                    
        except Exception as e:
            print(f"Error getting player info: {str(e)}")
            return {
                "name": player_name,
                "positions": [],
                "team": "FA",
                "salary": "N/A",
                "status": str(e)
            }
        
    async def get_teams(self) -> Dict:
        """Get all unique teams from league data"""
        try:
            league_info = await self._make_request("getLeagueInfo", {
                "leagueId": self.league_id,
                "sport": "NBA"
            })
            
            # Extract teams from matchups to ensure we get all teams
            teams = {}
            if "matchups" in league_info and league_info["matchups"]:
                first_period = league_info["matchups"][0]
                for matchup in first_period.get("matchupList", []):
                    # Add home team
                    if "home" in matchup:
                        team = matchup["home"]
                        teams[team["id"]] = {
                            "name": team["name"],
                            "shortName": team.get("shortName", ""),
                            "id": team["id"]
                        }
                    # Add away team
                    if "away" in matchup:
                        team = matchup["away"]
                        teams[team["id"]] = {
                            "name": team["name"],
                            "shortName": team.get("shortName", ""),
                            "id": team["id"]
                        }
            
            return teams
                
        except Exception as e:
            print(f"Error getting team info: {type(e).__name__}")
            return {"error": "Could not retrieve team data"}

    async def get_roster_constraints(self) -> Dict:
        """Get roster constraints for the league"""
        try:
            league_info = await self._make_request("getLeagueInfo", {
                "leagueId": self.league_id,
                "sport": "NBA"
            })
            
            if "rosterInfo" in league_info:
                return {
                    "positions": league_info["rosterInfo"]["positionConstraints"],
                    "maxPlayers": league_info["rosterInfo"]["maxTotalPlayers"],
                    "maxActive": league_info["rosterInfo"]["maxTotalActivePlayers"],
                    "maxReserve": league_info["rosterInfo"]["maxTotalReservePlayers"]
                }
                
            return {"error": "No roster information found"}
                
        except Exception as e:
            print(f"Error getting roster info: {type(e).__name__}")
            return {"error": "Could not retrieve roster data"}
        
    async def save_api_response(self):
        """Save the full API response to a file for analysis"""
        try:
            league_info = await self._make_request("getLeagueInfo", {
                "leagueId": self.league_id,
                "sport": "NBA"
            })
            
            # Save to a JSON file with nice formatting
            with open('api_response.json', 'w') as f:
                json.dump(league_info, f, indent=2)
                
            return "API response saved to api_response.json"
                
        except Exception as e:
            return f"Error saving API response: {str(e)}"


    async def get_standings(self) -> Dict:
        """Get current league standings"""
        try:
            response = await self._make_request("getStandings", {
                "sport": "NBA"
            })
            
            if "error" in response:
                return {"error": response["error"]}
                
            print("Standings response:", response)  # Let's see what data we get back
            return response
                
        except Exception as e:
            print(f"Error getting standings: {type(e).__name__}")
            return {"error": "Could not retrieve standings"}
        


    async def get_team_roster(self, team_id: str) -> Dict:
        """Get roster for specific team"""
        try:
            league_info = await self.get_league_info()
            
            # Get team info
            teams = league_info.get("teamInfo", {})
            team = teams.get(team_id)
            
            if not team:
                return {"error": "Team not found"}
                
            # TODO: Extract roster info once we find where it is in the API response
            roster = []
                
            return {
                "team": team,
                "roster": roster
            }
                
        except Exception as e:
            print(f"Error getting roster: {type(e).__name__}")
            return {"error": "Could not retrieve roster"}
    
    async def get_team_rosters(self, period: int = None) -> Dict:
        """Get all team rosters"""
        try:
            data = {"sport": "NBA"}
            if period:
                data["period"] = period
                
            response = await self._make_request("getTeamRosters", data)
            
            print("\nRoster response:", response)  # Debug print to see response structure
            return response
                
        except Exception as e:
            print(f"Error getting rosters: {type(e).__name__}")
            return {"error": "Could not retrieve rosters"}
    

    async def get_player_names(self) -> Dict:
        """Get mapping of player IDs to names"""
        try:
            response = await self._make_request("getPlayerIds", {
                "sport": "NBA"
            })
            print("Player names response:", response)  # Debug print to see response structure
            return response
        except Exception as e:
            print(f"Error getting player names: {str(e)}")
            return {"error": "Could not retrieve player names"}



    async def test_connection(self) -> bool:
        """Test the connection to Fantrax API"""
        try:
            result = await self.get_league_info()
            print("Test connection result:", result)
            return "error" not in result
        except Exception as e:
            print(f"Test connection failed: {str(e)}")
            return False

    def get_current_matchups(self, league_info: Dict) -> List[Dict]:
        """Extract current week's matchups from league info"""
        current_period = None
        today = datetime.now()
        
        # Find current period from matchups list
        matchups = league_info.get("matchups", [])
        if matchups:
            # For now, just get the first period's matchups
            # We'll need to add logic to determine the current period
            current_period = matchups[0]
        
        if current_period:
            return current_period.get("matchupList", [])
        return []

    def format_matchup_message(self, matchups: List[Dict]) -> str:
        """Format matchups into a readable message"""
        message = "*Weekly Matchups*\n\n"
        for matchup in matchups:
            home = matchup.get("home", {}).get("name", "Unknown")
            away = matchup.get("away", {}).get("name", "Unknown")
            message += f"{away} @ {home}\n"
        return message

    async def format_team_info(self, team_name: str) -> str:
        """Get formatted team information"""
        rosters = await self.get_team_rosters()
        standings = await self.get_standings()
        league_info = await self.get_league_info()
        
        # Find team in league info
        team_id = None
        team_data = None
        for id, team in league_info.get("teamInfo", {}).items():
            if team.get("name", "").lower() == team_name.lower():
                team_id = id
                team_data = team
                break
        
        if not team_data:
            return f"Team '{team_name}' not found"
        
        # Format response
        message = (
            f"*{team_data.get('name')}*\n\n"
            f"• Short Name: {team_data.get('shortName', 'N/A')}\n"
            # Add more team details as we find them in the API response
        )
        
        return message

    async def send_weekly_update(self, chat_id: str, bot) -> None:
        """Send weekly matchup updates to the specified chat"""
        try:
            league_info = await self.get_league_info()
            matchups = self.get_current_matchups(league_info)
            message = self.format_matchup_message(matchups)
            
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="MARKDOWN"
            )
        except Exception as e:
            print(f"Error sending weekly update: {str(e)}")

    def find_current_period(self, league_info: Dict) -> Optional[int]:
        """Find the current matchup period"""
        # Will implement logic to determine current period
        # based on date ranges or other available data
        return 1  # Placeholder