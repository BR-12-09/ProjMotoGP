from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Configuration de la connexion MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/ProjMotoGP"  # Remplacez par l'URI de votre base de données Mongo
mongo = PyMongo(app)

# Connexion à Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Fonction de recherche
def search_riders(query):
    body = {
        "query": {
            "wildcard": {
                "name": {
                    "value": f"{query}*"  # Utilise un wildcard pour faire une recherche par préfixe
                }
            }
        }
    }
    result = es.search(index="riders", body=body)
    return result['hits']['hits']

# Route pour tester la connexion
@app.route('/')
def index():
    return render_template('acceuil.html')

@app.route('/riders')
def get_riders():
    riders = mongo.db.riders.find()  # Récupérer tous les documents de la collection 'riders'
    teams = mongo.db.teams.find()  # Récupérer tous les documents de la collection 'teams'
    return render_template('riders.html', riders=riders, teams=teams)

@app.route('/teams')
def get_teams():
    teams = mongo.db.teams.find()  # Récupérer tous les documents de la collection 'teams'
    riders = mongo.db.riders.find()  # Récupérer tous les documents de la collection 'riders'
    return render_template('teams.html', teams=teams, riders=riders)

@app.route('/recherche', methods=["GET", "POST"])
def get_recherche():
    if request.method == "POST":
        query = request.form["query"]
        riders = search_riders(query)  # Cherche les pilotes
        return render_template("recherche.html", riders=riders, query=query)
    return render_template("recherche.html", riders=[], query="")

@app.route('/<rider_id>')
def get_rider_details(rider_id):
    rider = mongo.db.riders.find_one({"_id": rider_id})  # Récupération du pilote depuis MongoDB
    if not rider:
        return "Pilote non trouvé", 404
    # Vérifier si une équipe existe pour ce pilote
    teams = mongo.db.teams.find()
    return render_template("rider_details.html", rider=rider, teams=teams)


if __name__ == '__main__':
    app.run(debug=True)
