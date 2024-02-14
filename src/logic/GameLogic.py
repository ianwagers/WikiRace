
from PyQt5.QtCore import QObject, pyqtSignal
import requests, sys
sys.path.append('C:\Project_Workspace\WikiRace')

class GameLogic(QObject):
    linkClicked = pyqtSignal(str)
    openGameTab = pyqtSignal(str, str)

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

    def startGame(self, start_url=None, end_url=None):
        # Check if start_url or end_url is None and fetch a random link
        if start_url is None:
            start_url = self.getRandomWikiLink()
        if end_url is None:
            end_url = self.getRandomWikiLink()

        # Setup game logic here (e.g., resetting counters, starting timers)

        # Notify the UI to open a new game tab with the start and end URLs
        self.openGameTab.emit(start_url, end_url)

    def stopGame(self):
        # This method will stop the game and perform any cleanup necessary
        pass  # Placeholder for actual stop game logic

    def linkClicked(self, url):
        # This method will be called when a link is clicked
        self.links_used += 1
        self.linkClicked.emit(url)

    def getLinksUsed(self):
        # This method will return the number of links clicked
        return self.links_used
