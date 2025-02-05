# Projet MotoGP Data Scraper & Web App 🏍️

Ce projet permet de récupérer, stocker et afficher des données sur les pilotes et équipes de MotoGP en utilisant Scrapy, MongoDB, Elasticsearch, Flask et Docker.

## 📌 Fonctionnalités principales

Scraping des données de pilotes et équipes avec Scrapy

Stockage des données dans MongoDB

Recherche avancée des pilotes avec Elasticsearch

Interface web avec Flask

## 🚀 Installation et Lancement
 
### 1️⃣ Clonez le projet

git clone https://github.com/votre-repo/ProjMotoGP.git

cd ProjMotoGP

### 2️⃣ Installation de l'environnement

Lancer le fichier setup_environnement.sh avec la commande : 

./setup_environnement.sh

### 3️⃣ Installation des dépendances et les services (MongoDB + Elasticsearch)

Lancer le fichier setup_docker.sh avec la commande : 

./setup_docker.sh

### 4️⃣ Lancer le scraping des données et le démarrage de l'application Flask

Lancer le fichier setup_scrapping.sh avec la commande : 

./setup_scrapping.sh

L'application sera accessible à l'adresse : http://127.0.0.1:5000/

## ⚙️ Choix techniques

🛠 Technologies utilisées

### Python 3.13

Langage principal

### Flask

Serveur web pour l'interface utilisateur

### Scrapy

Scraping des données

### MongoDB

Base de données NoSQL

### Elasticsearch

Moteur de recherche avancé

### Docker

Conteneurisation de MongoDB et Elasticsearch

## 🏢 Pourquoi ces choix ?

Scrapy : Performant et flexible pour le web scraping

MongoDB : Stockage flexible des données des pilotes/équipes

Elasticsearch : Recherche rapide des pilotes avec autocomplétion

Flask : Simple et léger pour créer une API et une interface web

Docker : Facilité d’installation et d’exécution des services

## 🔥 Améliorations possibles

📊 Ajout de visualisations graphiques sur les statistiques des pilotes

🏃 Comparaison entre pilotes basée sur leurs performances
