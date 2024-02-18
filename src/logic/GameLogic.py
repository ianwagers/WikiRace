from PyQt5.QtCore import QObject, pyqtSignal
import requests, sys
sys.path.append('C:\Project_Workspace\WikiRace')

class GameLogic(QObject):
    linkClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.links_used = 0

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

        # Check if start_url or end_url is None and fetch a random link
        if start_url is not None:
            end_url = self.findWikiPage(start_url)
        else:    
            start_url = self.getRandomWikiLink()
        
        if end_url is not None:
            end_url = self.findWikiPage(end_url)
        else:   
            end_url = self.getRandomWikiLink()       

        # Setup game logic here (e.g., resetting counters, starting timers)

        # Notify the UI to open a new game tab with the start and end URLs
        return start_url, end_url


    def stopGame(self):
        # This method will stop the game and perform any cleanup necessary
        pass  # Placeholder for actual stop game logic


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

        try:
            # Send the request to Wikipedia's API
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Raises an exception for HTTP errors

            # Parse the JSON response
            data = response.json()

            # Check if there are any search results
            if data["query"]["search"]:
                # Extract the page ID of the top search result
                page_id = data["query"]["search"][0]["pageid"]

                # Construct the URL to the Wikipedia page
                wiki_url = f"https://en.wikipedia.org/?curid={page_id}"

                return wiki_url
            else:
                # Handle the case where no search results are found
                print(f"No results found for '{search_text}'")
                return None
        except Exception as e:
            print(f"Error finding Wikipedia page: {e}")
            return None


