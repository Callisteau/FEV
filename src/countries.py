import pandas as pd
import spacy
import pycountry

nlp = spacy.load("en_core_web_sm")

manual_map = {
    "Estados Unidos de América": "United States",
    "Estados Unidos": "United States",
    "Atlanta": "United States",
    "USA": "United States",
    "Hanover": "United States",
    "Medley": "United States",
    "Lakeville": "United States",
    "México": "Mexico",
    "Wietnam": "Vietnam",
    "Kanakpura": "India",
    "UK": "United Kingdom",
    "Spain": "European Union", # a voir
    "EU": "European Union",
    "purchase": "United States",
    "Pays-Bas": "Netherlands",
    "Dubai": "Arab Emirates",
    "Veghel": "Netherlands"
}

def normalize_to_country(text):
    if not text or pd.isna(text):
        return None
    
    text = str(text).strip()
    
    # 1. Dictionnaire manuel
    if text in manual_map:
        return manual_map[text]

    # 2. Normalisation simple
    clean = text.replace("_", " ").replace("/", " ")

    # 3. Fuzzy search pycountry
    try:
        country = pycountry.countries.search_fuzzy(clean)[0]
        return country.name
    except Exception:
        return None


def normalize_countries_batch(origin_series):
    unique_origins = origin_series.dropna().unique()
    cache = {}
    
    print(f"Traitement de {len(unique_origins)} origines uniques avec spaCy...")
    
    # Pre-normalisation des virgules pour spaCy
    cleaned_origins = [o.replace(",", ", ") for o in unique_origins]
    
    for origin_text, doc in zip(unique_origins, nlp.pipe(cleaned_origins, batch_size=200)):

        # Entités géographiques
        entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "NORP"]]

        if not entities:
            entities = [p.strip() for p in origin_text.replace(",", ", ").split(",")]

        normalized = None

        # Tester de la plus spécifique à la plus large
        for ent in reversed(entities):
            normalized = normalize_to_country(ent)
            if normalized:
                break

        if not normalized:
            normalized = normalize_to_country(origin_text)

        cache[origin_text] = normalized
    
    print("Pays reconnus :", sum(v is not None for v in cache.values()))
    return origin_series.map(lambda x: cache.get(x, None) if pd.notna(x) else None)
