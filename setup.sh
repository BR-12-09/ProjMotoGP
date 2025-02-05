#!/bin/bash

set -e  # Arrête le script immédiatement en cas d'erreur

echo "🚀 Démarrage du setup..."

# Activer l'environnement virtuel
echo "🔹 Activation de l'environnement virtuel..."
pipenv shell

# Installer les dépendances
echo "🔹 Installation des dépendances..."
pipenv install --dev || { echo "❌ Erreur lors de l'installation des dépendances."; exit 1; }

# Lancer Docker Compose et attendre son démarrage complet
echo "🔹 Démarrage des services Docker..."
docker-compose up -d || { echo "❌ Erreur lors du lancement de Docker Compose."; exit 1; }

# Attendre quelques secondes pour s'assurer que les services sont bien en place
echo "⏳ Attente de 10 secondes pour que les services démarrent..."
sleep 10  # Temps d'attente pour laisser MongoDB et Elasticsearch se lancer correctement

# Vérifier que les services sont bien en ligne avant de continuer
echo "🔹 Vérification des services Docker..."
docker ps || { echo "❌ Aucun service Docker en cours d'exécution."; exit 1; }

# Lancer les spiders Scrapy un par un et s'assurer que chaque scrape est terminé avant de passer au suivant
echo "🔹 Lancement des spiders Scrapy..."

scrapy crawl seasons || { echo "❌ Erreur lors de l'exécution de 'seasons'."; exit 1; }
echo "✅ Scrapy 'seasons' terminé."

scrapy crawl categories || { echo "❌ Erreur lors de l'exécution de 'categories'."; exit 1; }
echo "✅ Scrapy 'categories' terminé."

scrapy crawl categoriestm || { echo "❌ Erreur lors de l'exécution de 'categoriestm'."; exit 1; }
echo "✅ Scrapy 'categoriestm' terminé."

scrapy crawl riders || { echo "❌ Erreur lors de l'exécution de 'riders'."; exit 1; }
echo "✅ Scrapy 'riders' terminé."

scrapy crawl teams || { echo "❌ Erreur lors de l'exécution de 'teams'."; exit 1; }
echo "✅ Scrapy 'teams' terminé."

# Lancer l'application Flask uniquement si tout le reste a réussi
echo "🔹 Démarrage de l'application Flask..."
python app.py || { echo "❌ Erreur lors du démarrage de l'application."; exit 1; }

echo "✅ Setup terminé avec succès !"