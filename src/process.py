import pandas as pd
from plotnine import ggplot, aes, geom_col, theme, element_text
import spacy
import pycountry

data_csv = "openfoodfacts_en_clean_filtered.csv"

df = pd.read_csv(data_csv, sep="\t")
nlp = spacy.load("en_core_web_sm")

def normalize_to_country(text):
    """
    Convertit un texte (ville, région, pays) vers un nom de pays standardisé avec pycountry.
    """
    if not text or pd.isna(text):
        return None
    
    text = str(text).strip()
    
    # Essayer de trouver le pays avec pycountry (recherche floue)
    try:
        country = pycountry.countries.search_fuzzy(text)[0]
        return country.name
    except (LookupError, AttributeError):
        return None

def normalize_countries_batch(origin_series):
    """
    Normalise les noms de pays en utilisant spaCy pour extraire les entités géographiques
    et pycountry pour les convertir en noms de pays standardisés.
    Traitement optimisé par batch des valeurs uniques.
    """
    # Créer un cache pour les valeurs uniques
    unique_origins = origin_series.dropna().unique()
    cache = {}
    
    print(f"Traitement de {len(unique_origins)} origines uniques avec spaCy...")
    
    # Traiter par batch avec spaCy
    for doc in nlp.pipe(unique_origins, batch_size=200):
        origin_text = doc.text
        
        # Extraire toutes les entités géographiques (GPE = Geo-Political Entity, LOC = Location)
        gpe_entities = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        
        # Si pas d'entités, essayer de splitter par virgule
        if not gpe_entities:
            parts = [p.strip() for p in origin_text.split(',')]
            gpe_entities = parts
        
        # Essayer de convertir chaque entité en pays (en commençant par la dernière)
        normalized = None
        for entity in reversed(gpe_entities):
            country = normalize_to_country(entity)
            if country:
                normalized = country
                break
        
        # Si aucune entité n'a donné un pays valide, essayer le texte complet
        if normalized is None:
            normalized = normalize_to_country(origin_text)
        
        cache[origin_text] = normalized
    
    print(f"Normalisation terminée. Pays valides trouvés: {len([v for v in cache.values() if v is not None])}")
    
    # Mapper les résultats à toute la série
    return origin_series.map(lambda x: cache.get(x, None) if pd.notna(x) else None)

df = df[["product_origin", "sugars_100g"]]
df = df.dropna(subset=["product_origin"])

# print(f"Avant normalisation: {len(df['product_origin'].unique())} origines uniques")

# # Normaliser avec spaCy
# df['product_origin_normalized'] = normalize_countries_batch(df['product_origin'])

# print(f"Après normalisation: {len(df['product_origin_normalized'].unique())} origines uniques")

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