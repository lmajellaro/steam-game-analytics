from pathlib import Path
import shutil
import duckdb

DATABASES = [
    Path("/app/data/steam_games.duckdb"),
    Path("/app/sample_data/steam_games_sample.duckdb"),
]

VIEW_SQL = """
CREATE OR REPLACE VIEW reporting.steam_game_weekly_stats AS
WITH weekly_base AS (
    SELECT
        CAST(date_trunc('week', stat_date) AS TIMESTAMP) AS week_start,
        appid,
        AVG(concurrent_players) AS avg_concurrent_players_week,
        MAX(concurrent_players) AS peak_concurrent_players_week,
        MAX(owners_midpoint) - MIN(owners_midpoint) AS owners_growth_week,
        MAX(positive_reviews) - MIN(positive_reviews) AS positive_reviews_growth_week,
        MAX(negative_reviews) - MIN(negative_reviews) AS negative_reviews_growth_week,
        AVG(review_score_pct) AS avg_review_score_pct
    FROM steam_game_daily_stats
    GROUP BY week_start, appid
),
weekly_with_lag AS (
    SELECT
        *,
        LAG(avg_concurrent_players_week) OVER (
            PARTITION BY appid
            ORDER BY week_start
        ) AS prev_avg_players
    FROM weekly_base
)
SELECT
    week_start,
    appid,
    avg_concurrent_players_week,
    peak_concurrent_players_week,
    owners_growth_week,
    positive_reviews_growth_week,
    negative_reviews_growth_week,
    avg_review_score_pct,
    ROUND(
        (avg_concurrent_players_week - prev_avg_players)
        / NULLIF(prev_avg_players, 0) * 100,
        2
    ) AS growth_pct
FROM weekly_with_lag
"""


def refresh_view(db_path: Path) -> None:
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}")

    backup_path = db_path.with_name(
        f"{db_path.stem}.before_weekly_view_fix.duckdb"
    )

    # Preserve the original database before making any changes.
    if not backup_path.exists():
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print(f"Existing backup retained: {backup_path}")

    print(f"\nUpdating: {db_path}")

    conn = duckdb.connect(str(db_path))
    try:
        conn.execute(VIEW_SQL)

        columns = conn.execute(
            "DESCRIBE SELECT * FROM reporting.steam_game_weekly_stats"
        ).fetchall()

        week_start = next(
            (col for col in columns if col[0] == "week_start"), None
        )

        if week_start is None or week_start[1] != "TIMESTAMP":
            raise RuntimeError(
                f"Unexpected week_start type: {week_start}"
            )

        # Execute the view to ensure its definition binds successfully.
        conn.execute(
            "SELECT * FROM reporting.steam_game_weekly_stats LIMIT 1"
        ).fetchall()

        print("View updated and verified.")
        print(f"week_start type: {week_start[1]}")
    finally:
        conn.close()


def main() -> None:
    for db_path in DATABASES:
        refresh_view(db_path)

    print("\nAll database updates completed successfully.")


if __name__ == "__main__":
    main()
