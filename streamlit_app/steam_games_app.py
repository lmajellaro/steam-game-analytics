import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Steam Game Analytics",
    page_icon="🎮",
    layout="wide"
)

# ---------------------------------------------------
# Background Image Loading & Styling
# ---------------------------------------------------

def get_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

try:
    image_path = Path("assets/steam_game_analytics_bg.png")
    img_base64 = get_base64(image_path)
except FileNotFoundError:
    img_base64 = ""

# Set your target opacity here (0.0 = hidden/pure theme color, 1.0 = full raw image)
bg_opacity = 0.3

# Dynamically calculate the matching dark mask overlay percentage
overlay_alpha = 1.0 - bg_opacity

st.markdown(
    f"""
    <style>
    /* Target the base container Streamlit guarantees to draw across the screen */
    .stApp {{
        background-image: linear-gradient(rgba(14, 17, 23, {overlay_alpha}), rgba(14, 17, 23, {overlay_alpha})), 
                          url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: #0e1117 !important;
    }}

    /* Modern Glass Container styling */
    .glass {{
        background: rgba(20, 24, 33, 0.75);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# Header (Fixed formatting issue)
# ---------------------------------------------------

st.markdown(
    """
    <div class="glass">
        <h1 style='margin-top: 0;'>🎮 Steam Game Analytics</h1>
        <h3 style='color: #8892b0; margin-bottom: 1.5rem;'>Track. Analyze. Discover.</h3>
        <p style='font-size: 1.1rem; line-height: 1.6; color: #ccd6f6;'>
            A modern analytics platform that collects and analyzes Steam game data 
            using Steam APIs, SteamSpy and DuckDB.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------------------------------------------
# Project Overview
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Games Tracked",
        value="200+"
    )

with col2:
    st.metric(
        label="Daily Refresh",
        value="24h"
    )

with col3:
    st.metric(
        label="Data Sources",
        value="Steam + SteamSpy"
    )

st.divider()

st.subheader("📊 Available Dashboards")

st.markdown("""
### 🏆 Best Games
Identify top performing games every week.

### 📈 Weekly Trends
Track player growth and ownership evolution.

### 🚀 Fastest Growing Games
Spot emerging hits before they become mainstream.

### 🎭 Genre Analytics
Analyze genre market share and trends.

### 📰 News Impact Analysis
Measure the effect of Steam news announcements on player activity.
""")

st.divider()

st.info(
    "Use the left navigation menu to explore dashboards."
)
