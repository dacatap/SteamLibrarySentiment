import streamlit as st
import duckdb
import boto3
import tempfile
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(
    page_title="Steam Library Player Sentiment",
    page_icon="🎮",
    layout="wide"
)

@st.cache_resource
def load_db():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION_NAME")
    )
    tmp = tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False)
    s3.download_fileobj(os.environ.get("AWS_S3_BUCKET_NAME"), "analytics/prod.duckdb", tmp)
    tmp.close()
    return duckdb.connect(tmp.name, read_only=True)

@st.cache_data
def get_games(_con):
    return _con.execute("SELECT steam_app_id, title FROM dim_games ORDER BY title").df()

@st.cache_data
def get_reviews(_con, steam_app_id):
    return _con.execute("""
        SELECT review_date, recommendations_up, recommendations_down
        FROM fact_daily_metrics
        WHERE steam_app_id = ?
        ORDER BY review_date
    """, [steam_app_id]).df()

@st.cache_data
def get_player_counts(_con, steam_app_id):
    return _con.execute("""
        SELECT recorded_date, avg_players
        FROM fact_player_counts
        WHERE steam_app_id = ?
        ORDER BY recorded_date
    """, [steam_app_id]).df()

@st.cache_data
def get_announcements(_con, steam_app_id):
    return _con.execute("""
        SELECT published_date, title, url
        FROM fact_announcements
        WHERE steam_app_id = ?
        ORDER BY published_date
    """, [steam_app_id]).df()

@st.cache_data
def get_price_events(_con, steam_app_id):
    return _con.execute("""
        SELECT price_date, discount_pct, price_amount, regular_price
        FROM fact_price_history
        WHERE steam_app_id = ? AND discount_pct > 0
        ORDER BY price_date
    """, [steam_app_id]).df()

# --- App ---
st.title("🎮 Steam Library Player Sentiment")
st.caption("Correlating player counts and review sentiment with game events across your Steam library.")

try:
    con = load_db()
    games = get_games(con)

    selected_title = st.selectbox(
        "Select a game",
        options=games["title"].tolist()
    )

    steam_app_id = str(games[games["title"] == selected_title]["steam_app_id"].values[0])

    reviews = get_reviews(con, steam_app_id)
    players = get_player_counts(con, steam_app_id)
    announcements = get_announcements(con, steam_app_id)
    price_events = get_price_events(con, steam_app_id)

    # --- Chart ---
    fig = go.Figure()

    # Player count line
    if not players.empty:
        fig.add_trace(go.Scatter(
            x=players["recorded_date"],
            y=players["avg_players"],
            name="Avg Players",
            line=dict(color="#5B9BD5", width=2),
            yaxis="y1"
        ))

    # Review sentiment lines
    if not reviews.empty:
        fig.add_trace(go.Scatter(
            x=reviews["review_date"],
            y=reviews["recommendations_up"],
            name="Positive Reviews",
            line=dict(color="#70AD47", width=1.5, dash="dot"),
            yaxis="y2"
        ))
        fig.add_trace(go.Scatter(
            x=reviews["review_date"],
            y=reviews["recommendations_down"],
            name="Negative Reviews",
            line=dict(color="#FF6B6B", width=1.5, dash="dot"),
            yaxis="y2"
        ))

    # Announcement markers
    if not announcements.empty:
        fig.add_trace(go.Scatter(
            x=announcements["published_date"],
            y=[0] * len(announcements),
            mode="markers",
            name="Announcement",
            marker=dict(symbol="triangle-up", size=12, color="#FFC000"),
            customdata=announcements[["title", "url"]].values,
            hovertemplate="<b>📢 Announcement</b><br>%{customdata[0]}<extra></extra>",
            yaxis="y1"
        ))

    # Sale/discount markers
    if not price_events.empty:
        fig.add_trace(go.Scatter(
            x=price_events["price_date"],
            y=[0] * len(price_events),
            mode="markers",
            name="Sale",
            marker=dict(symbol="diamond", size=12, color="#9B59B6"),
            customdata=price_events[["discount_pct", "price_amount"]].values,
            hovertemplate="<b>🏷️ Sale</b><br>%{customdata[0]}% off — $%{customdata[1]:.2f}<extra></extra>",
            yaxis="y1"
        ))

    fig.update_layout(
        title=f"{selected_title} — Player Sentiment Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Avg Players", side="left"),
        yaxis2=dict(title="Review Count", side="right", overlaying="y"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        height=550,
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="#FAFAFA")
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Event tables below chart ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📢 Announcements")
        if not announcements.empty:
            for _, row in announcements.iterrows():
                st.markdown(f"**{row['published_date']}** — [{row['title']}]({row['url']})")
        else:
            st.caption("No announcements found.")

    with col2:
        st.subheader("🏷️ Sale History")
        if not price_events.empty:
            for _, row in price_events.iterrows():
                st.markdown(f"**{row['price_date']}** — {int(row['discount_pct'])}% off (${row['price_amount']:.2f})")
        else:
            st.caption("No sale history found.")

except Exception as e:
    st.error(f"Could not load data: {e}")
    st.caption("Make sure AWS credentials are set and prod.duckdb exists in S3.")