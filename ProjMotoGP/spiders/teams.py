import scrapy
from scrapy import Request
import json
from ..items import Team
from pathlib import Path

class TeamsSpider(scrapy.Spider):
    name = "teams"
    allowed_domains = ["api.pulselive.motogp.com"]

    def start_requests(self):
        # Charger les fichiers JSON
        seasons_file = Path(__file__).parent.parent.parent / "seasons.json"
        with open(seasons_file, "r") as f:
            seasons = json.load(f)

        categories_file = Path(__file__).parent.parent.parent / "categories.json"
        with open(categories_file, "r") as f:
            categories = json.load(f)

        base_url = "https://api.pulselive.motogp.com/motogp/v1/teams"

        # Initialiser un dictionnaire vide qui sera transmis via `meta`
        teams_mapping = {}

        # Générer les requêtes
        for i, season in enumerate(seasons):
            for j, category in enumerate(categories):
                url = f"{base_url}?categoryUuid={category['id']}&seasonYear={season['year']}"
                
                yield Request(
                    url,
                    callback=self.parse,
                    meta={
                        'season_year': season['year'],
                        'teams_mapping': teams_mapping,
                        'last_request': (i == len(seasons) - 1 and j == len(categories) - 1)  # Vérifier si c'est la dernière requête
                    }
                )

    def parse(self, response):
        data_teams_details = json.loads(response.text)
        season_year = response.meta['season_year']
        teams_mapping = response.meta['teams_mapping']
        last_request = response.meta['last_request']

        for team in data_teams_details:
            team_id = team.get("id", "N/A")
            name = team.get("name", "N/A")
            constructor_name = team.get("constructor", {}).get("name", "N/A")
            picture = team.get("picture", "N/A")
            riders = [rider.get("id", "N/A") for rider in team.get("riders", [])]

            if team_id not in teams_mapping:
                teams_mapping[team_id] = {
                    "id": team_id,
                    "name": name,
                    "constructor_name": constructor_name,
                    "picture": picture,
                    "riders_team": {}
                }

            teams_mapping[team_id]["riders_team"][season_year] = riders

        # Si c'est la dernière requête, on fait une copie des valeurs pour éviter l'erreur
        if last_request:
            teams_list = list(teams_mapping.values())  # Copie les valeurs du dictionnaire

            for team in teams_list:
                yield Team(
                    id=team["id"],
                    name=team["name"],
                    constructor_name=team["constructor_name"],
                    picture=team["picture"],
                    riders_team=team["riders_team"]
                )
