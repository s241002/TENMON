from flask import Flask, request, jsonify
from skyfield.api import load, Topos, Star

app = Flask(__name__)

ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']

# ⭐ 明るい恒星
BRIGHT_STARS = [
    {"name": "Sirius", "ra": 6.752, "dec": -16.716},
    {"name": "Canopus", "ra": 6.399, "dec": -52.695},
    {"name": "Arcturus", "ra": 14.261, "dec": 19.182},
    {"name": "Vega", "ra": 18.615, "dec": 38.783},
    {"name": "Capella", "ra": 5.279, "dec": 45.997},
]

@app.route("/")
def home():
    return "Star AR API running"

@app.route("/stars")
def stars():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    direction = request.args.get("dir", 0)
    return {
        "stars": [
            {"name": "Betelgeuse", "x": 100, "y": 120},
            {"name": "Rigel", "x": 150, "y": 200}
        ]
    }
