from PyQt5.QtCore import QObject, pyqtSignal
from random import random
import requests, sys
sys.path.append('C:\Project_Workspace\WikiRace')

class GameLogic(QObject):
    linkClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.links_used = 0
        self.initGameDatabase()

    def getRandomWikiLink(self):
        try:
            # Use Wikipedia's API to get a random page
            response = requests.get('https://en.wikipedia.org/w/api.php', {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 0,
                'rnlimit': 1
            })
            # Check if the request was successful
            if response.status_code == 200:
                json_data = response.json()
                page_id = json_data['query']['random'][0]['id']
                random_page_url = f'https://en.wikipedia.org/?curid={page_id}'
                return random_page_url
            else:
                # Handle unsuccessful request
                print(f"Error fetching random Wikipedia page: {response.status_code}")
                return None
        except requests.RequestException as e:
            # Handle request exception
            print(f"Request failed: {e}")
            return None

    def startGame(self, homePage, start_url=None, end_url=None):
        self.homePage = homePage

        match start_url:
            case 'Random': # Start a game with random Wikipedia pages
                start_url = self.getRandomWikiLink()
            case 'Custom': # Start a game with custom Wikipedia pages
                start_url = self.findWikiPage(start_url)
            case 'Buildings': # Start a game with a specific category of Wikipedia pages
                start_url = self.getFromCategory('Buildings')

        match end_url:
            case 'Random': # End a game with random Wikipedia pages
                end_url = self.getRandomWikiLink()
            case 'Custom':
                end_url = self.findWikiPage(end_url)
            case 'Buildings':
                end_url = self.getLinkFromCategory('Buildings')
            
            
        # Notify the UI to open a new game tab with the start and end URLs
        return start_url, end_url


    def stopGame(self):
        # This method will stop the game and perform any cleanup necessary
        pass  # Placeholder for actual stop game logic

    def getLinkFromCategory(self, category):
        match category:
            case 'Buildings':
                i = random(0, len(self.Buildings) - 1)


    def findWikiPage(self, search_text):
        # URL to Wikipedia's API for searching
        api_url = "https://en.wikipedia.org/w/api.php"

        # Parameters for the API request
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_text,
            "format": "json",
            "srlimit": 1  # Limit the search to the top result
        }

        # Send the request to Wikipedia's API
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raises an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Check if search results are present
        if data["query"]["search"]:
            # Extract the page ID of the top search result
            page_id = data["query"]["search"][0]["pageid"]

            # Construct the URL to the Wikipedia page
            wiki_url = f"https://en.wikipedia.org/?curid={page_id}"

            print(f"Found Wikipedia page: {wiki_url}")
            return wiki_url
        else:
            # Handle the case where no results are found
            print("No results found for the given search text.")
            return wiki_url
        
    def initGameDatabase(self):
        self.Buildings = [
            "https://en.wikipedia.org/wiki/Empire_State_Building",
            "https://en.wikipedia.org/wiki/Burj_Khalifa",
            "https://en.wikipedia.org/wiki/One_World_Trade_Center",
            "https://en.wikipedia.org/wiki/Shanghai_Tower",
            "https://en.wikipedia.org/wiki/Taipei_101", 
            "https://en.wikipedia.org/wiki/Space_Needle", 
            "https://en.wikipedia.org/wiki/Eiffel_Tower",
        ]