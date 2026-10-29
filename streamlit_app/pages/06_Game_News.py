#######################################
# Purpose 
#######################################
# Display latest updates/news by game.

import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH
import streamlit as st

st.title("📰 Steam News")

conn = get_connection(STREAMLIT_DB_PATH)

df = conn.execute("""
SELECT *
FROM reporting.latest_game_news
ORDER BY published_date DESC
LIMIT 100
""").df()

for _, row in df.iterrows():

    st.subheader(row["game_name"])

    st.write(row["news_title"])

    st.caption(row["published_date"])

    st.link_button(
        "Open Article",
        row["news_url"]
    )

    st.divider()