import scrapy
from scrapy import Request
import json
from .. items import Categorie
from pathlib import Path

class CategoriesSpider(scrapy.Spider):
    name = "categories"
    allowed_domains = ["api.pulselive.motogp.com"]

    def start_requests(self):
        # Charger le fichier seasons.json
        seasons_file = Path(__file__).parent.parent.parent / "seasons.json"
        with open(seasons_file, "r") as f:
            seasons = json.load(f)

        # Parcourir les IDs des saisons pour générer les URLs
        base_url = "https://api.pulselive.motogp.com/motogp/v1/categories"

        # Concaténer une nouvelle url pour scrapper les pilotes sur celle-ci
        for season in seasons:
            url = f"{base_url}?seasonYear={season["year"]}"
            # Passer une request sur la nouvelle url et un callback qui appellera `parse`
            yield Request(
                url,
                callback=self.parse
            )

    def parse(self, response):
        # Parser la réponse de l'API initiale
        data_categories_details = json.loads(response.text)
        
        # Récupérer les données des saisons
        for categories in data_categories_details:
            id = categories.get("id", "N/A")
            name = categories.get("name", "N/A")

            # On peut maintenant envoyer les données combinées dans un seul `yield`
            yield Categorie(
                id = id,
                name = name
            )