import pandas as pd
from pathlib import Path
from plotnine import ggplot, aes, geom_col, theme, element_text, labs, facet_wrap
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"

data_csv = DATA_DIR / "openfoodfacts_categories_clean.csv"
df = pd.read_csv(data_csv, sep="\t")

df_exchange = df[df['manufacturing_places_normalized'] != df['product_origin_normalized']].copy()

print(f"Produits avec commerce international: {len(df_exchange)}")
print(f"Produits locaux (même pays): {len(df) - len(df_exchange)}")


exports_cat = df_exchange.groupby(['manufacturing_places_normalized', 'categories_normalized']).size().reset_index(name='count')

country_totals = exports_cat.groupby('manufacturing_places_normalized')['count'].transform('sum')
exports_cat['percentage'] = (exports_cat['count'] / country_totals) * 100

# 10 première catégories
top_categories = df_exchange['categories_normalized'].value_counts().head(10).index.tolist()

# catégorie otherpour le reste
exports_cat['category_grouped'] = exports_cat['categories_normalized'].apply(
    lambda x: x if x in top_categories else 'Other'
)

# Recalculer les pourcentages après regroupement
exports_final = exports_cat.groupby(['manufacturing_places_normalized', 'category_grouped'])['percentage'].sum().reset_index()


imports_cat = df_exchange.groupby(['product_origin_normalized', 'categories_normalized']).size().reset_index(name='count')

country_totals_import = imports_cat.groupby('product_origin_normalized')['count'].transform('sum')
imports_cat['percentage'] = (imports_cat['count'] / country_totals_import) * 100

imports_cat['category_grouped'] = imports_cat['categories_normalized'].apply(
    lambda x: x if x in top_categories else 'Other'
)

# Recalculer les pourcentages après regroupement
imports_final = imports_cat.groupby(['product_origin_normalized', 'category_grouped'])['percentage'].sum().reset_index()


# 15 pays exportateurs et importateurs
top_exporters = exports_cat.groupby('manufacturing_places_normalized')['count'].sum().sort_values(ascending=False).head(15).index
top_importers = imports_cat.groupby('product_origin_normalized')['count'].sum().sort_values(ascending=False).head(15).index

# mêmes pays dans les deux graphiques
common_countries = sorted(set(top_exporters) | set(top_importers))[:15]

# filtrer les données
exports_final = exports_final[exports_final['manufacturing_places_normalized'].isin(common_countries)].copy()
imports_final = imports_final[imports_final['product_origin_normalized'].isin(common_countries)].copy()

exports_final = exports_final.rename(columns={'manufacturing_places_normalized': 'pays'})
imports_final = imports_final.rename(columns={'product_origin_normalized': 'pays'})

exports_final['type'] = 'Exportations'
imports_final['type'] = 'Importations'

combined_df = pd.concat([exports_final, imports_final], ignore_index=True)

print(f"\nNombre de pays affichés: {len(common_countries)}")
print(f"Catégories affichées: {top_categories + ['Other']}")

graph_combined = (
    ggplot(combined_df, aes(x='pays', y='percentage', fill='category_grouped'))
    + geom_col(position='stack')
    + facet_wrap('~type', ncol=2)
    + labs(
        title='Distribution des catégories par pays: Exportations vs Importations (en %)',
        x='Pays',
        y='Pourcentage (%)',
        fill='Catégorie'
    )
    + theme(
        axis_text_x=element_text(rotation=90, ha='right', size=7),
        figure_size=(24, 8),
        legend_position='right'
    )
)

output_combined = RESULTS_DIR / "import_export.png"
graph_combined.save(output_combined, dpi=300)

