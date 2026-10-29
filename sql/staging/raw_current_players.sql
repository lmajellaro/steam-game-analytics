CREATE OR REPLACE TABLE raw_current_players AS
SELECT 
    CAST(app_id AS INTEGER) AS appid,
    CAST(player_count AS INTEGER) AS player_count,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp
FROM {source_df};