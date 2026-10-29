import sys
sys.path.insert(0, "/app/scripts")

from database.duckdb_connection import get_connection
from settings import STREAMLIT_DB_PATH

import streamlit as st
import duckdb
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Weekly Trends & News",
    layout="wide"
)

# ---------------------------------------------------
# Connection
# ---------------------------------------------------

@st.cache_resource
def get_connection_cached(db_path):
    return duckdb.connect(db_path, read_only=True)

conn = get_connection_cached(STREAMLIT_DB_PATH)

# ---------------------------------------------------
# Page Header
# ---------------------------------------------------

st.title("📈 Weekly Trends & News Correlation")

st.markdown("""
Analyze player trends and identify possible correlations
between major player movements and Steam news events.
""")

# ---------------------------------------------------
# Game Selection
# ---------------------------------------------------

games = conn.execute("""
SELECT DISTINCT game_name
FROM reporting.game_performance_summary
ORDER BY game_name
""").df()

selected_game = st.selectbox(
    "Select Game",
    games["game_name"]
)

# ---------------------------------------------------
# Weekly Trend Data
# ---------------------------------------------------

trend_df = conn.execute("""
SELECT
    w.week_start,
    w.avg_concurrent_players_week,
    w.peak_concurrent_players_week
FROM reporting.steam_game_weekly_stats w
JOIN game_info g
    ON w.appid = g.appid
WHERE g.game_name = ?
ORDER BY week_start
""",
[selected_game]).df()

# ---------------------------------------------------
# Major Events Data
# ---------------------------------------------------

events_df = conn.execute("""
SELECT
    e.week_start,
    e.player_change,
    e.abs_player_change,
    e.news_titles
FROM reporting.game_major_events_with_news e
JOIN game_info g
    ON e.appid = g.appid
WHERE g.game_name = ?
ORDER BY e.week_start
""",
[selected_game]).df()

# ---------------------------------------------------
# Trend Chart
# ---------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=trend_df["week_start"],
        y=trend_df["avg_concurrent_players_week"],
        mode="lines+markers",
        name="Average Players"
    )
)

fig.add_trace(
    go.Scatter(
        x=trend_df["week_start"],
        y=trend_df["peak_concurrent_players_week"],
        mode="lines",
        name="Peak Players"
    )
)

# ---------------------------------------------------
# Major Event Markers
# ---------------------------------------------------

if not events_df.empty:

    for _, row in events_df.iterrows():

        if pd.isna(row["news_titles"]):
            continue

        event_date = row["week_start"]

        trend_row = trend_df[
            trend_df["week_start"] == event_date
        ]

        if trend_row.empty:
            continue

        y_value = trend_row[
            "avg_concurrent_players_week"
        ].iloc[0]

        annotation_y = y_value * 1.03

        titles = str(row["news_titles"]).split(" | ")

        hover_text = "<br>".join(titles)

        fig.add_vline(
            x=event_date,
            line_dash="dash",
            opacity=0.30
        )

        fig.add_trace(
            go.Scatter(
                x=[event_date],
                y=[annotation_y],
                mode="markers+text",
                text=["📰"],
                textposition="top center",
                hovertext=[hover_text],
                hoverinfo="text",
                name="News Event",
                showlegend=False
            )
        )

# ---------------------------------------------------
# Layout
# ---------------------------------------------------

fig.update_layout(
    height=700,
    title=f"{selected_game} - Weekly Trends & Major Events",
    xaxis_title="Date",
    yaxis_title="Players",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# Major Events Table
# ---------------------------------------------------

st.subheader("🎯 Major Trend Events & Related News")

if events_df.empty:

    st.info("No major events detected.")

else:

    display_df = events_df.copy()

    display_df = display_df[
    display_df["news_titles"].notna()
]

    display_df = display_df.rename(
        columns={
            "week_start": "Week",
            "player_change": "Player Change",
            "abs_player_change": "Absolute Change",
            "news_titles": "Related News"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------
# Complete News History
# ---------------------------------------------------

st.subheader("📰 Full News Timeline")

news_df = conn.execute("""
SELECT
    published_date,
    news_title
FROM steam_game_news n
JOIN game_info g
    ON n.appid = g.appid
WHERE g.game_name = ?
ORDER BY published_date DESC
""",
[selected_game]).df()

if news_df.empty:

    st.info("No news available.")

else:

    st.dataframe(
        news_df,
        use_container_width=True,
        hide_index=True
    )