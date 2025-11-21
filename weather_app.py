import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# -------------------------------------------------------------------
# PAGE SETTINGS + GRADIENT BACKGROUND
# -------------------------------------------------------------------
st.set_page_config(page_title="Säädata – OpenWeather (API) + Weatherbit (API)", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #d0ecf7, #f0ffe8);
        background-attachment: fixed;
    }
    .cron-bar {
        background: rgba(255,255,255,0.5);
        padding: 12px;
        border-radius: 10px;
        font-size: 0.9rem;
        margin-top: 40px;
        backdrop-filter: blur(4px);
    }
    .cron-title {
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# LOAD .ENV
# -------------------------------------------------------------------
load_dotenv(dotenv_path="/home/ubuntu/cron_assignment/.env")

DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")

# -------------------------------------------------------------------
# MYSQL FETCH
# -------------------------------------------------------------------
def fetch_city_data(city_name):
    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )

    df = pd.read_sql(
        f"""
        SELECT *
        FROM weather_data
        WHERE city = '{city_name}'
        ORDER BY timestamp DESC
        LIMIT 50
        """,
        conn
    )

    conn.close()
    return df


# -------------------------------------------------------------------
# CRON-LOG FETCH (single-line, compact ✔ format)
# -------------------------------------------------------------------
def read_cron_events():
    logfile = "/home/ubuntu/cron_assignment/weather_cron.log"
    if not os.path.exists(logfile):
        return []

    with open(logfile, "r") as f:
        lines = f.readlines()

    events = []
    for line in reversed(lines[-300:]):     # read last 300 lines, reverse for latest first
        if "OK" in line and line.strip().startswith("2025"):
            try:
                timestamp = line.split("OK")[0].strip()
                t = timestamp[-8:]          # take HH:MM:SS
                events.append(f"{t} ✔")
            except:
                pass
        if len(events) >= 10:
            break

    return events


# -------------------------------------------------------------------
# USER SELECT CITY
# -------------------------------------------------------------------
city = st.selectbox("Valitse kaupunki:", ["Helsinki", "Oulu", "Tampere"])

df = fetch_city_data(city)

latest_open = df[df["source"] == "openweather"].iloc[0]
latest_wb = df[df["source"] == "weatherbit"].iloc[0]

# -------------------------------------------------------------------
# TWO WEATHER CARDS
# -------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌤 OpenWeather API")
    st.markdown(f"### {int(latest_open['temperature'])}°C")
    st.caption(latest_open['description'])
    st.caption(f"Päivitetty: {latest_open['timestamp']}")

with col2:
    st.subheader("🌐 Weatherbit API")
    st.markdown(f"### {int(latest_wb['temperature'])}°C")
    st.caption(latest_wb['description'])
    st.caption(f"Päivitetty: {latest_wb['timestamp']}")

st.markdown("---")

# -------------------------------------------------------------------
# DISPLAY TABLE OF LAST 50 ENTRIES
# -------------------------------------------------------------------
st.subheader("📄 Viimeisimmät 50 havaintoa")
st.dataframe(df, use_container_width=True)

# -------------------------------------------------------------------
# CRON LOG — ONE LINE AT BOTTOM
# -------------------------------------------------------------------
cron_events = read_cron_events()
if cron_events:
    cron_line = "  |  ".join(cron_events)
else:
    cron_line = "Ei lokitietoa"

st.markdown("<div class='cron-bar'><div class='cron-title'>⏱ Cron-ajot</div>" + cron_line + "</div>", unsafe_allow_html=True)
