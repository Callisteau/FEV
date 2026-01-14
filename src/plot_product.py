import matplotlib.pyplot as plt
import pandas as pd
import sys
from countries import normalize_countries_batch

def plot_sugar_by_country(product_name):
    """
    product_name = nom du fichier sans le prefixe 'openfoodfacts_' et sans extension
                   ex : 'snickers', 'pepsi', 'cocacola'
    """

    # 1. Construction dynamique du CSV
    data_csv = f"openfoodfacts_{product_name}.csv"

    # 2. Chargement des données
    df = pd.read_csv(data_csv, sep="\t")

    # 3. Normalisation des pays
    df["product_origin_normalized"] = normalize_countries_batch(df["product_origin"])

    # 4. Calcul de la moyenne des sucres
    sugar_by_country = (
        df.groupby("product_origin_normalized")["sugars_100g"]
        .mean()
        .sort_values(ascending=False)
    )

    # 5. Plot
    plt.figure(figsize=(12, 6))
    sugar_by_country.plot(kind="bar")

    plt.title(f"Taux de sucres (g/100g) des produits {product_name.capitalize()} par pays")
    plt.xlabel("Pays")
    plt.ylabel("Sucres (g / 100 g)")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 plot_product.py product_name")
        sys.exit(1)

    product = sys.argv[1]
    plot_sugar_by_country(product)
