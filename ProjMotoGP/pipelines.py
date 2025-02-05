# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
import ProjMotoGP.items
import pymongo
from elasticsearch import Elasticsearch

# Pour notre projet nous avons choisis de scrapper nos données que à partir des années 2000 au lieu du début en 1949
class FilterSeasonsPipeline:
    def process_item(self, item, spider):
        # Vérifier si l'objet est de type `Season`
        if isinstance(item, ProjMotoGP.items.Season):
            if item['year'] >= 2000:
                return item  # Laisser passer l'élément
            else:
                raise scrapy.exceptions.DropItem(f"Season year {item['year']} is less than 2000")
        else:
            # Si ce n'est pas un `Season`, passer à la prochaine pipeline
            return item

# Pour notre projet nous avons choisis de scrapper nos données que à partir des années 2000 au lieu du début en 1949
class FilterCategoriesPipeline:
    def __init__(self):
        self.seen_categories = set()

    def process_item(self, item, spider):
        # Vérifier si l'objet est de type `Categorie`
        if isinstance(item, ProjMotoGP.items.Categorie):
            category_id = item.get('id', None)
            category_name = item.get('name', None)

            # Vérifier si la catégorie est dans les noms autorisés
            if category_name not in ["MotoGP", "500cc"]:
                raise scrapy.exceptions.DropItem(f"Category {category_name} is not MotoGP or 500cc")

            # Vérifier si l'ID est un doublon
            if category_id in self.seen_categories:
                raise scrapy.exceptions.DropItem(f"Duplicate category found: {category_id}")
            else:
                self.seen_categories.add(category_id)
                return item

        # Si ce n'est pas un `Categorie`, passer à la prochaine pipeline
        return item

class RetiredStatusPipeline:
    def process_item(self, item, spider):
        if isinstance(item, ProjMotoGP.items.Rider):
            # Debugging - Afficher la valeur de season_team pour vérifier la structure
            print(f"season_team: {item.get('season_team')}")  # Affiche la saison de l'équipe

            # Vérifier si la saison 2025 est présente dans season_team
            if 2025 in item.get('season_team', {}):  # Si '2025' est une clé dans le dictionnaire
                print("Saison 2025 trouvée, modification de retired et retired_year")
                item['retired'] = False
                item['retired_year'] = None  # Ou utiliser None si tu utilises MongoDB
            else:
                print("Saison 2025 NON trouvée.")

            return item
        
        # Passer à la prochaine pipeline si ce n'est pas un 'Rider'
        return item

class MongoPipeline(object):
    def open_spider(self, spider):
        # Connecter au serveur MongoDB
        self.client = pymongo.MongoClient()
        # Définir la base de données
        self.db = self.client["ProjMotoGP"]

    def close_spider(self, spider):
        # Fermer la connexion à MongoDB
        self.client.close()

    def process_item(self, item, spider):
        # Utiliser le nom du spider comme nom de collection
        collection_name = spider.name  # Chaque spider aura sa propre collection
        # Utilisation de l'id de l'item comme _id pour éviter la génération automatique de MongoDB
        item_dict = dict(item)
        item_id = item_dict.get('id')  # Remplacez 'id' par le champ ID de votre item spécifique
        # Traiter le champ 'season_team' pour s'assurer que les clés sont des chaînes
        if 'season_team' in item_dict:
            # Convertir toutes les clés en chaînes
            item_dict['season_team'] = {
                str(key): value for key, value in item_dict['season_team'].items()
            }

        # Traiter le champ 'riders_team' pour s'assurer que les clés sont des chaînes
        if 'riders_team' in item_dict:
            # Convertir toutes les clés en chaînes
            item_dict['riders_team'] = {
                str(key): value for key, value in item_dict['riders_team'].items()
            }

        if item_id:
            # Supprimer le champ 'id' pour ne conserver que l'ID généré par MongoDB
            item_dict.pop('id', None)
            # Insérer le document en utilisant l'ID existant comme _id
            self.db[collection_name].replace_one({'_id': item_id}, item_dict, upsert=True)
        else:
            # Si l'ID n'est pas spécifié, laissez MongoDB en générer un pour l'item
            self.db[collection_name].insert_one(item_dict)

        return item
    
class ElasticsearchPipeline:
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")

    def process_item(self, item, spider):
        index_name = spider.name
        document = dict(item)
        self.es.index(index=index_name, id=item['id'], body=document)
        return item