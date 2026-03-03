from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# 星データをロード
with open("stars_mag4_light.json", "r", encoding="utf-8") as f:
    stars = json.load(f)

# 星座線データをロード
with open("constellation_lines.json", "r", encoding="utf-8") as f:
    lines = json.load(f)

# 画面サイズ・星サイズ範囲・等級範囲
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
SIZE_MIN = 0.1
SIZE_MAX = 2.0
MAG_MIN = 1.0  # 明るい星
MAG_MAX = 6.0  # 暗い星

def ra_dec_to_screen(ra, dec, center_ra, center_dec, fov):
    """
    RA/Dec を簡易スクリーン座標に変換
    ra, dec, center_ra, center_dec, fov は全て度
    x=0~320, y=0~240
    """
    dx = ra - center_ra
    dy = dec - center_dec

    # 360度ラップ
    if dx > 180:
        dx -= 360
    elif dx < -180:
        dx += 360

    # 視野角チェック
    if abs(dx) > fov/2 or abs(dy) > fov/2:
        return None

    x = ((dx / (fov/2)) + 1) * (SCREEN_WIDTH/2)
    y = ((-dy / (fov/2)) + 1) * (SCREEN_HEIGHT/2)
    x = max(0, min(SCREEN_WIDTH, x))
    y = max(0, min(SCREEN_HEIGHT, y))
    return x, y

def mag_to_size(mag):
    """等級を 0.1~2 に変換"""
    if mag < MAG_MIN: mag = MAG_MIN
    if mag > MAG_MAX: mag = MAG_MAX
    size = SIZE_MAX - (mag - MAG_MIN) / (MAG_MAX - MAG_MIN) * (SIZE_MAX - SIZE_MIN)
    return round(size, 2)

@app.route("/get_stars")
def get_stars():
    try:
        center_ra = float(request.args.get("azimuth"))   # 中心RAをazimuthで指定
        center_dec = float(request.args.get("altitude")) # 中心Decをaltitudeで指定
        fov = float(request.args.get("fov"))
    except:
        return jsonify({"error": "invalid parameters"}), 400

    # 視野内の星を抽出
    visible_stars = []
    for star in stars:
        ra = star.get("r")
        dec = star.get("d")
        pos = ra_dec_to_screen(ra, dec, center_ra, center_dec, fov)
        if pos is None:
            continue
        x, y = pos
        visible_stars.append({
            "x": x,
            "y": y,
            "size": mag_to_size(star.get("m", 5)),
            "name": star.get("n", ""),
            "id": star.get("h")
        })

    # サイズ順にソートして上位 20 個
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
