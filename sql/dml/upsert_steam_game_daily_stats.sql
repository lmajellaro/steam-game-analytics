MERGE INTO steam_game_daily_stats trg
USING (
    SELECT
        CURRENT_DATE AS stat_date,
        rcp.appid,
        CAST(rcp.player_count AS INTEGER) AS concurrent_players,
        CAST(replace(ssgsp.owners_min, ',', '') AS INTEGER) AS owners_min,
        CAST(replace(ssgsp.owners_max, ',', '') AS INTEGER) AS owners_max,
        (CAST(replace(ssgsp.owners_min, ',', '') AS INTEGER) + CAST(replace(ssgsp.owners_max, ',', '') AS INTEGER)) / 2 AS owners_midpoint,
        CAST(ssr.total_positive_reviews AS INTEGER) AS positive_reviews,
        CAST(ssr.total_negative_reviews AS INTEGER) AS negative_reviews,
        ROUND(
            (CAST(ssr.total_positive_reviews AS DOUBLE) / NULLIF(CAST(ssr.total_positive_reviews AS DOUBLE) + CAST(ssr.total_negative_reviews AS DOUBLE),0)) * 100,
            2
        ) AS review_score_pct
    FROM raw_current_players rcp
    LEFT JOIN silver_steamspy_game_stats_parsed ssgsp
        ON rcp.appid = ssgsp.appid
    LEFT JOIN silver_steam_reviews_parsed ssr
        ON rcp.appid = ssr.appid
) src
ON trg.stat_date = src.stat_date
AND trg.appid = src.appid
WHEN MATCHED AND (
    src.concurrent_players IS DISTINCT FROM trg.concurrent_players
    OR src.owners_min IS DISTINCT FROM trg.owners_min
    OR src.owners_max IS DISTINCT FROM trg.owners_max
    OR src.owners_midpoint IS DISTINCT FROM trg.owners_midpoint
    OR src.positive_reviews IS DISTINCT FROM trg.positive_reviews
    OR src.negative_reviews IS DISTINCT FROM trg.negative_reviews
    OR src.review_score_pct IS DISTINCT FROM trg.review_score_pct
)
THEN UPDATE SET
    concurrent_players = src.concurrent_players,
    owners_min = src.owners_min,
    owners_max = src.owners_max,
    owners_midpoint = src.owners_midpoint,
    positive_reviews = src.positive_reviews,
    negative_reviews = src.negative_reviews,
    review_score_pct = src.review_score_pct,
    modified_ts = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
INSERT (
    stat_date,
    appid,
    concurrent_players,
    owners_min,
    owners_max,
    owners_midpoint,
    positive_reviews,
    negative_reviews,
    review_score_pct,
    created_ts
)
VALUES (
    src.stat_date,
    src.appid,
    src.concurrent_players,
    src.owners_min,
    src.owners_max,
    src.owners_midpoint,
    src.positive_reviews,
    src.negative_reviews,
    src.review_score_pct,
    CURRENT_TIMESTAMP
);