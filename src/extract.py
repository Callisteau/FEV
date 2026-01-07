import pandas as pd

input_csv = "openfoodfacts_en_clean.csv"
output_csv = "openfoodfacts_en_clean_filtered.csv"

def filter_origin_places():
    df = pd.read_csv(input_csv, sep="\t")

    print("Initial len :", len(df))

    df_clean = df[~(df["manufacturing_places"].isna())]
    df_clean.to_csv(output_csv, sep="\t", index=False)

    print("Final len:", len(df_clean))
    

filter_origin_places()

def extract_product_name(name):
    df = pd.read_csv(output_csv, sep="\t")
    name_lower = name.lower()
    df_filtered = df[df["product_name_clean"].astype(str).str.lower() == name_lower]
    output = "openfoodfacts_" + name + ".csv"
    df_filtered.to_csv(output, sep="\t", index=False)
 
extract_product_name("oreo")

