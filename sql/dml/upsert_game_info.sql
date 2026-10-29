MERGE INTO game_info trg
USING (
    SELECT
        APPID AS appid,
        GAME_NAME AS game_name,
        CASE 
            WHEN RELEASE_DATE = '' THEN NULL 
            ELSE strptime(RELEASE_DATE, '%b %d, %Y')::DATE 
        END AS release_date,
        DEVELOPER AS developer,
        PUBLISHER AS publisher,
        INITIAL_PRICE_CENTS_USD AS initial_price_usd,
        IS_FREE AS is_free
    FROM silver_game_details_parsed
) src
ON src.appid = trg.appid

WHEN MATCHED AND (
    src.game_name IS DISTINCT FROM trg.game_name
    OR src.release_date IS DISTINCT FROM trg.release_date
    OR src.developer IS DISTINCT FROM trg.developer
    OR src.publisher IS DISTINCT FROM trg.publisher
    OR src.initial_price_usd IS DISTINCT FROM trg.initial_price_usd
    OR src.is_free IS DISTINCT FROM trg.is_free
) THEN
UPDATE SET
    game_name = src.game_name,
    release_date = src.release_date,
    developer = src.developer,
    publisher = src.publisher,
    initial_price_usd = src.initial_price_usd,
    is_free = src.is_free,
    modified_ts = current_timestamp

WHEN NOT MATCHED THEN
INSERT (
    appid, 
    game_name, 
    release_date, 
    developer, 
    publisher, 
    initial_price_usd, 
    is_free, 
    created_ts
) 
VALUES (
    src.appid, 
    src.game_name, 
    src.release_date, 
    src.developer, 
    src.publisher, 
    src.initial_price_usd, 
    src.is_free, 
    current_timestamp
);
