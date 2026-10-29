from datetime import datetime, timezone
import aiohttp
import asyncio
import pandas as pd
import json


async def fetch_achievement_stats(session, app_id):

    url = (
        "https://api.steampowered.com/"
        f"ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/?gameid={app_id}"
    )

    try:
        async with session.get(url) as resp:

            if resp.status == 200:

                data = await resp.json()

                return {
                    "app_id": app_id,
                    "raw_json": json.dumps(data),
                    "load_timestamp": datetime.now(timezone.utc)
                }

            print(f"Failed {app_id}: {resp.status}")
            return None

    except Exception as e:

        print(f"Error {app_id}: {e}")
        return None


async def fetch_achievement_stats_async(app_ids):

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_achievement_stats(session, app_id)
            for app_id in app_ids
        ]

        results = await asyncio.gather(*tasks)

    return pd.DataFrame(
        [r for r in results if r is not None]
    )


def fetch_steam_achievement_stats_async(app_ids):

    return asyncio.run(
        fetch_achievement_stats_async(app_ids)
    )