from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# 星データをロード
with open("stars_mag4_light.json", "r", encoding="utf-8") as f:
    stars = json.load(f)

# 星座線データをロード
with open("constellation_lines.json", "r", encoding="utf-8") as f:
    lines = json.load(f)

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
SIZE_MIN = 0.1
SIZE_MAX = 2.0
MAG_MIN = 1.0  # 最大等級(明るい)
MAG_MAX = 6.0  # 最小等級(暗い)

def sky_to_screen(az, alt, center_az, center_alt, fov):
    """
    az, alt, center_az, center_alt, fov は全て度
    スクリーン座標 x=0~320, y=0~240
    """
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

    # スクリーン座標に変換
    x = ((dx / (fov/2)) + 1) * (SCREEN_WIDTH/2)
    y = ((-dy / (fov/2)) + 1) * (SCREEN_HEIGHT/2)
    # 座標クリップ
    x = max(0, min(SCREEN_WIDTH, x))
    y = max(0, min(SCREEN_HEIGHT, y))
    return x, y

def mag_to_size(mag):
    """等級を 0.1~2 に変換"""
    # 明るい星は大きく、暗い星は小さく
    if mag < MAG_MIN: mag = MAG_MIN
    if mag > MAG_MAX: mag = MAG_MAX
    size = SIZE_MAX - (mag - MAG_MIN) / (MAG_MAX - MAG_MIN) * (SIZE_MAX - SIZE_MIN)
    return round(size, 2)

@app.route("/get_stars")
def get_stars():
    try:
        center_az = float(request.args.get("azimuth"))
        center_alt = float(request.args.get("altitude"))
        fov = float(request.args.get("fov"))
    except:
        return jsonify({"error": "invalid parameters"}), 400

    visible_stars = []
    for star in stars:
        az = star.get("az")
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
            "size": mag_to_size(star.get("mag", 5)),
            "name": star.get("name", ""),
            "id": star.get("id")
        })

    # 等級順にソートして上位 20 個
    visible_stars.sort(key=lambda s: s["size"], reverse=True)
    visible_stars = visible_stars[:20]

    # 星座線は視野内の星だけ
    visible_ids = {s["id"] for s in visible_stars if s.get("id") is not None}
    visible_lines = []
    for line in lines:
        if line.get("from") in visible_ids and line.get("to") in visible_ids:
            visible_lines.append(line)

    return jsonify({"stars": visible_stars, "lines": visible_lines})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
