import pandas as pd

input_csv = "openfoodfacts_en_clean.csv"
output_csv = "openfoodfacts_en_clean_filtered.csv"

def filter_origin_places():
    df = pd.read_csv(input_csv, sep="\t")

    print("Initial len :", len(df))

    df_clean = df[~(df["manufacturing_places"].isna())]
    df_clean.to_csv(output_csv, sep="\t", index=False)

    print("Final len:", len(df_clean))
    
    print(f"Cleaned CSV saved to: {output_csv}")


filter_origin_places()