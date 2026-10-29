
from datetime import datetime, timezone
import aiohttp
import asyncio
import pandas as pd
import json


STEAM_REVIEWS_URL = (
    "https://api.steampowered.com/"
    "IUserReviewsService/GetAppReviews/v1/"
)


async def fetch_reviews(session, app_id):

    # New API uses numeric enum values:
    # filter=1: Recent
    # purchase_type=1: All purchase types
    params = {
        "input_json": json.dumps({
            "appid": int(app_id),
            "filter": 1,
            "languages": ["all"],
            "purchase_type": 1,
            "num_per_page": 100,
            "cursor": "*",
        })
    }

    try:
        async with session.get(
            STEAM_REVIEWS_URL,
            params=params,
        ) as resp:

            resp.raise_for_status()
            data = await resp.json()

            # New API wraps its result in "response".
            response_data = data.get("response")

            if response_data is None:
                print(f"Missing response payload for {app_id}")
                return None

            return {
                "app_id": app_id,
                "raw_json": json.dumps(response_data),
                "load_timestamp": datetime.now(timezone.utc),
            }

    except Exception as e:
        print(f"Error {app_id}: {type(e).__name__}: {e!r}")
        return None


async def fetch_reviews_async(app_ids):

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        results = []

        # Sequential requests reduce the risk of rate limiting.
        for app_id in app_ids:
            result = await fetch_reviews(session, app_id)

            if result is not None:
                results.append(result)

            await asyncio.sleep(1)

    return pd.DataFrame(
        results,
        columns=["app_id", "raw_json", "load_timestamp"],
    )


def fetch_steam_reviews_async(app_ids):

    return asyncio.run(
        fetch_reviews_async(app_ids)
    )
