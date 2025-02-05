from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

if es.ping():
    print("Connexion à Elasticsearch réussie!")
else:
    print("Erreur de connexion à Elasticsearch.")
