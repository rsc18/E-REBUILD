import sys
import pandas as pd

csv_fn = sys.argv[1]

df = pd.read_csv(csv_fn, header=0)

score_keys = ["premath", "postmath_adjusted"]

pre_avg, pre_std = df["premath"].mean(), df["premath"].std()
post_avg, post_std = df["postmath_adjusted"].mean(), df["postmath_adjusted"].std()

# Categorize the scores
for idx, row in df.iterrows():
    if row["premath"] < pre_avg - pre_std:
        pre_cat = "Low"
    elif row["premath"] > pre_avg + pre_std:
        pre_cat = "High"
    else:
        pre_cat = "Medium"

    if row["postmath_adjusted"] < pre_avg - pre_std:
        post_cat = "Low"
    elif row["postmath_adjusted"] > pre_avg + pre_std:
        post_cat = "High"
    else:
        post_cat = "Medium"

    print(f"{row['firstname']},{pre_cat},{post_cat}")

