#!/bin/bash

set -e

echo "Generation des visualisations"
echo ""

echo "1/3: Distribution des categories par pays"
python visualization/plot_categorie.py

echo ""
echo "2/3: Taux de sucres par pays"
python visualization/plot_sugar.py

echo ""
echo "3/3: Exportations vs Importations"
python visualization/import_export.py

echo ""
echo "Toutes les visualisations ont ete generees dans data/results/"
