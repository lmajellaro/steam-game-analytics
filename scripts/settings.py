from pathlib import Path

# ======== Paths ========

DB_PATH = "/opt/airflow/duckdb/steam_games.duckdb"

# Streamlit database selection:
# Use the live database for local development with your live database:
# STREAMLIT_DB_PATH = "/app/data/steam_games.duckdb"

# Use the sample database for demo mode (e.g. for GitHub users):
STREAMLIT_DB_PATH = "/app/sample_data/steam_games_sample.duckdb"

BASE_SQL_PATH = Path("/opt/airflow/sql")

# ======== SQL scripts ========

UPSERT_PIPELINE_LOG_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_pipeline_log.sql"
)

# ======== Staging ========


RAW_GAME_DETAILS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_game_details.sql"
)

RAW_CURRENT_PLAYERS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_current_players.sql"
)

RAW_STEAMSPY_GAME_STATS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_steamspy_game_stats.sql"
)

RAW_STEAM_REVIEWS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_steam_reviews.sql"
)

RAW_STEAM_NEWS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_steam_news.sql"
)

RAW_STEAM_ACHIEVEMENT_STATS_SCRIPT = (
    BASE_SQL_PATH / "staging" / "raw_steam_achievement_stats.sql"
)

# ======== Gold ========

UPSERT_GAME_GENRE_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_game_genre.sql"
)

UPSERT_GAME_INFO_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_game_info.sql"
)

UPSERT_GENRE_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_genre.sql"
)

UPSERT_STEAM_GAME_DAILY_STATS_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_steam_game_daily_stats.sql"
)

UPSERT_STEAM_GAME_NEWS_SCRIPT = (
    BASE_SQL_PATH / "dml" / "upsert_steam_game_news.sql"
)

