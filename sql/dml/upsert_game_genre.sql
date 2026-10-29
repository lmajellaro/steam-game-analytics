MERGE INTO game_genre trg
USING (
    SELECT DISTINCT
        appid,
        CAST(genre_id AS INTEGER) AS genreid
    FROM silver_game_details_genres_parsed
    WHERE genre_id IS NOT NULL
) src
ON trg.appid = src.appid
AND trg.genreid = src.genreid

WHEN NOT MATCHED THEN
INSERT (
    appid,
    genreid,
    created_ts
)
VALUES (
    src.appid,
    src.genreid,
    current_timestamp
);