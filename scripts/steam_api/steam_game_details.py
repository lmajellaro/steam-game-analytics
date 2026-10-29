from datetime import datetime, timezone
import aiohttp
import json
import asyncio
import pandas as pd

#############################################################
# Fetch game details from Steam API (single async request) #
###########################################################
async def fetch_game_details(session, app_id):
    """
    Asynchronously retrieves detailed metadata for a single Steam game
    using the Steam Store API.

    Parameters:
    - session (aiohttp.ClientSession): Active HTTP session
    - app_id (int): Steam application ID

    Returns:
    - dict: Contains app_id, raw JSON response, and load timestamp
    """
    base_url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": app_id, "cc": "US", "l": "en"}
    try:
        async with session.get(base_url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "app_id": app_id,
                    "raw_json": json.dumps(data.get(str(app_id), {})),
                    "load_timestamp": datetime.now(timezone.utc)
                }
            else:
                print(f"Failed {app_id}: {resp.status}")
                return None
    except Exception as e:
        print(f"Error {app_id}: {e}")
        return None


############################################################
# Fetch multiple game details asynchronously (batch mode) #
##########################################################
async def fetch_game_details_async(app_ids):
    """
    Executes asynchronous requests to retrieve metadata for multiple Steam games.

    Parameters:
    - app_ids (list): List of Steam AppIDs

    Returns:
    - DataFrame: Contains raw API responses and metadata for each game
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_game_details(session, app_id) for app_id in app_ids]
        results = await asyncio.gather(*tasks)
    return pd.DataFrame([r for r in results if r is not None])


###############################################################
# Wrapper to execute async Steam API fetch in sync context   #
#############################################################
def fetch_steam_game_details_async(app_ids):
    """
    Synchronous wrapper to execute asynchronous retrieval of Steam game details.

    Parameters:
    - app_ids (list): List of Steam AppIDs

    Returns:
    - DataFrame: Resulting dataset from async API calls
    """
    return asyncio.run(fetch_game_details_async(app_ids))
