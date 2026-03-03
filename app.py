# app.py
import os
import json
from flask import Flask, jsonify

app = Flask(__name__)

# --- JSON ファイルを絶対パスで読み込む ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
stars_file = os.path.join(BASE_DIR, "stars_mag4_light.json")
lines_file = os.path.join(BASE_DIR, "constellation_lines.json")

with open(stars_file, "r", encoding="utf-8") as f:
    stars_data = json.load(f)

with open(lines_file, "r", encoding="utf-8") as f:
    lines_data = json.load(f)

# --- デバッグ用：画面座標簡易計算 ---
def sky_to_screen_debug(ra, dec, width=240, height=240):
    # RA/Dec を 0-360 / -90~90 に正規化して画面座標に変換
    x = (ra % 360) / 360 * width
    y = (90 - dec) / 180 * height
    return x, y

# --- 星のサイズ（等級から） ---
def mag_to_size(mag):
    return max(1, int(6 - mag))  # 1~5 の範囲

@app.route("/get_stars")
def get_stars():
    try:
        # デバッグ用：すべての星を返す
        visible_stars = []
        hip_map = {}
        for star in stars_data:
            ra = star.get("r", 0)
            dec = star.get("d", 0)
            hip = star.get("h", None)
            name = star.get("n", "")
            mag = star.get("m", 5)

            x, y = sky_to_screen_debug(ra, dec)
            size = mag_to_size(mag)

            star_entry = {
                "x": x, "y": y, "size": size,
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
                star1 = hip_map[hip1]
                star2 = hip_map[hip2]
                visible_lines.append({
                    "x1": star1["x"], "y1": star1["y"],
                    "x2": star2["x"], "y2": star2["y"]
                })

        return jsonify({"stars": visible_stars, "lines": visible_lines})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
