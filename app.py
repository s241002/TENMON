from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# 星データ読み込み
with open("stars_mag4_light.json", "r") as f:
    stars = json.load(f)

# 星座線データ読み込み
with open("constellation_lines.json", "r") as f:
    lines = json.load(f)

def sky_to_screen(ra100, dec100, center_az, center_alt, fov):
    # r,dは100倍されている
    ra = ra100 / 100
    dec = dec100 / 100
    dx = ra - center_az
    dy = dec - center_alt
    half_fov = fov / 2
    x = dx / half_fov
    y = dy / half_fov
    # -1..1 の範囲だけ表示
    if abs(x) > 1 or abs(y) > 1:
        return None
    return {"x": x, "y": y}

@app.route("/get_stars")
def get_stars():
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
        azimuth = float(request.args.get("azimuth", 0))
        altitude = float(request.args.get("altitude", 0))
        fov = float(request.args.get("fov", 60))
    except:
        return jsonify({"error":"invalid params"}), 400

    visible_stars = []
    for s in stars:
        pos = sky_to_screen(s["r"], s["d"], azimuth, altitude, fov)
        if pos:
            size = max(1, 5 - s["m"]/10)  # 適当にサイズ調整
            visible_stars.append({
                "x": pos["x"],
                "y": pos["y"],
                "size": size,
                "name": s.get("n","")
            })
    # 星座線も視野内のみ
    visible_lines = []
    for l in lines:
        start_star = next((s for s in visible_stars if s.get("h") == l["from"]), None)
        end_star = next((s for s in visible_stars if s.get("h") == l["to"]), None)
        if start_star and end_star:
            visible_lines.append({
                "start": {"x": start_star["x"], "y": start_star["y"]},
                "end": {"x": end_star["x"], "y": end_star["y"]}
            })

    return jsonify({"stars": visible_stars, "lines": visible_lines})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
