import pandas as pd
from pathlib import Path
from plotnine import ggplot, aes, geom_col, theme, element_text
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.countries import normalize_countries_batch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"

data_csv = DATA_DIR / "openfoodfacts_en_clean_filtered.csv"
df = pd.read_csv(data_csv, sep="\t")

df = df[["product_origin", "sugars_100g"]]
df = df.dropna(subset=["product_origin"])

df['sugars_100g'] = pd.to_numeric(df['sugars_100g'], errors='coerce')
df = df.dropna(subset=["sugars_100g"])

df['product_origin_normalized'] = normalize_countries_batch(df['product_origin'])

df_grouped = df.groupby("product_origin_normalized", as_index=False).agg(
    sugars_100g=('sugars_100g', 'mean'),
    count=('sugars_100g', 'count')
)
df_grouped = df_grouped.rename(columns={'product_origin_normalized': 'product_origin'})

df_grouped = df_grouped.sort_values('sugars_100g')

print(f"Nombre de pays dans le graphique: {len(df_grouped)}")

graph = (
    ggplot(df_grouped)
    + aes(x="product_origin", y="sugars_100g")
    + geom_col()
    + theme(
        axis_text_x=element_text(rotation=90, ha="right", size=6),
        figure_size=(20, 8)
    )
)

output_file = RESULTS_DIR / "sugar_by_country.png"
graph.save(output_file, dpi=600)
