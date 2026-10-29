MERGE INTO steam_game_news trg
USING (
    SELECT
        appid,
        news_id,
        news_title,
        news_url,
        author,
        published_date
    FROM silver_steam_news_parsed
) src
ON src.appid = trg.appid
AND src.news_id = trg.news_id
WHEN MATCHED AND (
    src.news_title IS DISTINCT FROM trg.news_title
    OR src.news_url IS DISTINCT FROM trg.news_url
    OR src.author IS DISTINCT FROM trg.author
    OR src.published_date IS DISTINCT FROM trg.published_date
) THEN
UPDATE SET
    news_title = src.news_title,
    news_url = src.news_url,
    author = src.author,
    published_date = src.published_date,
    modified_ts = current_timestamp
WHEN NOT MATCHED THEN
INSERT (
    appid,
    news_id,
    news_title,
    news_url,
    author,
    published_date,
    created_ts
)
VALUES (
    src.appid,
    src.news_id,
    src.news_title,
    src.news_url,
    src.author,
    src.published_date,
    current_timestamp
);