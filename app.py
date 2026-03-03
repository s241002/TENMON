# app.py
import os
import json
from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# --- JSON ファイルを絶対パスで読み込む ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "stars_mag4_light.json"), "r", encoding="utf-8") as f:
    stars_data = json.load(f)

with open(os.path.join(BASE_DIR, "constellation_lines.json"), "r", encoding="utf-8") as f:
    lines_data = json.load(f)

# --- 星座線描画に使うサイズ変換関数 ---
def mag_to_size(mag):
    # 星の等級から描画サイズを決める（例）
    return max(1, int(6 - mag))  # 1～5 の範囲

# --- 赤経/赤緯からスクリーン座標へ変換（簡易版） ---
def sky_to_screen(ra, dec, azimuth, altitude, fov, width=240, height=240):
    try:
        dx = ra - azimuth
        dy = dec - altitude
        if abs(dx) > fov/2 or abs(dy) > fov/2:
            return None
        x = (dx + fov/2) / fov * width
        y = (fov/2 - dy) / fov * height
        return x, y
    except:
        return None

@app.route("/get_stars")
def get_stars():
    try:
        # --- パラメータ取得 ---
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
        azimuth = float(request.args.get("azimuth", 0))
        altitude = float(request.args.get("altitude", 0))
        fov = float(request.args.get("fov", 60))

        visible_stars = []
        for star in stars_data:
            ra = star.get("ra")
            dec = star.get("dec")
            hip = star.get("hip")
            name = star.get("name", "")
            mag = star.get("mag", 5)

            # None チェック
            if ra is None or dec is None or hip is None:
                continue

            pos = sky_to_screen(ra, dec, azimuth, altitude, fov)
            if pos is None:
                #continue
                pos = (120, 120)

            x, y = pos
            size = mag_to_size(mag)
            visible_stars.append({
                "x": x, "y": y, "size": size, "name": name, "mag": mag, "hip": hip
            })

        # 明るい順に並べて上位20個
        visible_stars.sort(key=lambda s: s["mag"])
        visible_stars = visible_stars[:20]

        # --- 星座線 ---
        visible_lines = []
        for line in lines_data:
            hip1 = line.get("from")
            hip2 = line.get("to")
            if hip1 is None or hip2 is None:
                continue

            star1 = next((s for s in visible_stars if s["hip"] == hip1), None)
            star2 = next((s for s in visible_stars if s["hip"] == hip2), None)
            if star1 and star2:
                visible_lines.append({
                    "x1": star1["x"], "y1": star1["y"],
                    "x2": star2["x"], "y2": star2["y"]
                })

        return jsonify({"stars": visible_stars, "lines": visible_lines})
        print(len(stars_data))
        print(stars_data[:5])

    except Exception as e:
        # エラー内容を返す
        return jsonify({"error": str(e)}), 500

# --- Render 用 ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
