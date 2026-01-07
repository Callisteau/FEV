import pandas as pd
from plotnine import ggplot, aes, geom_col, theme, element_text
from countries import normalize_countries_batch

data_csv = "openfoodfacts_en_clean_filtered.csv"
df = pd.read_csv(data_csv, sep="\t")

df = df[["product_origin", "sugars_100g"]]
df = df.dropna(subset=["product_origin"])

df['product_origin_normalized'] = normalize_countries_batch(df['product_origin'])

# Grouper par origine normalisée
df_grouped = df.groupby("product_origin_normalized", as_index=False).agg(
    sugars_100g=('sugars_100g', 'mean'),
    count=('sugars_100g', 'count')
)
df_grouped = df_grouped.rename(columns={'product_origin_normalized': 'product_origin'})

# Trier par moyenne de sucre pour un meilleur visuel
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

graph.save("myplot.png", dpi=600)