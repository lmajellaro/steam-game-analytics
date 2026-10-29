MERGE INTO genre trg
USING (
    SELECT DISTINCT
        CAST(genre_id AS INTEGER) AS genreid,
        genre_name
    FROM silver_game_details_genres_parsed
    WHERE genre_id IS NOT NULL
) src
ON src.genreid = trg.genreid

WHEN MATCHED AND (
    src.genre_name IS DISTINCT FROM trg.genre_name
) THEN
UPDATE SET
    genre_name = src.genre_name,
    modified_ts = current_timestamp

WHEN NOT MATCHED THEN
INSERT (
    genreid,
    genre_name,
    created_ts
)
VALUES (
    src.genreid,
    src.genre_name,
    current_timestamp
);