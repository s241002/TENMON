from flask import Flask, request, jsonify

app = Flask(__name__)

# ⭐ 固定星データ（とりあえず30個ダミー）
STARS = [
    {"id": 0, "name": "Star0", "x": 50, "y": 40},
    {"id": 1, "name": "Star1", "x": 80, "y": 60},
    {"id": 2, "name": "Star2", "x": 120, "y": 90},
    {"id": 3, "name": "Star3", "x": 150, "y": 120},
    {"id": 4, "name": "Star4", "x": 180, "y": 140},
]

# 30個に増やす
for i in range(5, 30):
    STARS.append({
        "id": i,
        "name": f"Star{i}",
        "x": (i * 13) % 320,
        "y": (i * 17) % 240
    })


@app.route("/")
def home():
    return "Star API running"


@app.route("/stars")
def stars():
    return jsonify({
        "count": len(STARS),
        "stars": STARS
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
