#!/bin/bash

set -e  # Arrête le script immédiatement en cas d'erreur

# Lancer les spiders Scrapy un par un et s'assurer que chaque scrape est terminé avant de passer au suivant
echo "🔹 Lancement des spiders Scrapy..."

scrapy crawl seasons -o seasons.json || { echo "❌ Erreur lors de l'exécution de 'seasons'."; exit 1; }
echo "✅ Scrapy 'seasons' terminé."

scrapy crawl categories -o categories.json || { echo "❌ Erreur lors de l'exécution de 'categories'."; exit 1; }
echo "✅ Scrapy 'categories' terminé."

scrapy crawl categoriestm -o ctegoriestm.json || { echo "❌ Erreur lors de l'exécution de 'categoriestm'."; exit 1; }
echo "✅ Scrapy 'categoriestm' terminé."

scrapy crawl riders -o riders.json || { echo "❌ Erreur lors de l'exécution de 'riders'."; exit 1; }
echo "✅ Scrapy 'riders' terminé."

scrapy crawl teams -o teams.json || { echo "❌ Erreur lors de l'exécution de 'teams'."; exit 1; }
echo "✅ Scrapy 'teams' terminé."

# Lancer l'application Flask uniquement si tout le reste a réussi
echo "🔹 Démarrage de l'application Flask..."
python app.py || { echo "❌ Erreur lors du démarrage de l'application."; exit 1; }

echo "✅ Setup terminé avec succès !"