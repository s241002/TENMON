from flask import Flask, request, jsonify
import json
import math

app = Flask(__name__)

# 星データと星座線データを読み込む
with open("stars_mag4_light.json", "r", encoding="utf-8") as f:
    stars_data = json.load(f)

with open("constellation_lines.json", "r", encoding="utf-8") as f:
    lines_data = json.load(f)

# 赤経/赤緯 → 画面座標に変換
def sky_to_screen(ra, dec, azimuth, altitude, fov, width=320, height=240):
    """
    ra, dec: 星の赤経・赤緯（度）
    azimuth, altitude: 視点方向（度）
    fov: 視野角（度）
    width, height: 画面サイズ
    """
    # 視野内か判定（簡易）
    dx = ra - azimuth
    dy = dec - altitude
    if dx < -180: dx += 360
    if dx > 180: dx -= 360

    if abs(dx) > fov/2 or abs(dy) > fov/2:
        return None  # 視野外

    # 画面座標に変換
    x = (dx / fov + 0.5) * width
    y = (-dy / fov + 0.5) * height
    return int(x), int(y)

# 星の大きさ（等級→サイズ）変換
def mag_to_size(mag):
    # 0〜5等でサイズ1〜5
    return max(1, int(6 - mag))

@app.route("/get_stars")
def get_stars():
    # URLパラメータ取得
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
        azimuth = float(request.args.get("azimuth", 0))
        altitude = float(request.args.get("altitude", 0))
        fov = float(request.args.get("fov", 60))
    except:
        return jsonify({"error": "invalid parameters"}), 400

    # 視野内の星を抽出
    visible_stars = []
    for star in stars_data:
        ra = star.get("ra")
        dec = star.get("dec")
        name = star.get("name", "")
        mag = star.get("mag", 5)

        pos = sky_to_screen(ra, dec, azimuth, altitude, fov)
        if pos is None:
            continue

        x, y = pos
        size = mag_to_size(mag)
        visible_stars.append({"x": x, "y": y, "size": size, "name": name, "mag": mag})

    # 等級順にソートして上位20個
    visible_stars.sort(key=lambda s: s["mag"])
    visible_stars = visible_stars[:20]

    # 星座線の抽出
    visible_lines = []
    for line in lines_data:
        # 始点・終点の星名
        star1_name = line["start"]
        star2_name = line["end"]

        star1 = next((s for s in visible_stars if s["name"] == star1_name), None)
        star2 = next((s for s in visible_stars if s["name"] == star2_name), None)

        if star1 and star2:
            visible_lines.append({
                "x1": star1["x"], "y1": star1["y"],
                "x2": star2["x"], "y2": star2["y"]
            })

    # 返すJSON
    return jsonify({
        "stars": [{"x": s["x"], "y": s["y"], "size": s["size"], "name": s["name"]} for s in visible_stars],
        "lines": visible_lines
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
