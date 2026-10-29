------------------------------------------------
-- Bronze Layer
CREATE OR REPLACE TABLE raw_game_details (
    appid INTEGER,
    raw_json JSON,
    load_timestamp TIMESTAMP
);

CREATE OR REPLACE TABLE raw_current_players (
    appid INTEGER,
    player_count INTEGER,
    load_timestamp TIMESTAMP
);

CREATE OR REPLACE TABLE raw_steamspy_game_stats (
    appid INTEGER,
    raw_json JSON,
    load_timestamp TIMESTAMP
);

CREATE OR REPLACE TABLE raw_steam_reviews (
    appid INTEGER,
    raw_json JSON,
    load_timestamp TIMESTAMP
);

CREATE OR REPLACE TABLE raw_steam_news (
    appid INTEGER,
    raw_json JSON,
    load_timestamp TIMESTAMP
);

CREATE OR REPLACE TABLE raw_steam_achievement_stats (
    appid INTEGER,
    raw_json JSON,
    load_timestamp TIMESTAMP
);

------------------------------------------------
-- Silver Layer
CREATE OR REPLACE VIEW silver_game_details_parsed AS
SELECT
    g.appid,
    json_extract_string(g.raw_json, '$.data.name') AS game_name,
    json_extract_string(g.raw_json, '$.data.release_date.date') AS release_date,
    json_extract_string(g.raw_json, '$.data.developers[0]') AS developer,
    json_extract_string(g.raw_json, '$.data.publishers[0]') AS publisher,
    json_extract(g.raw_json, '$.data.price_overview.initial') AS initial_price_cents_usd,
    json_extract(g.raw_json, '$.data.is_free') AS is_free,
    g.load_timestamp
FROM raw_game_details g;

CREATE OR REPLACE VIEW silver_game_details_genres_parsed AS
SELECT
    g.appid,
  
    -- flattened genre fields
    json_extract_string(genre.value, '$.id') AS genre_id,
    json_extract_string(genre.value, '$.description') AS genre_name,
    g.load_timestamp    
FROM raw_game_details g,
LATERAL json_each(json_extract(g.raw_json, '$.data.genres')) AS genre;


CREATE OR REPLACE VIEW silver_steamspy_game_stats_parsed AS
SELECT
    appid,
    json_extract_string(raw_json, '$.positive') AS positive_reviews,
    json_extract_string(raw_json, '$.negative') AS negative_reviews,
    split_part(json_extract_string(raw_json, '$.owners'), '..', 1) AS owners_min,
    split_part(json_extract_string(raw_json, '$.owners'), '..', 2) AS owners_max,
    load_timestamp
FROM raw_steamspy_game_stats;


CREATE OR REPLACE VIEW silver_steam_reviews_parsed AS
SELECT
    appid,
    json_extract_string(raw_json, '$.query_summary.review_score_desc') AS review_score_desc,
    json_extract_string(raw_json, '$.query_summary.review_score') AS review_score,
    json_extract_string(raw_json, '$.query_summary.total_positive') AS total_positive_reviews,
    json_extract_string(raw_json, '$.query_summary.total_negative') AS total_negative_reviews,
    json_extract_string(raw_json, '$.query_summary.total_reviews') AS total_reviews,
    load_timestamp
FROM raw_steam_reviews;


CREATE OR REPLACE VIEW silver_steam_news_parsed AS
SELECT
    r.appid,
    json_extract_string(news.value, '$.gid') AS news_id,
    json_extract_string(news.value, '$.title') AS news_title,
    json_extract_string(news.value, '$.url') AS news_url,
    json_extract_string(news.value, '$.author') AS author,
    to_timestamp(
        CAST(
            json_extract_string(news.value, '$.date')
            AS BIGINT
        )
    ) AS published_date,
    r.load_timestamp
FROM raw_steam_news r,
LATERAL json_each(
    json_extract(r.raw_json, '$.appnews.newsitems')
) AS news;

------------------------------------------------
-- Gold Layer
-- Fact Table: steam_game_daily_stats
CREATE OR REPLACE TABLE steam_game_daily_stats (
    stat_date DATE,
    appid INTEGER,
    concurrent_players INTEGER,
    owners_min INTEGER,
    owners_max INTEGER,
    owners_midpoint INTEGER,
    positive_reviews INTEGER,
    negative_reviews INTEGER,
    review_score_pct DOUBLE,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);

-- Dimension: game_info
CREATE OR REPLACE TABLE game_info (
    appid INTEGER PRIMARY KEY,
    game_name TEXT,
    release_date DATE,
    developer TEXT,
    publisher TEXT,
    initial_price_usd DOUBLE,
    is_free BOOLEAN,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);

-- Dimension: genre
CREATE OR REPLACE TABLE genre (
    genreid INTEGER PRIMARY KEY,
    genre_name TEXT,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);

-- Bridge Table: game_genre
CREATE OR REPLACE TABLE game_genre (
    appid INTEGER,
    genreid INTEGER,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP,
    PRIMARY KEY (appid, genreid)
);

-- Dimension: steam_game_news
CREATE OR REPLACE TABLE steam_game_news (
    appid INTEGER,
    news_id VARCHAR,
    news_title VARCHAR,
    news_url VARCHAR,
    author VARCHAR,
    published_date TIMESTAMP,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);

------------------------------------------------
------------------------------------------------
-- Reporting Layer

CREATE OR REPLACE SCHEMA reporting;

