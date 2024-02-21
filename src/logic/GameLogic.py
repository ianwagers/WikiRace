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
        
    # Currently supported categories:
    # 'Buildings', 'Celebrities', 'Countries', 'Most Popular', 'US Presidents', 'Gaming', 'Random', 'Custom'
    def startGame(self, homePage, start_url=None, end_url=None):
        self.homePage = homePage

        match start_url:
            case 'Random': # Start a game with random Wikipedia pages
                start_url = self.getRandomWikiLink()
            case 'Custom': # Start a game with custom Wikipedia pages
                start_url = self.findWikiPage(start_url)
            case 'Buildings': # Start a game with a specific category of Wikipedia pages
                start_url = self.getLinkFromCategory('Buildings')
            case 'Celebrities':
                start_url = self.getLinkFromCategory('Celebrities')
            case 'Countries':
                start_url = self.getLinkFromCategory('Countries')
            case 'Most Popular':
                start_url = self.getLinkFromCategory('Most Popular')
            case 'US Presidents':
                start_url = self.getLinkFromCategory('US Presidents')
            case 'Gaming':
                start_url = self.getLinkFromCategory('Gaming')
            case _:
                start_url = self.findWikiPage("Segmentation Fault (software bug)")

        match end_url:
            case 'Random': # End a game with random Wikipedia pages
                end_url = self.getRandomWikiLink()
            case 'Custom':
                end_url = self.findWikiPage(end_url)
            case 'Buildings':
                end_url = self.getLinkFromCategory('Buildings')
            case 'Celebrities':
                end_url = self.getLinkFromCategory('Celebrities')
            case 'Countries':
                end_url = self.getLinkFromCategory('Countries')
            case 'Most Popular':
                end_url = self.getLinkFromCategory('Most Popular')
            case 'US Presidents':
                end_url = self.getLinkFromCategory('US Presidents')
            case 'Gaming':
                end_url = self.getLinkFromCategory('Gaming')
            case _:
                end_url = self.findWikiPage("Segmentation Fault (software bug)")
            
            
        # Notify the UI to open a new game tab with the start and end URLs
        return start_url, end_url


    def stopGame(self):
        # This method will stop the game and perform any cleanup necessary
        pass  # Placeholder for actual stop game logic

    def getLinkFromCategory(self, category):
        match category:
            case 'Buildings':
                i = int(random() * len(self.Buildings))
                return self.Buildings[i]
            case 'Celebrities':
                i = int(random() * len(self.Celebrities))
                return self.Celebrities[i]
            case 'Countries':
                i = int(random() * len(self.Countries))
                return self.Countries[i]
            case 'Most Popular':
                i - int(random() * len(self.MostPopular))
                return self.MostPopular[i]
            case 'US Presidents':
                i = int(random() * len(self.USPresidents))
                return self.USPresidents[i]
            case 'Gaming':
                i = int(random() * len(self.Gaming))
                return self.Gaming[i]
            case _:
                return self.findWikiPage("God's Plan (song)")


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
        
    # In the future this will be saved in some kind of external doc/database
    def initGameDatabase(self):
        self.Buildings = [
            "https://en.wikipedia.org/wiki/Empire_State_Building",
            "https://en.wikipedia.org/wiki/Burj_Khalifa",
            "https://en.wikipedia.org/wiki/One_World_Trade_Center",
            "https://en.wikipedia.org/wiki/Shanghai_Tower",
            "https://en.wikipedia.org/wiki/Taipei_101", 
            "https://en.wikipedia.org/wiki/Space_Needle", 
            "https://en.wikipedia.org/wiki/Eiffel_Tower",
            "https://en.wikipedia.org/wiki/Leaning_Tower_of_Pisa",
            "https://en.wikipedia.org/wiki/Big_Ben",
            "https://en.wikipedia.org/wiki/Sydney_Opera_House",
        ]

        self.Celebrities = [
            "https://en.wikipedia.org/wiki/Elon_Musk",
            "https://en.wikipedia.org/wiki/Bill_Gates",
            "https://en.wikipedia.org/wiki/Jeff_Bezos",
            "https://en.wikipedia.org/wiki/Mark_Zuckerberg",
            "https://en.wikipedia.org/wiki/Drake_(musician)",
            "https://en.wikipedia.org/wiki/Dwayne_Johnson",
            "https://en.wikipedia.org/wiki/Eminem",
            "https://en.wikipedia.org/wiki/Will_Smith",
            "https://en.wikipedia.org/wiki/Leonardo_DiCaprio",
            "https://en.wikipedia.org/wiki/Brad_Pitt",
        ]

        self.Gaming = [
            "https://en.wikipedia.org/wiki/League_of_Legends",
            "https://en.wikipedia.org/wiki/World_of_Warcraft",
            "https://en.wikipedia.org/wiki/Counter-Strike:_Global_Offensive",
            "https://en.wikipedia.org/wiki/Fortnite",
            "https://en.wikipedia.org/wiki/Minecraft",
            "https://en.wikipedia.org/wiki/Grand_Theft_Auto_V",
            "https://en.wikipedia.org/wiki/Call_of_Duty:_Warzone",
            "https://en.wikipedia.org/wiki/Overwatch_(video_game)",
            "https://en.wikipedia.org/wiki/Valorant",
            "https://en.wikipedia.org/wiki/Among_Us",
        ]

        self.Countries = [
            "https://en.wikipedia.org/wiki/United_States",
            "https://en.wikipedia.org/wiki/China",
            "https://en.wikipedia.org/wiki/India",
            "https://en.wikipedia.org/wiki/Brazil",
            "https://en.wikipedia.org/wiki/Russia",
            "https://en.wikipedia.org/wiki/Australia",
            "https://en.wikipedia.org/wiki/Canada",
            "https://en.wikipedia.org/wiki/South_Africa",
            "https://en.wikipedia.org/wiki/Nigeria",
            "https://en.wikipedia.org/wiki/Argentina",
        ]

        self.USPresidents = [
            "https://en.wikipedia.org/wiki/George_Washington",
            "https://en.wikipedia.org/wiki/Thomas_Jefferson",
            "https://en.wikipedia.org/wiki/Abraham_Lincoln",
            "https://en.wikipedia.org/wiki/Theodore_Roosevelt",
            "https://en.wikipedia.org/wiki/Franklin_D._Roosevelt",
            "https://en.wikipedia.org/wiki/John_F._Kennedy",
            "https://en.wikipedia.org/wiki/Ronald_Reagan",
            "https://en.wikipedia.org/wiki/Barack_Obama",
            "https://en.wikipedia.org/wiki/Donald_Trump",
            "https://en.wikipedia.org/wiki/Joe_Biden",
            "https://en.wikipedia.org/wiki/George_H._W._Bush",
            "https://en.wikipedia.org/wiki/Bill_Clinton",
        ]

        self.MostPopular = [
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://en.wikipedia.org/wiki/Sex",
            "https://en.wikipedia.org/wiki/United States",
            "https://en.wikipedia.org/wiki/India",
            "https://en.wikipedia.org/wiki/Lady_Gaga",
            "https://en.wikipedia.org/wiki/Barack_Obama",
            "https://en.wikipedia.org/wiki/Donald_Trump",
            "https://en.wikipedia.org/wiki/COVID-19_pandemic",
            "https://en.wikipedia.org/wiki/World_War_II",
        ]

