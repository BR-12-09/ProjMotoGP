#!/bin/bash

set -e  # Arrête le script immédiatement en cas d'erreur

echo "🚀 Démarrage du setup..."

# Activer l'environnement virtuel
echo "🔹 Activation de l'environnement virtuel..."
pipenv shell

echo "✅ Setup Environnement terminé avec succès !"