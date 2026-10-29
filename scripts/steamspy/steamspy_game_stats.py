from datetime import datetime, timezone
import aiohttp
import json
import asyncio
import pandas as pd

###############################################################
# Fetch SteamSpy stats for a single game (async request)      #
###############################################################
async def fetch_steamspy_game_stats(session, app_id):
    """
    Retrieves gameplay statistics from SteamSpy for a single game.

    Parameters:
    - session (aiohttp.ClientSession): Active HTTP session
    - app_id (int): Steam application ID

    Returns:
    - dict: AppID, raw JSON payload and timestamp
    """

    url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"

    try:
        async with session.get(url) as resp:

            if resp.status == 200:
                data = await resp.json()
                return {
                    "appid": app_id,
                    "raw_json": json.dumps(data),
                    "load_timestamp": datetime.now(timezone.utc)
                }

            else:
                print(f"SteamSpy failed for {app_id}: {resp.status}")

                return None

    except Exception as e:

        print(f"SteamSpy error for {app_id}: {e}")

        return None

###############################################################
# Fetch SteamSpy stats for multiple games asynchronously      #
###############################################################
async def fetch_all_steamspy_game_stats(app_ids):

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_steamspy_game_stats(session, app_id)
            for app_id in app_ids
        ]

        results = await asyncio.gather(*tasks)

    return pd.DataFrame(
        [r for r in results if r is not None]
    )

###############################################################
# Wrapper for SteamSpy async extraction                       #
###############################################################
def fetch_steamspy_game_stats_async(app_ids):

    return asyncio.run(
        fetch_all_steamspy_game_stats(app_ids)
    )