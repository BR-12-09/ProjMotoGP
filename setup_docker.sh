#!/bin/bash

set -e  # Arrête le script immédiatement en cas d'erreur

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

echo "✅ Setup terminé avec succès !"