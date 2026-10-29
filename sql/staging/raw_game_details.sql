CREATE OR REPLACE TABLE raw_game_details AS
SELECT 
    CAST(app_id AS INTEGER) AS appid,
    CAST(raw_json AS JSON) AS raw_json,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp
FROM {source_df};