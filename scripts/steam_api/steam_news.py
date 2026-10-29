from datetime import datetime, timezone
import aiohttp
import asyncio
import pandas as pd
import json


async def fetch_game_news(session, app_id):

    url = (
        "https://api.steampowered.com/"
        f"ISteamNews/GetNewsForApp/v2/?appid={app_id}&count=20"
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


async def fetch_game_news_async(app_ids):

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_game_news(session, app_id)
            for app_id in app_ids
        ]

        results = await asyncio.gather(*tasks)

    return pd.DataFrame(
        [r for r in results if r is not None]
    )


def fetch_steam_news_async(app_ids):

    return asyncio.run(
        fetch_game_news_async(app_ids)
    )