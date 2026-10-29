###################
# Purpose 
###################
# Current Top Games
# Search Game
# KPI Overview

import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH
import streamlit as st


st.title("🎮 Steam Game Performance")

conn = get_connection(STREAMLIT_DB_PATH)

df = conn.execute("""
SELECT *
FROM reporting.game_performance_summary
ORDER BY concurrent_players DESC
""").df()

game = st.selectbox(
    "Select a Game",
    df["game_name"].tolist()
)

game_df = df[df["game_name"] == game]

st.metric(
    "Concurrent Players",
    int(game_df["concurrent_players"].iloc[0])
)

st.metric(
    "Review Score %",
    round(game_df["review_score_pct"].iloc[0], 2)
)

st.metric(
    "Estimated Owners",
    int(game_df["owners_midpoint"].iloc[0])
)

st.dataframe(game_df)