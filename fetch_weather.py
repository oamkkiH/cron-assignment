import requests
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

# --- LOAD .ENV ---
load_dotenv(dotenv_path="/home/ubuntu/cron_assignment/.env")

# --- API KEYS ---
OWM_KEY = os.getenv("OPENWEATHER_API_KEY")
WB_KEY = os.getenv("WEATHERBIT_API_KEY")

# --- MYSQL ---
DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")

# --- CITIES ---
CITIES = {
    "Helsinki": {"lat": 60.1699, "lon": 24.9384},
    "Oulu": {"lat": 65.0121, "lon": 25.4651},
    "Tampere": {"lat": 61.4978, "lon": 23.7610}
}


def fetch_openweather(city, lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OWM_KEY}&units=metric"
    )

    r = requests.get(url).json()

    return {
        "city": city,
        "temp": round(r["main"]["temp"]),
        "desc": r["weather"][0]["description"].title(),
        "source": "openweather"
    }


def fetch_weatherbit(city, lat, lon):
    url = (
        f"https://api.weatherbit.io/v2.0/current?"
        f"lat={lat}&lon={lon}&key={WB_KEY}&units=M"
    )

    r = requests.get(url).json()

    data = r["data"][0]

    return {
        "city": city,
        "temp": round(data["temp"]),
        "desc": data["weather"]["description"],
        "source": "weatherbit"
    }


def insert_row(data):
    conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
    )

    cursor = conn.cursor()

    sql = """
    INSERT INTO weather_data (city, temperature, description, source, timestamp)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        data["city"],
        data["temp"],
        data["desc"],
        data["source"],
        datetime.now()
    )

    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()


# --- MAIN EXECUTION ---
print("=== WEATHER FETCH STARTED ===")

for city, coords in CITIES.items():
    lat = coords["lat"]
    lon = coords["lon"]

    # --- OpenWeather ---
    try:
        data = fetch_openweather(city, lat, lon)
        insert_row(data)
        print(f"[OK] OpenWeather {city}: {data['temp']}°C")
    except Exception as e:
        print(f"[ERROR] OpenWeather {city}: {e}")

    # --- Weatherbit ---
    try:
        data = fetch_weatherbit(city, lat, lon)
        insert_row(data)
        print(f"[OK] Weatherbit {city}: {data['temp']}°C")
    except Exception as e:
        print(f"[ERROR] Weatherbit {city}: {e}")

print("=== WEATHER FETCH COMPLETE ===")
