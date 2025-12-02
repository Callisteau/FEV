import pyarrow.parquet as pq
import pandas as pd
import numpy as np

parquet_file = pq.ParquetFile("data/food.parquet")

SUGAR_NAMES = {"sugar", "sugars", "glucose", "fructose", "sucrose"}

results = []   # we store all extracted rows here

for batch in parquet_file.iter_batches(columns=["product_name", "nutriments", "lang"], batch_size=200):
    df = batch.to_pandas()

    # Keep only French products
    df = df[df["lang"] == "fr"]

    # -------- Extract product text --------
    def extract_product_text(arr):
        if isinstance(arr, (list, np.ndarray)):
            for item in arr:
                if item.get("lang") == "main":
                    return item.get("text")
        return None

    df["product_text"] = df["product_name"].apply(extract_product_text)

    # -------- Extract sugar nutriment name --------
    def extract_sugar_name(arr):
        if isinstance(arr, (list, np.ndarray)):
            for item in arr:
                name = item.get("name", "").lower()
                if name in SUGAR_NAMES:
                    return name
        return None

    df["sugar_name"] = df["nutriments"].apply(extract_sugar_name)

    # -------- Extract sugar value 100g --------
    def extract_sugar_value(arr):
        if isinstance(arr, (list, np.ndarray)):
            for item in arr:
                name = item.get("name", "").lower()
                if name in SUGAR_NAMES:
                    return item.get("100g")
        return None

    df["sugar_100g"] = df["nutriments"].apply(extract_sugar_value)

    # Keep only entries where sugar exists
    filtered = df[df["sugar_name"].notnull()][["product_text", "sugar_name", "sugar_100g"]]

    results.append(filtered)

# -------- Combine all results --------
final_df = pd.concat(results, ignore_index=True)

# -------- Save to Parquet --------
final_df.to_parquet("data/sugar_products.parquet", index=False)

print("Saved to data/sugar_products.parquet")
print(final_df.head())
