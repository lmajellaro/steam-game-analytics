CREATE OR REPLACE TABLE raw_steamspy_game_stats AS
SELECT 
    CAST(appid AS INTEGER) AS appid,
    CAST(raw_json AS JSON) AS raw_json,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp
FROM {source_df};