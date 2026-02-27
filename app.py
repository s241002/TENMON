import random
import time

@app.route("/stress")
def stress():
    count = int(request.args.get("n"))

    start = time.time()

    result = []

    for i in range(count):
        # ダミー計算（星計算相当）
        x = random.random() * 360
        y = random.random() * 90

        result.append({
            "id": i,
            "alt": y,
            "az": x
        })

    elapsed = time.time() - start

    return jsonify({
        "count": count,
        "time_sec": round(elapsed, 4)
    })

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
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    direction = float(request.args.get("dir"))  # ← 追加

    observer = earth + Topos(latitude_degrees=lat,
                             longitude_degrees=lon)

    t = ts.now()
    result = []

    for s in BRIGHT_STARS:
        star = Star(ra_hours=s["ra"], dec_degrees=s["dec"])
        astrometric = observer.at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        if alt.degrees > 0:

            # ⭐ 方位差計算（超重要）
            diff = abs((az.degrees - direction + 180) % 360 - 180)

            if diff < 30:  # ← 視野 ±30°
                result.append({
                    "name": s["name"],
                    "alt": round(alt.degrees, 2),
                    "az": round(az.degrees, 2),
                    "diff": round(diff, 2)
                })

    return jsonify(result)
