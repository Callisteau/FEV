import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pandas as pd

SUGAR_NAMES = {"sugar", "sugars", "glucose", "fructose", "sucrose"}

def extract_product_origin_vectorized(df, column="manufacturing_places"):
    origins_list = df[column].tolist()

    return [
        origin.split(",")[0].strip() if isinstance(origin, str) else None
        for origin in origins_list
    ]


def extract_product_name_vectorized(df, column="product_name"):
    name_list = df[column].tolist()
    
    return [
        next((item["text"] for item in names if isinstance(item, dict) and item.get("lang")=="main"), None)
        if names is not None else None
        for names in name_list
    ]

def extract_nutriment_vectorized(df, column="nutriments", nutriment_name="sugars"):
    nutriments_list = df[column].tolist()
    
    return [
        next((n["100g"] for n in nutriments if n.get("name") == nutriment_name), None)
        if nutriments is not None else None
        for nutriments in nutriments_list
    ]

def process_openfoodfacts_parquet(parquet_path, output_csv, language_filter="en", batch_size=1024,columns=None,):


    dataset = ds.dataset(parquet_path, format="parquet")
    total_rows = dataset.count_rows()
    num_batches = (total_rows + batch_size - 1) // batch_size 

    print(f"Total rows : {total_rows}")
    print(f"Batch size : {batch_size}")
    print(f"Estimated number of batches : {num_batches}")
    batch_id = 0

    writer = None
    first_write = True

    for batch in dataset.to_batches(batch_size=batch_size):
        batch_id += 1
        print(f"\n Traitement batch #{batch_id} (taille: {batch.num_rows} lignes)")

        df = batch.to_pandas()
        if columns is not None:
            df = df[[c for c in columns if c in df.columns]]



        if "languages_codes" in df.columns:
            df = df[df["languages_codes"].str.contains(language_filter, na=False)]
        elif "lang" in df.columns:
            df = df[df["lang"] == language_filter]


        if df.empty:
            continue


        df["sugars_100g"] = extract_nutriment_vectorized(df, "nutriments", "sugars")
        df["carbohydrates_100g"] = extract_nutriment_vectorized(df, "nutriments", "carbohydrates")

        if "nutriments" in df.columns:
            df = df.drop(columns=["nutriments"])

        df["product_name_clean"] = extract_product_name_vectorized(df, "product_name")
        df["product_origin"] = extract_product_origin_vectorized(df, "manufacturing_places")
        df = df.drop(columns=["product_name"])
        df.to_csv(output_csv, mode="a", index=False, header=first_write,sep="\t")
        first_write = False
        #print(df.head())
        #break

if __name__ == "__main__":
    useful_columns = [
        "manufacturing_places",
        "product_name",
        "lang",
        "nutriments",
        "brands",
        "categories"
    ]
    process_openfoodfacts_parquet(
        parquet_path="data/food.parquet",
        output_csv="openfoodfacts_en_clean.csv",
        language_filter="en",
        columns=useful_columns
    )

    print("Traitement terminé : fichier généré-> openfoodfacts_en_clean.csv")
