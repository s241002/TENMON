from flask import Flask, request, jsonify
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos

app = Flask(__name__)

ts = load.timescale()

# ★ ここが重要：Ephemerisは一度だけロード
eph = load('de421.bsp')
earth = eph['earth']

@app.route("/")
def home():
    return "Star API running"

@app.route("/stars")
def stars():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    observer = earth + Topos(latitude_degrees=lat,
                             longitude_degrees=lon)

    t = ts.now()

    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)

    # 明るい星だけ（1.5等星まで）
    bright = df[df['magnitude'] < 1.5]

    result = []

    for hip, row in bright.iterrows():
        star = Star.from_dataframe(row)
        astrometric = observer.at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        if alt.degrees > 0:
            result.append({
                "name": str(hip),
                "alt": round(alt.degrees, 2),
                "az": round(az.degrees, 2)
            })

    return jsonify(result)
