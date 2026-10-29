from datetime import datetime, timezone
import aiohttp
import json
import asyncio
import pandas as pd

################################################################
# Fetch current player count (single async API request)       #
##############################################################
async def fetch_steam_current_players(session, app_id):
    """
    Asynchronously retrieves the current number of players for a given game
    using the official Steam Web API.

    Parameters:
    - session (aiohttp.ClientSession): Active HTTP session
    - app_id (int): Steam application ID

    Returns:
    - dict: Contains app_id, current player count, and load timestamp
    """
    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app_id}"

    try:
        async with session.get(url) as resp:
            data = await resp.json()
            return {
                "app_id": app_id,
                "player_count": data.get("response", {}).get("player_count"),
                "load_timestamp": datetime.now(timezone.utc)
            }
    except:
        return {
            "app_id": app_id,
            "player_count": None,
            "load_timestamp": datetime.now(timezone.utc)
        }


################################################################
# Fetch current players for multiple games (async batch)      #
##############################################################
async def fetch_all_current_players(app_ids):
    """
    Executes asynchronous requests to retrieve current player counts
    for multiple Steam games.

    Parameters:
    - app_ids (list): List of Steam AppIDs

    Returns:
    - DataFrame: Contains player counts and timestamps for each game
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_steam_current_players(session, app_id) for app_id in app_ids]
        results = await asyncio.gather(*tasks)
    return pd.DataFrame(results)


###############################################################
# Wrapper to execute async Steam API fetch in sync context   #
#############################################################
def fetch_steam_current_players_data_asynch(app_ids):
    return asyncio.run(fetch_all_current_players(app_ids))
