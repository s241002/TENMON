import csv
import json

INPUT_CSV = "bright_star_catalog.csv"
OUTPUT_JSON = "stars.json"

MAX_MAG = 4.0

stars = []

def ra_hours_to_deg(ra_hours):
    return float(ra_hours) * 15.0

with open(INPUT_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            mag = float(row["vmag"])
        except:
            continue

        if mag <= MAX_MAG:
            # 星名が無い場合はバイエル名を使う
            name = row.get("proper_name") or row.get("bayer") or row.get("hr")

            if not name:
                continue

            try:
                ra_deg = ra_hours_to_deg(row["ra_hours"])
                dec_deg = float(row["dec_deg"])
            except:
                continue

            stars.append({
                "n": name.strip(),
                "ra": round(ra_deg, 6),
                "dec": round(dec_deg, 6),
                "mag": round(mag, 2),
                "c": row.get("constellation", "").strip()
            })

# 明るい順にソート
stars.sort(key=lambda x: x["mag"])

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(stars, f, ensure_ascii=False)

print("生成完了:", len(stars), "stars")
