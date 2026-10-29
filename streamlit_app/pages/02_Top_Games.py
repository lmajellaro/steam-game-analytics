################
# Purpose 
################
# Weekly winners

import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH
import streamlit as st

st.title("🏆 Latest Week Top 3 Games")

conn = get_connection(STREAMLIT_DB_PATH)

df = conn.execute("""
SELECT *
FROM reporting.best_game_per_week
""").df()

st.dataframe(df)