-- View: steam_game_weekly_stats
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
    GROUP BY
        week_start,
        appid
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
    ROUND((avg_concurrent_players_week - prev_avg_players)/NULLIF(prev_avg_players, 0)* 100,2) AS growth_pct
FROM weekly_with_lag;

-- View: best_game_per_week
CREATE OR REPLACE VIEW reporting.best_game_per_week AS
SELECT
    week_start,
    s.appid,
    g.game_name,
    avg_concurrent_players_week,
    growth_pct,
    avg_review_score_pct
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY week_start
            ORDER BY avg_concurrent_players_week DESC
        ) AS rank
    FROM reporting.steam_game_weekly_stats
) s
JOIN game_info g
    ON s.appid = g.appid
WHERE rank <= 3
  AND week_start = (
      SELECT MAX(week_start)
      FROM reporting.steam_game_weekly_stats
  )
ORDER BY rank;

-- View: weekly_genre_market_share
-- How many average concurrent players belong to games of this genre
-- Dashboards: 05_Weekly_Trends
CREATE OR REPLACE VIEW reporting.weekly_genre_market_share AS
SELECT
    w.week_start,
    g.genre_name,
    CAST(SUM(w.avg_concurrent_players_week) AS INTEGER) AS genre_total_players,
    SUM(w.peak_concurrent_players_week) AS genre_peak_players,
    COUNT(DISTINCT w.appid) AS number_of_games
FROM steam_game_weekly_stats w
JOIN game_genre gg
    ON w.appid = gg.appid
JOIN genre g
    ON gg.genreid = g.genreid
	WHERE  genre_name NOT ILIKE '%Free To Play%'
	AND genre_name NOT ILIKE '%Early Access%'
GROUP BY
    w.week_start,
    g.genre_name;

-- View: fastest_growing_games
CREATE OR REPLACE VIEW reporting.fastest_growing_games AS
SELECT
    w.week_start,
    g.game_name,
    w.appid,
    w.avg_concurrent_players_week,
    w.growth_pct,
    w.owners_growth_week,
    w.positive_reviews_growth_week,
    w.avg_review_score_pct
FROM steam_game_weekly_stats w
JOIN game_info g
    ON w.appid = g.appid
WHERE w.growth_pct IS NOT NULL;


-- latest_game_news
CREATE OR REPLACE VIEW reporting.latest_game_news AS
SELECT
    n.appid,
    g.game_name,
    n.news_title,
    n.news_url,
    n.author,
    n.published_date
FROM steam_game_news n
JOIN game_info g
    ON n.appid = g.appid;


CREATE OR REPLACE VIEW reporting.game_performance_summary AS
SELECT
    g.appid,
    g.game_name,
    g.developer,
    g.publisher,
    g.release_date,
    s.concurrent_players,
    s.owners_midpoint,
    s.positive_reviews,
    s.negative_reviews,
    s.review_score_pct
FROM game_info g
JOIN (
    SELECT *
    FROM steam_game_daily_stats
    QUALIFY ROW_NUMBER()
        OVER (
            PARTITION BY appid
            ORDER BY stat_date DESC
        ) = 1
) s
ON g.appid = s.appid;

CREATE OR REPLACE VIEW reporting.game_news_timeline AS
SELECT
    n.appid,
    g.game_name,
    n.news_id,
    n.news_title,
    n.news_url,
    n.author,
    n.published_date
FROM steam_game_news n
JOIN game_info g
    ON n.appid = g.appid;


CREATE OR REPLACE VIEW reporting.game_trend_events AS
WITH trend_changes AS (
    SELECT
        week_start,
        appid,
        avg_concurrent_players_week,
        LAG(avg_concurrent_players_week)
            OVER (
                PARTITION BY appid
                ORDER BY week_start
            ) AS prev_avg_players
    FROM reporting.steam_game_weekly_stats
)
SELECT
    week_start,
    appid,
    avg_concurrent_players_week,
    prev_avg_players,
    avg_concurrent_players_week - prev_avg_players
        AS player_change,
    ABS(
        avg_concurrent_players_week - prev_avg_players
    ) AS abs_player_change
FROM trend_changes
WHERE prev_avg_players IS NOT NULL;


CREATE OR REPLACE VIEW reporting.game_major_events AS
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY appid
            ORDER BY abs_player_change DESC
        ) AS rn
    FROM reporting.game_trend_events
)
WHERE rn <= 5;


CREATE OR REPLACE VIEW reporting.game_major_events_with_news AS
WITH news_by_week AS (
    SELECT
        n.appid,
        DATE_TRUNC('week', n.published_date) AS week_start,
        string_agg(
            n.news_title,
            ' | '
            ORDER BY n.published_date
        ) AS news_titles
    FROM steam_game_news n
    GROUP BY
        n.appid,
        DATE_TRUNC('week', n.published_date)
)
SELECT
    e.appid,
    e.week_start,
    e.player_change,
    e.abs_player_change,
    nbw.news_titles
FROM reporting.game_major_events e
LEFT JOIN news_by_week nbw
    ON e.appid = nbw.appid
   AND e.week_start = nbw.week_start;

------------------------------------------------
-- Logging
-- Pipeline Logging
CREATE OR REPLACE TABLE pipeline_runs (
    dag_id VARCHAR,
    run_date TIMESTAMP,
    status VARCHAR,
    last_success_timestamp TIMESTAMP
);