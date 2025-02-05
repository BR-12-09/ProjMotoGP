import scrapy
from scrapy import Request
import json
from ..items import Rider
from pathlib import Path

class RidersSpider(scrapy.Spider):
    name = "riders"
    # Liste des 2 sites que l'on veut scrapper un site HTML et une API car on veut récupérer le plus d'informations possibles
    allowed_domains = ["api.pulselive.motogp.com", "motogp.com"]

    def start_requests(self):
        # Charger le fichier seasons.json
        seasons_file = Path(__file__).parent.parent.parent / "seasons.json"
        with open(seasons_file, "r") as f:
            seasons = json.load(f)

        # Charger le fichier categories_TM.json
        categories_tm_file = Path(__file__).parent.parent.parent / "categoriestm.json"
        with open(categories_tm_file, "r") as f:
            categories_tm = json.load(f)

        # Liste pour stocker tous les IDs pilotes
        self.riders_uuids = []

        # URL dont on veut scraper les pilotes de 2025
        url_motogp_riders_2025 = "https://www.motogp.com/fr/riders/motogp"
        # Passer une request sur la nouvelle URL, un callback qui appellera `parse_riders_2025` et les données seasons et categories_TM qui vont nous servir pour le scrapping de la prochaine page l'API
        yield Request(url_motogp_riders_2025, callback=self.parse_riders_2025, meta={'seasons': seasons, 'categories_TM': categories_tm})

    def parse_riders_2025(self, response):
        # Scraping de la page HTML pour récupérer les IDs pilotes de 2025
        # Extraire les IDs des pilotes de 2025
        riders_html_uuids = response.css(".rider-grid__motogp.js-listing-container a::attr(data-rider-id)").getall()
        
        # Ajouter les IDs récupérés depuis la page web à la liste existante
        for rider_id in riders_html_uuids:
            if rider_id and rider_id not in self.riders_uuids:
                self.riders_uuids.append(rider_id)

        # URL dont on veut scraper tous les autres pilotes qui ont roulés en MotoGP depuis les années 2000
        base_url = "https://api.pulselive.motogp.com/motogp/v1/results/standings"
        # Récupérer les données déjà associées dans `meta` (les données envoyées avec `yield Request` dans la fonction `start_requests`)
        seasons = response.meta['seasons']
        categories_tm = response.meta['categories_TM']

        # Parcourir les IDs des saisons et de la catégorie_TM pour générer les URLs
        for season in seasons:
            for category in categories_tm:
                url = f"{base_url}?seasonUuid={season['id']}&categoryUuid={category['id']}"
                # Passer une request sur les nouvelles URLs et un callback qui appellera `parse` et les données seasons et categories_TM
                yield Request(url, callback=self.parse, meta={'seasons': seasons, 'categories_TM': categories_tm})

    def parse(self, response):
        # Parser la réponse de l'API initiale
        data = json.loads(response.text)

        # Récupérer les données déjà associées dans `meta` (les données envoyées avec `yield Request` dans la fonction `start_requests`)
        seasons = response.meta['seasons']
        categories_tm = response.meta['categories_TM']
        
        # Récupérer les UUIDs des pilotes depuis l'API
        riders_api_uuids = [
            rider.get("rider", {}).get("riders_api_uuid", "N/A")
            for rider in data.get("classification", [])
        ]

        # Fusionner les deux sources d'IDs (HTML + API) tout en évitant les doublons
        for uuid in riders_api_uuids:
            if uuid and uuid not in self.riders_uuids:
                self.riders_uuids.append(uuid)

        # Scraper les détails des pilotes en utilisant la liste fusionnée
        for uuid in self.riders_uuids:
            rider_url_details = f"https://api.pulselive.motogp.com/motogp/v1/riders/{uuid}"
            # Passer une request sur les nouvelles URLs et un callback qui appellera `parse_rider_details` et les données seasons et categories_TM et un dictionnaire rider_data pour rassembler toutes les informations
            yield Request(rider_url_details, callback=self.parse_rider_details, meta={'rider_data': {}, 'seasons': seasons, 'categories_TM': categories_tm})

    def parse_rider_details(self, response):
        # Parser la réponse de l'API spécifique aux détails des pilotes
        data_rider_details = json.loads(response.text)

        # Récupérer les données déjà associées dans `meta` (les données envoyées avec `yield Request` dans la fonction `parse`)
        rider_data = response.meta['rider_data']
        seasons = response.meta['seasons']
        categories_tm = response.meta['categories_TM']

        # Récupérer les données des pilotes
        id = data_rider_details.get("id", "N/A")
        legacy_id = data_rider_details.get("legacy_id", "N/A")
        name = data_rider_details.get("name", "N/A")
        surname = data_rider_details.get("surname", "N/A")
        country = data_rider_details.get("country", {}).get("name", "N/A")
        country_flag = data_rider_details.get("country", {}).get("flag", "N/A")
        # Initialiser un dictionnaire pour regrouper les saisons et les équipes
        season_team_mapping = {}
        # Parcourir les détails de la carrière
        for season in data_rider_details.get("career", []):
            season_year = season.get("season", "N/A")
            if season.get("team") and isinstance(season.get("team"), dict):
                team_id = season.get("team", {}).get("id", "N/A")
                team_type_driver = season.get("type", "N/A")
            else:
                team_id = "N/A"
                team_type_driver = "N/A"
            if season.get("category", {}).get("name","N/A") == "MotoGP" or season.get("category", {}).get("name","N/A") == "500cc":
                season_team_mapping[season_year] = {"team_id": team_id, "team_type_driver": team_type_driver}  # Associer la saison à l'équipe
        birth_date = data_rider_details.get("birth_date", "N/A")
        birth_city = data_rider_details.get("birth_city", "N/A")
        max_year = max(season_team_mapping.keys())
        for season in data_rider_details.get("career", []):
            if season.get("season") == max_year:
                picture = season.get("pictures", {}).get("profile", {}).get("main", "N/A")
        #bio = data_rider_details.get("biography", {}).get("text", "N/A")
        height = data_rider_details.get("physical_attributes", {}).get("height", "N/A")
        weight = data_rider_details.get("physical_attributes", {}).get("weight", "N/A")
        start_year = min(season_team_mapping.keys())
        retired_year = data_rider_details.get("retired_year", "N/A")
        retired = data_rider_details.get("retired", "N/A")

        # Ajouter les informations du pilote aux données déjà existantes
        rider_data.update({
            "id": id,
            "legacy_id": legacy_id,
            "name": name,
            "surname": surname,
            "country": country,
            "country_flag": country_flag,
            "birth_date": birth_date,
            "birth_city": birth_city,
            "picture": picture,
            #"bio": bio,
            "height": height,
            "weight": weight,
            "start_year": start_year,
            "retired_year": retired_year,
            "retired": retired,
            "season_team":season_team_mapping
        })

        # Maintenant on fait une deuxième requête pour récupérer les statistiques des pilotes
        rider_url_stats = f"https://api.pulselive.motogp.com/motogp/v1/riders/{rider_data['legacy_id']}/stats"
        # Passer une request sur la nouvelle URL et un callback qui appellera `parse_rider_stats` et les données seasons et categories_TM et le dictionnaire rider_data avec les données déjà existantes et updater
        yield Request(rider_url_stats, callback=self.parse_rider_stats, meta={'rider_data': rider_data, 'seasons': seasons, 'categories_TM': categories_tm})

    def parse_rider_stats(self, response):
        # Parser la réponse de l'API spécifique aux stats des pilotes
        data_rider_stats = json.loads(response.text)
        
        # Récupérer les données déjà associées dans `meta` (les données envoyées avec le `yield Request` dans la fonction `parse_rider_details`)
        rider_data = response.meta['rider_data']
        seasons = response.meta['seasons']
        categories_tm = response.meta['categories_TM']
        
        # Récupérer les données des stats des pilotes
        for category in categories_tm:
            world_champion_wins = next((cat["count"] for cat in data_rider_stats.get("world_championship_wins", {}).get("categories", []) if cat.get("category", {}).get("id") == category['id']),0)
            grand_prix_victories = next((cat["count"] for cat in data_rider_stats.get("grand_prix_victories", {}).get("categories", []) if cat.get("category", {}).get("id") == category['id']),0)            
            podiums = next((cat["count"] for cat in data_rider_stats.get("podiums", {}).get("categories", []) if cat.get("category", {}).get("id") == category['id']),0)
            poles = next((cat["count"] for cat in data_rider_stats.get("poles", {}).get("categories", []) if cat.get("category", {}).get("id") == category['id']),0)
            races = next((cat["count"] for cat in data_rider_stats.get("all_races", {}).get("categories", []) if cat.get("category", {}).get("id") == category['id']),0)

        # Ajouter les statistiques des pilotes aux données déjà existantes
        rider_data.update({
            "world_champion_wins": world_champion_wins,
            "grand_prix_victories":  grand_prix_victories,
            "podiums": podiums,
            "poles": poles,
            "races": races
        })

        # À ce moment-là, toutes les données sont disponibles dans `rider_data`
        # On peut maintenant envoyer les données combinées dans un seul `yield`
        yield Rider(
            id = rider_data.get('id'),
            legacy_id = rider_data.get('legacy_id'),
            name = rider_data.get('name'),
            surname = rider_data.get('surname'),
            country = rider_data.get('country'),
            country_flag = rider_data.get("country_flag"),
            birth_date = rider_data.get("birth_date"),
            birth_city = rider_data.get("birth_city"),
            picture = rider_data.get("picture"),
            #bio = rider_data.get("bio"),
            taille = rider_data.get("height"),
            poids = rider_data.get("weight"),
            start_year = rider_data.get("start_year"),
            retired_year = rider_data.get("retired_year"),
            retired = rider_data.get("retired"),
            season_team = rider_data.get("season_team"),
            world_champion_wins = rider_data.get("world_champion_wins"),
            grand_prix_victories = rider_data.get("grand_prix_victories"),
            podiums = rider_data.get('podiums'),
            poles = rider_data.get("poles"),
            races = rider_data.get("races")
        )