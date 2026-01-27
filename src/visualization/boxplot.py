import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "data" / "results"


def load_all_results():

    frames = []

    for csv_file in RESULTS_DIR.glob("sugar_by_country_*.csv"):
        product = csv_file.stem.replace("sugar_by_country_", "")

        df = pd.read_csv(csv_file)
        df["product"] = product

        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def main(top_n_countries=6):

    df = load_all_results()

    # ---------------------------
    # 1️⃣ Countries with most coverage
    # ---------------------------
    country_counts = df["country"].value_counts()

    selected_countries = country_counts.head(top_n_countries).index

    df = df[df["country"].isin(selected_countries)]


    product_means = (
        df.groupby("product")["avg_sugars_100g"]
        .mean()
        .rename("product_mean")
    )

    df = df.merge(product_means, on="product")


    df["delta_vs_product"] = (
        df["avg_sugars_100g"] - df["product_mean"]
    )


    grouped = [
        df[df["country"] == c]["delta_vs_product"]
        for c in selected_countries
    ]

    plt.figure(figsize=(12, 7))

    plt.boxplot(grouped, tick_labels=selected_countries)

    plt.axhline(0, linestyle="--")
    plt.title("Écart de teneur en sucres par rapport à la moyenne du produit selon le pays")
    plt.xlabel("Pays")
    plt.ylabel("Différence de sucres par rapport à la moyenne du produit")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main(top_n_countries=6)
