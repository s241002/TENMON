from flask import Flask, request, jsonify
from skyfield.api import Star, load, Topos
from skyfield.data import hipparcos

app = Flask(__name__)

ts = load.timescale()
planets = load('de421.bsp')

@app.route("/")
def home():
    return "API is running"
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    t = ts.now()

    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)

    bright_stars = df[df["magnitude"] < 2.5].head(20)

    result = []
    for hip, row in bright_stars.iterrows():
        star = Star.from_dataframe(row)
        astrometric = (planets["earth"] + observer).at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        if alt.degrees > 0:
            result.append({
                "hip": int(hip),
                "alt": alt.degrees,
                "az": az.degrees
            })

    return jsonify(result)

if __name__ == "__main__":

    app.run()
