#############################
# Purpose 
#############################
# Which genres dominate Steam

import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH
import streamlit as st
import plotly.express as px

st.title("🎯 Genre Trends")

conn = get_connection(STREAMLIT_DB_PATH)

df = conn.execute("""
SELECT 
    week_start,
    genre_name,
    sum(genre_total_players) as genre_total_players,
    sum(genre_peak_players) as genre_peak_players,
    max(number_of_games) as number_of_games
FROM reporting.weekly_genre_market_share
GROUP BY week_start, genre_name
ORDER BY week_start, genre_name;
""").df()


fig = px.line(
    df,
    x="week_start",
    y="genre_total_players",
    color="genre_name",
    labels={
        "week_start": "Timeline (Weeks)",
        "genre_total_players": "Total Active Players",
        "genre_name": "Game Genre"
    }
)
fig.show()

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "week_start": "Week",
        "genre_name": "Genre",

        "genre_total_players":
            st.column_config.NumberColumn(
                "Genre Total Players per Week",
                format="%,d"
            ),

        "genre_peak_players":
            st.column_config.NumberColumn(
                "Genre Peak Players per Week",
                format="%,d"
            ),

        "number_of_games":
            st.column_config.NumberColumn(
                "# Top Games",
                format="%,d"
            )
    }
)
