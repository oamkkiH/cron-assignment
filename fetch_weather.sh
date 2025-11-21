#!/bin/bash
# Working directory
cd /home/ubuntu/cron_assignment || exit

# Use absolute venv path
VENV="/home/ubuntu/cron_assignment/venv"

# Activate venv
source "$VENV/bin/activate"

# Run weather fetch
python3 fetch_weather.py >> weather_cron.log 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') OK" >> weather_cron.log
