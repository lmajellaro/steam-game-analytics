from scripts.settings import DB_PATH
import requests
import duckdb

#############################################
# Retrieve top Steam game AppIDs (SteamSpy) #
#############################################
#############################################
# Retrieve Steam game AppIDs (API + DB)     #
#############################################
def get_unique_steamspy_app_ids():
    """
    Retrieves a unified list of AppIDs by combining:
    1. Top games from SteamSpy (recent + all-time)
    2. Existing AppIDs already stored in the game_info table

    This ensures that previously ingested games are not lost
    even if they are no longer returned by the API.

    Returns:
    - list: Unique AppIDs from API and database
    """
    urls = {
        "top2weeks": "https://steamspy.com/api.php?request=top100in2weeks",
        "topforever": "https://steamspy.com/api.php?request=top100forever"
    }
    
    all_app_ids = set()

    # Step 1: Fetch from SteamSpy
    for key, url in urls.items():
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            all_app_ids.update(map(int, data.keys()))  # ensure integers
        else:
            print(f"Error fetching {key}: {resp.status_code}")

    # Step 2: Fetch existing AppIDs from DuckDB
    try:
        conn = duckdb.connect(DB_PATH)
        existing_ids = conn.execute("""
            SELECT DISTINCT appid 
            FROM game_info
        """).fetchall()

        # Flatten list of tuples → list of ints
        existing_ids = [row[0] for row in existing_ids]

        conn.close()

        all_app_ids.update(existing_ids)

    except Exception as e:
        print(f"Warning: could not fetch existing app_ids from DB: {e}")

    return list(all_app_ids)
