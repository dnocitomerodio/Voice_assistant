pip install -r requirements.txt 

cd api
FLASK_APP=app.py FLASK_ENV=developement flask run &

cd ..
python3 script/voice.py 2>/dev/null