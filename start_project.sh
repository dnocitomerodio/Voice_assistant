#!/bin/bash
echo "Downloading dependencies..."
pip install -r requirements.txt

echo "Starting API Flask..."
cd api
FLASK_APP=app.py FLASK_ENV=development flask run &

cd ..
echo "Initializing voice assistant script."
python3 script/voice.py 2>/dev/null
