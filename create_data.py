import pandas as pd

df = pd.read_csv("hip_mag4.csv")

# 座標が空の行を削除
df = df.dropna(subset=["_RA_icrs", "_DE_icrs"])

# 100倍整数化（軽量化）
df["RA"] = (df["_RA_icrs"] * 100).astype(int)
df["Dec"] = (df["_DE_icrs"] * 100).astype(int)

df = df[["HIP", "RA", "Dec", "Vmag"]]

df.to_json("stars_mag4_light.json", orient="records")
