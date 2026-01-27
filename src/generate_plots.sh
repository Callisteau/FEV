#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Étape 1/4 : Distribution des catégories par pays"
python "$SCRIPT_DIR/visualization/plot_categorie.py"

echo ""
echo "Étape 2/4 : Taux de sucres par pays"
python "$SCRIPT_DIR/visualization/plot_sugar.py"

echo ""
echo "Étape 3/4 : Exportations vs importations"
python "$SCRIPT_DIR/visualization/import_export.py"

echo ""
echo "Étape 4/4 : Ecart de teneur en sucre"
python "$SCRIPT_DIR/visualization/boxplot.py"
echo ""
echo "Toutes les visualisations ont été générées dans data/results"
