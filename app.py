from flask import Flask, request, jsonify
import json
import math

app = Flask(__name__)

# 星データをロード
with open("stars_mag4_light.json", "r", encoding="utf-8") as f:
    stars = json.load(f)

# 星座線データをロード
with open("constellation_lines.json", "r", encoding="utf-8") as f:
    lines = json.load(f)

# スクリーン変換（簡易版）
def sky_to_screen(az, alt, center_az, center_alt, fov):
    """
    az, alt, center_az, center_alt, fov は全て度
    """
    # 視野の中心との差
    dx = az - center_az
    dy = alt - center_alt

    # 360度ラップ調整
    if dx > 180:
        dx -= 360
    elif dx < -180:
        dx += 360

    # 視野角フィルタ
    if abs(dx) > fov/2 or abs(dy) > fov/2:
        return None

    # 正規化座標 -1~1
    x = dx / (fov/2)
    y = dy / (fov/2)
    return x, y

@app.route("/get_stars")
def get_stars():
    try:
        center_az = float(request.args.get("azimuth"))
        center_alt = float(request.args.get("altitude"))
        fov = float(request.args.get("fov"))
    except:
        return jsonify({"error": "invalid parameters"}), 400

    # 視野内の星を取得
    visible_stars = []
    for star in stars:
        az = star.get("az")  # ここは az/alt を事前に入れておくと簡単
        alt = star.get("alt")
        if az is None or alt is None:
            continue
        pos = sky_to_screen(az, alt, center_az, center_alt, fov)
        if pos is None:
            continue
        x, y = pos
        visible_stars.append({
            "x": x,
            "y": y,
            "mag": star.get("mag", 5),
            "name": star.get("name", "")
        })

    # 等級順にソートして上位20個
    visible_stars.sort(key=lambda s: s["mag"])
    visible_stars = visible_stars[:20]

    # 星座線フィルタ
    visible_lines = []
    star_ids_in_view = {s.get("id") for s in visible_stars if "id" in s}
    for line in lines:
        if line.get("from") in star_ids_in_view and line.get("to") in star_ids_in_view:
            visible_lines.append(line)

    return jsonify({"stars": visible_stars, "lines": visible_lines})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
