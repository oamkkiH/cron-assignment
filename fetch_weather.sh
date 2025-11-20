#!/bin/bash
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

if [ -f "requirements.txt" ]; then
  pip install --upgrade pip
  pip install -r requirements.txt
fi

if [ -f "fetch_weather.py" ]; then
  python fetch_weather.py
fi

echo "Valmis!"
