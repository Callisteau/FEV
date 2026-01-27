import pandas as pd
import spacy
from pathlib import Path
from spacy.pipeline import EntityRuler
import re

# --------
# LOAD DATA
# --------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
data_dir = BASE_DIR / "data" 
data_csv = data_dir / f"openfoodfacts_en_clean_filtered.csv"
df = pd.read_csv(data_csv, sep="\t")

# -------------------------------------------
# 1) SPACY MODEL + ENTITY RULER (typos connues)
# -------------------------------------------
nlp = spacy.blank("en")

ruler = nlp.add_pipe("entity_ruler")

# Typos courantes et formes proches de "Skittles"
patterns = [
    {"label": "WHEY", "pattern": "WHEY"},
    {"label": "WHEY", "pattern": "Whey"},
]

ruler.add_patterns(patterns)

# -----------------------------------------------------------
# 2) Fuzzy regex pour capturer les variations non listées
# -----------------------------------------------------------
fuzzy_regex = r"wh[ei]y"

def detect_whey_regex(text):
    if pd.isna(text):
        return False
    return re.search(fuzzy_regex, text.lower()) is not None


# -----------------------------------------------------------
# 3) Application SpaCy + fuzzy regex
# -----------------------------------------------------------
def detect_whey_spacy(text):
    if pd.isna(text):
        return False
    doc = nlp(text)
    return any(ent.label_ == "WHEY" for ent in doc.ents)


df["has_whey_spacy"] = df["product_name_clean"].apply(detect_whey_spacy)
df["has_whey_regex"] = df["product_name_clean"].apply(detect_whey_regex)

# Combine both
df["has_whey"] = df["has_whey_spacy"] | df["has_whey_regex"]

df_whey = df[df["has_whey"]]
output_csv = data_dir / "openfoodfacts_whey.csv"
df_whey.to_csv(output_csv, sep="\t", index=False)

print("Produits whey détectés :", len(df_whey))
