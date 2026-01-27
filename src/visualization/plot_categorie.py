import pandas as pd
from pathlib import Path
from plotnine import ggplot, aes, geom_col, theme, element_text, labs, position_stack
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.countries import normalize_countries_batch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"

data_csv = DATA_DIR / "openfoodfacts_categories_clean.csv"
df = pd.read_csv(data_csv, sep="\t")

df = df[["product_origin", "categories_normalized"]]
df = df.dropna(subset=["product_origin", "categories_normalized"])

print(f"Normalisation des pays d'origine...")
df['product_origin_normalized'] = normalize_countries_batch(df['product_origin'])
df = df.dropna(subset=["product_origin_normalized"])

print(f"\nDonnées après nettoyage: {len(df)} lignes")

df_grouped = df.groupby(['product_origin_normalized', 'categories_normalized']).size().reset_index(name='count')

country_totals = df_grouped.groupby('product_origin_normalized')['count'].transform('sum')
df_grouped['percentage'] = (df_grouped['count'] / country_totals) * 100

top_categories = df['categories_normalized'].value_counts().head(10).index.tolist()

df_grouped['category_grouped'] = df_grouped['categories_normalized'].apply(
    lambda x: x if x in top_categories else 'Other'
)

# Recalculer les pourcentages après regroupement
df_final = df_grouped.groupby(['product_origin_normalized', 'category_grouped'])['percentage'].sum().reset_index()

# Trier les pays par nombre total de produits
country_order = df.groupby('product_origin_normalized').size().sort_values(ascending=False).index.tolist()

print(f"\nNombre de pays: {len(country_order)}")
print(f"Catégories affichées: {top_categories + ['Other']}")

graph = (
    ggplot(df_final, aes(x='product_origin_normalized', y='percentage', fill='category_grouped'))
    + geom_col(position='stack')
    + labs(
        title='Distribution des catégories par pays d\'origine (en %)',
        x='Pays d\'origine',
        y='Pourcentage (%)',
        fill='Catégorie'
    )
    + theme(
        axis_text_x=element_text(rotation=90, ha='right', size=6),
        figure_size=(24, 8),
        legend_position='right'
    )
)

output_file = RESULTS_DIR / "categories_by_country.png"
graph.save(output_file, dpi=600)


