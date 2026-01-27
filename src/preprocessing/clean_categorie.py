import pandas as pd
import spacy
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
sys.path.insert(0, str(BASE_DIR / "src"))
from utils.countries import normalize_countries_batch

nlp = spacy.load("en_core_web_sm")
data_csv = DATA_DIR / "openfoodfacts_en_clean_filtered.csv"

# Dictionnaire de traduction des catégories courantes
CATEGORY_TRANSLATIONS = {
    # Français
    'aliments et boissons à base de végétaux': 'plant-based foods and beverages',
    'aliments d\'origine végétale': 'plant-based foods',
    'aliments à base de plantes': 'plant-based foods',
    'boissons': 'beverages',
    'boissons et préparations de boissons': 'beverages',
    'snacks sucrés': 'sweet snacks',
    'viandes': 'meats',
    'viandes et dérivés': 'meats',
    'produits laitiers': 'dairy products',
    'fruits et légumes': 'fruits and vegetables',
    'céréales et pommes de terre': 'cereals and potatoes',
    'produits de la mer': 'seafood',
    'condiments': 'condiments',
    'desserts': 'desserts',
    # Espagnol
    'alimentos y bebidas de origen vegetal': 'plant-based foods and beverages',
    'bebidas': 'beverages',
    'bebidas y preparaciones de bebidas': 'beverages',
    'aperitivos': 'snacks',
    'botanas': 'snacks',
    'condimentos': 'condiments',
    # Allemand
    'pflanzliche lebensmittel und getränke': 'plant-based foods and beverages',
    'getränke': 'beverages',
    'fleisch': 'meats',
    'milchprodukte': 'dairy products',
    # Italien
    'cibi e bevande a base vegetale': 'plant-based foods and beverages',
    'bevande': 'beverages',
    'snack': 'snacks',
    'carni': 'meats',
    'latticini': 'dairy products',
    # Néerlandais
    'plantaardige levensmiddelen en dranken': 'plant-based foods and beverages',
    'plantaardige levensmiddelen': 'plant-based foods',
    'dranken': 'beverages',
    'snacks': 'snacks',
    'vlees': 'meats',
    'zuivelproducten': 'dairy products',
}

# Normalisation anglaise
ENGLISH_NORMALIZATION = {
    'plant-based foods and beverages': 'Plant-based foods',
    'plant-based foods': 'Plant-based foods',
    'beverages': 'Beverages',
    'Beverages': 'Beverages',
    'snacks': 'Snacks',
    'sweet snacks': 'Snacks',
    'meats': 'Meats',
    'meats and their products': 'Meats',
    'dairy products': 'Dairy products',
    'fruits and vegetables based foods': 'Fruits and vegetables',
    'cereals and potatoes': 'Cereals and potatoes',
    'seafood': 'Seafood',
    'fishes': 'Seafood',
}

def normalize_categories_batch(categories_series):
    unique_categories = categories_series.dropna().unique()
    cache = {}
    
    print(f"Traitement de {len(unique_categories)} catégories uniques...")
    
    for cat_text in unique_categories:
        cat_str = str(cat_text).strip()
        
        if cat_str.lower() in ['', 'null', 'nan']:
            cache[cat_text] = None
            continue
        
        parts = [p.strip() for p in cat_str.split(',')]
        valid_parts = []
        
        for part in parts:
            clean_part = part
            if ':' in part and len(part.split(':', 1)[0]) <= 3:
                clean_part = part.split(':', 1)[1].strip()
            
            if clean_part and not clean_part.lower().startswith('null'):
                valid_parts.append(clean_part)
        
        if valid_parts:
            category = valid_parts[0].strip().lower()
            
            if category in CATEGORY_TRANSLATIONS:
                category_en = CATEGORY_TRANSLATIONS[category]
            else:
                category_en = category
            
            if category_en in ENGLISH_NORMALIZATION:
                normalized = ENGLISH_NORMALIZATION[category_en]
            else:
                normalized = category_en.capitalize()
            
            cache[cat_text] = normalized
        else:
            cache[cat_text] = None
    
    print(f"Normalisation terminée. Catégories valides: {len([v for v in cache.values() if v is not None])}")
    
    return categories_series.map(lambda x: cache.get(x, None) if pd.notna(x) else None)

df = pd.read_csv(data_csv, sep="\t")

print("=" * 60)
print("NETTOYAGE DES CATEGORIES")
print("=" * 60)
print(f"Catégories uniques avant: {len(df['categories'].dropna().unique())}")

df['categories_normalized'] = normalize_categories_batch(df['categories'])
print(f"Catégories uniques après: {len(df['categories_normalized'].dropna().unique())}")

print("\nTop 30 catégories:")
print(df['categories_normalized'].value_counts().head(30))

print("\n" + "=" * 60)
print("NETTOYAGE DES PAYS D'ORIGINE")
print("=" * 60)
print(f"Origines uniques avant: {len(df['product_origin'].dropna().unique())}")

df['product_origin_normalized'] = normalize_countries_batch(df['product_origin'])
print(f"Pays uniques après: {len(df['product_origin_normalized'].dropna().unique())}")

print("\nTop 20 pays:")
print(df['product_origin_normalized'].value_counts().head(20))

print("\n" + "=" * 60)
print("NETTOYAGE DES LIEUX DE FABRICATION")
print("=" * 60)
print(f"Origines uniques avant: {len(df['manufacturing_places'].dropna().unique())}")

df['manufacturing_places_normalized'] = normalize_countries_batch(df['manufacturing_places'])
print(f"Pays uniques après: {len(df['manufacturing_places_normalized'].dropna().unique())}")

print("\nTop 20 pays:")
print(df['manufacturing_places_normalized'].value_counts().head(20))

print("\n" + "=" * 60)
print("FILTRAGE DES LIGNES")
print("=" * 60)
print(f"Nombre de lignes avant filtrage: {len(df)}")

df = df.dropna(subset=['product_origin_normalized', 'manufacturing_places_normalized', 'categories_normalized'])
print(f"Nombre de lignes après filtrage: {len(df)}")

output_csv = DATA_DIR / "openfoodfacts_categories_clean.csv"
df.to_csv(output_csv, sep="\t", index=False)
print(f"\nDonnées sauvegardées dans {output_csv}")
