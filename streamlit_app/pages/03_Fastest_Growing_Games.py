###################
# Purpose 
###################
# Trend discovery

import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH
import streamlit as st
import plotly.express as px

st.title("🚀 Fastest Growing Games")

conn = get_connection(STREAMLIT_DB_PATH)

df = conn.execute("""
SELECT week_start AS "Week Start"
	,game_name AS "Game Name"
	,appid AS "App ID"
	,avg_concurrent_players_week AS "Average Concurrent Players"
	,growth_pct AS "Percentage Growth"
	,positive_reviews_growth_week AS "Positive Reviews Growth"
	,avg_review_score_pct AS "Percentage Average Review Score"
FROM reporting.fastest_growing_games
ORDER BY week_start DESC
	,growth_pct DESC
""").df()

df_graph = conn.execute("""
SELECT *
FROM reporting.fastest_growing_games
ORDER BY week_start DESC,
         growth_pct DESC
LIMIT 20
""").df()

st.dataframe(df)

fig = px.bar(
	df_graph,
    x="game_name",
    y="growth_pct"
)

st.plotly_chart(fig, use_container_width=True)
