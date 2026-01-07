import pandas as pd
from plotnine import ggplot, aes, geom_col, theme, element_text
import spacy
import pycountry

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
