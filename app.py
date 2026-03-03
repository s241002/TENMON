# app.py
import os
import json
from flask import Flask, request, jsonify
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u

app = Flask(__name__)

# --- JSON ファイル ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
stars_file = os.path.join(BASE_DIR, "stars_mag4_light.json")
lines_file = os.path.join(BASE_DIR, "constellation_lines.json")

with open(stars_file, "r", encoding="utf-8") as f:
    stars_data = json.load(f)

with open(lines_file, "r", encoding="utf-8") as f:
    lines_data = json.load(f)

# --- 星サイズ（等級→サイズ） ---
def mag_to_size(mag):
    return max(1, int(6 - mag))

# --- RA/Dec → Az/Alt → 画面座標 ---
def sky_to_screen(alt, az, alt_center, az_center, fov, width=240, height=240):
    # 視野角内か確認
    delta_alt = alt - alt_center
    delta_az = (az - az_center + 180) % 360 - 180  # 0-360を-180~180に
    if abs(delta_alt) > fov/2 or abs(delta_az) > fov/2:
        return None
    # スクリーン座標化
    x = (delta_az + fov/2) / fov * width
    y = (fov/2 - delta_alt) / fov * height
    return x, y

@app.route("/get_stars")
def get_stars():
    try:
        # --- パラメータ ---
        lat = float(request.args.get("lat", 35.6))
        lon = float(request.args.get("lon", 139.7))
        az_center = float(request.args.get("azimuth", 180))
        alt_center = float(request.args.get("altitude", 45))
        fov = float(request.args.get("fov", 60))  # 視野角
        width = 240
        height = 240

        # --- 観測地と時刻 ---
        location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
        now = Time.now()
        altaz_frame = AltAz(obstime=now, location=location)

        # --- 星を変換 ---
        visible_stars = []
        hip_map = {}
        for star in stars_data:
            ra = star.get("r", 0)
            dec = star.get("d", 0)
            hip = star.get("h", None)
            name = star.get("n", "")
            mag = star.get("m", 5)

            # RA/Dec → Alt/Az
            coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg)
            altaz = coord.transform_to(altaz_frame)
            alt = altaz.alt.deg
            az = altaz.az.deg

            pos = sky_to_screen(alt, az, alt_center, az_center, fov, width, height)
            if pos is None:
                continue

            x, y = pos
            star_entry = {
                "x": x, "y": y,
                "size": mag_to_size(mag),
                "name": name, "mag": mag, "hip": hip
            }
            visible_stars.append(star_entry)
            if hip is not None:
                hip_map[hip] = star_entry

        # --- 星座線 ---
        visible_lines = []
        for line in lines_data:
            hip1 = line.get("from")
            hip2 = line.get("to")
            if hip1 in hip_map and hip2 in hip_map:
                s1 = hip_map[hip1]
                s2 = hip_map[hip2]
                visible_lines.append({
                    "x1": s1["x"], "y1": s1["y"],
                    "x2": s2["x"], "y2": s2["y"]
                })

        return jsonify({"stars": visible_stars, "lines": visible_lines})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
