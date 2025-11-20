import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# -------------------------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------------------------
st.set_page_config(page_title="Säädata – OpenWeather + Weatherbit",
                   layout="wide")

# -------------------------------------------------------------------
# LOAD .ENV
# -------------------------------------------------------------------
load_dotenv(dotenv_path="/home/ubuntu/cron_assignment/.env")

DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")

# -------------------------------------------------------------------
# BACKGROUND IMAGE LOGIC
# -------------------------------------------------------------------

def set_background(image_file):
    """Insert a CSS background."""
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = data.hex()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{data.hex()}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def choose_background(desc):
    """Pick background based on description."""
    desc = desc.lower()
    if "snow" in desc:
        return "images/snow.jpg"
    if "rain" in desc:
        return "images/rain.jpg"
    if "fog" in desc or "mist" in desc:
        return "images/fog.jpg"
    if "cloud" in desc:
        return "images/cloudy.jpg"
    return "images/sunny.jpg"

# -------------------------------------------------------------------
# MYSQL FETCH
# -------------------------------------------------------------------

def fetch_city_data(city_name):
    """Fetch latest OpenWeather + Weatherbit entries."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
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
# UI START
# -------------------------------------------------------------------

st.title("Säädata – OpenWeather + Weatherbit")


# -------------------------------------------------------------------
# SELECT CITY
# -------------------------------------------------------------------

city = st.selectbox("Valitse kaupunki:",
                    ["Helsinki", "Oulu", "Tampere"])


df = fetch_city_data(city)

# Show graceful message if database empty
if df.empty:
    st.warning("Ei vielä dataa tälle kaupungille.")
    st.stop()

# Ensure temperature int
df["temperature"] = df["temperature"].astype(float).round().astype(int)

# -------------------------------------------------------------------
# Pick latest sources
# -------------------------------------------------------------------

latest_open = df[df["source"] == "openweather"].head(1)
latest_wbit = df[df["source"] == "weatherbit"].head(1)

# Handle missing data
if latest_open.empty:
    st.error("OpenWeather-dataa ei löytynyt!")
    st.stop()

if latest_wbit.empty:
    st.error("Weatherbit-dataa ei löytynyt!")
    st.stop()

open_temp = latest_open.iloc[0]["temperature"]
open_desc = latest_open.iloc[0]["description"]
open_time = latest_open.iloc[0]["timestamp"]

wb_temp = latest_wbit.iloc[0]["temperature"]
wb_desc = latest_wbit.iloc[0]["description"]
wb_time = latest_wbit.iloc[0]["timestamp"]

# -------------------------------------------------------------------
# SET BACKGROUND IMAGE BASED ON OPENWEATHER (PRIMARY SOURCE)
# -------------------------------------------------------------------

bg = choose_background(open_desc)
set_background(bg)

# -------------------------------------------------------------------
# TOP ROW – TWO CARDS
# -------------------------------------------------------------------
col1, col2 = st.columns(2)

# ---- CARD: OPENWEATHER ----
with col1:
    st.subheader(f"🌤️ OpenWeather – {city}")

    # temperature color
    if open_temp < 0:
        color = "blue"
    elif open_temp >= 25:
        color = "red"
    else:
        color = "black"

    st.markdown(
        f"""
        <div style="font-size:48px; font-weight:700; color:{color}">
            {open_temp}°C
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(f"**Kuvaus:** {open_desc}")
    st.caption(f"Päivitetty: {open_time}")


# ---- CARD: WEATHERBIT ----
with col2:
    st.subheader(f"🌦️ Weatherbit – {city}")

    if wb_temp < 0:
        color2 = "blue"
    elif wb_temp >= 25:
        color2 = "red"
    else:
        color2 = "black"

    st.markdown(
        f"""
        <div style="font-size:48px; font-weight:700; color:{color2}">
            {wb_temp}°C
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(f"**Kuvaus:** {wb_desc}")
    st.caption(f"Päivitetty: {wb_time}")


# -------------------------------------------------------------------
# LAST UPDATE LABEL 
# -------------------------------------------------------------------
last_update = df["timestamp"].max()
st.caption(f"⏱️ Viimeisin päivitys tietokantaan: {last_update}")


# -------------------------------------------------------------------
# TABLE WITH ALL ENTRIES
# -------------------------------------------------------------------
st.subheader("Tallennetut säädatapisteet")
st.dataframe(df, use_container_width=True)
