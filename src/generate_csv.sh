#!/bin/bash

set -e

echo "Etape 1/3: Parsing du fichier parquet"
python preprocessing/parse.py

echo "Etape 2/3: Filtrage des donnees"
python -c "
import pandas as pd
from pathlib import Path

BASE_DIR = Path.cwd().parent
DATA_DIR = BASE_DIR / 'data'

df = pd.read_csv(DATA_DIR / 'openfoodfacts_en_clean.csv', sep='\t')
df_filtered = df.dropna(subset=['sugars_100g', 'product_name_clean'])
df_filtered.to_csv(DATA_DIR / 'openfoodfacts_en_clean_filtered.csv', sep='\t', index=False)
print(f'{len(df_filtered)} lignes sauvegardees')
"

echo "Etape 3/3: Nettoyage des categories"
python preprocessing/clean_categorie.py

echo "Tous les fichiers CSV ont ete generes dans data"
