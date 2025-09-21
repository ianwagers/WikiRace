from PyQt6.QtCore import QObject, pyqtSignal
from random import random
import requests, sys
sys.path.append('C:\Program Files\WikiRace')

class GameLogic(QObject):
    linkClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.links_used = 0
        self.initGameDatabase()

    def getRandomWikiLink(self):
        try:
            # Headers to avoid 403 errors
            headers = {
                'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
            }
            
            # Use Wikipedia's API to get a random page
            response = requests.get('https://en.wikipedia.org/w/api.php', {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 0,
                'rnlimit': 1
            }, headers=headers, timeout=10)
            
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
    # 'Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 'Historical Events', 'Random', 'Custom'
    def startGame(self, homePage, start_url=None, end_url=None):
        self.homePage = homePage

        match start_url:
            case 'Random': # Start a game with random Wikipedia pages
                start_url = self.getRandomWikiLink()
            case 'Animals':
                start_url = self.getLinkFromCategory('Animals')
            case 'Buildings': # Start a game with a specific category of Wikipedia pages
                start_url = self.getLinkFromCategory('Buildings')
            case 'Celebrities':
                start_url = self.getLinkFromCategory('Celebrities')
            case 'Countries':
                start_url = self.getLinkFromCategory('Countries')
            case 'Literature':
                start_url = self.getLinkFromCategory('Literature')
            case 'Music':
                start_url = self.getLinkFromCategory('Music')
            case 'STEM':
                start_url = self.getLinkFromCategory('STEM')
            case 'Historical Events':
                start_url = self.getLinkFromCategory('Historical Events')
            case 'Most Linked':
                start_url = self.getLinkFromCategory('Most Linked')
            case 'US Presidents':
                start_url = self.getLinkFromCategory('US Presidents')
            case 'Gaming':
                start_url = self.getLinkFromCategory('Gaming')
            case _: # Start a game with a custom Wikipedia page
                start_url = self.findWikiPage(start_url)

        match end_url:
            case 'Random': # End a game with random Wikipedia pages
                end_url = self.getRandomWikiLink()
            case 'Animals':
                end_url = self.getLinkFromCategory('Animals')
            case 'Buildings':
                end_url = self.getLinkFromCategory('Buildings')
            case 'Celebrities':
                end_url = self.getLinkFromCategory('Celebrities')
            case 'Literature':
                end_url = self.getLinkFromCategory('Literature')
            case 'Music':
                end_url = self.getLinkFromCategory('Music')
            case 'STEM':
                end_url = self.getLinkFromCategory('STEM')
            case 'Historical Events':
                end_url = self.getLinkFromCategory('Historical Events')
            case 'Most Linked':
                end_url = self.getLinkFromCategory('Most Linked')
            case 'Countries':
                end_url = self.getLinkFromCategory('Countries')
            case 'US Presidents':
                end_url = self.getLinkFromCategory('US Presidents')
            case 'Gaming':
                end_url = self.getLinkFromCategory('Gaming')
            case _:
                end_url = self.findWikiPage(end_url)
               
        # Get titles for the URLs (for custom pages)
        start_title = None
        end_title = None
        
        # If these are custom pages (not from categories), try to get titles
        if start_url and ("curid=" in start_url):
            # This is a custom page from search, try to get the title
            try:
                start_title = self._getTitleFromSearchUrl(start_url)
            except:
                pass
        
        if end_url and ("curid=" in end_url):
            # This is a custom page from search, try to get the title
            try:
                end_title = self._getTitleFromSearchUrl(end_url)
            except:
                pass
        
        # Notify the UI to open a new game tab with the start and end URLs and titles
        return start_url, end_url, start_title, end_title
    
    def _getTitleFromSearchUrl(self, url):
        """Helper method to get title from a curid URL"""
        # This is a simple cache-like approach - in a real app you might want to cache this
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        if "curid" in query_params:
            page_id = query_params["curid"][0]
            
            # Make a quick API call to get the title
            api_url = "https://en.wikipedia.org/w/api.php"
            headers = {'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'}
            params = {
                "action": "query",
                "pageids": page_id,
                "format": "json"
            }
            
            try:
                import requests
                response = requests.get(api_url, params=params, headers=headers, timeout=5)
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                for page_data in pages.values():
                    return page_data.get("title", None)
            except:
                pass
        
        return None

    def getLinkFromCategory(self, category):
        match category:
            case 'Animals':
                i = int(random() * len(self.Animals))
                return self.Animals[i]
            case 'Buildings':
                i = int(random() * len(self.Buildings))
                return self.Buildings[i]
            case 'Celebrities':
                i = int(random() * len(self.Celebrities))
                return self.Celebrities[i]
            case 'Countries':
                i = int(random() * len(self.Countries))
                return self.Countries[i]
            case 'Literature':
                i = int(random() * len(self.Literature))
                return self.Literature[i]
            case 'Music':
                i = int(random() * len(self.Music))
                return self.Music[i]
            case 'STEM':
                i = int(random() * len(self.STEM))
                return self.STEM[i]
            case 'Historical Events':
                i = int(random() * len(self.HistoricalEvents))
                return self.HistoricalEvents[i]
            case 'Most Linked':
                i = int(random() * len(self.MostLinked))
                return self.MostLinked[i]
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

        # Headers to avoid 403 errors
        headers = {
            'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
        }

        # Parameters for the API request
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_text,
            "format": "json",
            "srlimit": 1  # Limit the search to the top result
        }

        try:
            # Send the request to Wikipedia's API with headers
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # Raises an exception for HTTP errors

            # Parse the JSON response
            data = response.json()

            # Check if search results are present
            if data["query"]["search"]:
                # Extract the page ID and title of the top search result
                page_id = data["query"]["search"][0]["pageid"]
                page_title = data["query"]["search"][0]["title"]

                # Construct the URL to the Wikipedia page
                wiki_url = f"https://en.wikipedia.org/?curid={page_id}"

                print(f"Found Wikipedia page: {wiki_url} (Title: {page_title})")
                return wiki_url
            else:
                # Handle the case where no results are found
                print(f"No results found for '{search_text}'. Using fallback.")
                return None  # Return None to indicate no page found
        except requests.exceptions.RequestException as e:
            print(f"Error searching for '{search_text}': {e}")
            print("Using fallback random page...")
            return self.getRandomWikiLink()
        except Exception as e:
            print(f"Unexpected error searching for '{search_text}': {e}")
            print("Using fallback random page...")
            return self.getRandomWikiLink()
    
    def findWikiPageWithTitle(self, search_text):
        """Find a Wikipedia page and return both URL and title, or None if not found"""
        api_url = "https://en.wikipedia.org/w/api.php"

        headers = {
            'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
        }

        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_text,
            "format": "json",
            "srlimit": 1
        }

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data["query"]["search"]:
                page_id = data["query"]["search"][0]["pageid"]
                page_title = data["query"]["search"][0]["title"]
                wiki_url = f"https://en.wikipedia.org/?curid={page_id}"

                print(f"Found Wikipedia page: {wiki_url} (Title: {page_title})")
                return wiki_url, page_title
            else:
                print(f"No results found for '{search_text}'.")
                return None, None
        except Exception as e:
            print(f"Error searching for '{search_text}': {e}")
            return None, None
        
    # In the future this will be saved in some kind of external doc/database
    def initGameDatabase(self):
        
        self.Animals = [
            "https://en.wikipedia.org/wiki/Lion",
            "https://en.wikipedia.org/wiki/Tiger",
            "https://en.wikipedia.org/wiki/Elephant",
            "https://en.wikipedia.org/wiki/Giraffe",
            "https://en.wikipedia.org/wiki/Zebra",
            "https://en.wikipedia.org/wiki/Cougar",
            "https://en.wikipedia.org/wiki/Grizzly_bear",
            "https://en.wikipedia.org/wiki/Brown_bear",
            "https://en.wikipedia.org/wiki/Black_bear",
            "https://en.wikipedia.org/wiki/Polar_bear",
            "https://en.wikipedia.org/wiki/Panda",
            "https://en.wikipedia.org/wiki/Koala",
            "https://en.wikipedia.org/wiki/Kangaroo",
            "https://en.wikipedia.org/wiki/Platypus"
        ]

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

        self.HistoricalEvents = [
            "https://en.wikipedia.org/wiki/World_War_II",
            "https://en.wikipedia.org/wiki/World_War_I",
            "https://en.wikipedia.org/wiki/American_Revolution",
            "https://en.wikipedia.org/wiki/French_Revolution",
            "https://en.wikipedia.org/wiki/Industrial_Revolution",
            "https://en.wikipedia.org/wiki/October_Revolution",
            "https://en.wikipedia.org/wiki/Triangle_Shirtwaist_Factory_fire",
            "https://en.wikipedia.org/wiki/List_of_sieges_of_Constantinople",
            "https://en.wikipedia.org/wiki/Battle_of_Antietam",
            "https://en.wikipedia.org/wiki/Emu_War",
            "https://en.wikipedia.org/wiki/Chernobyl_disaster"
        ]

        self.Literature = [
            "https://en.wikipedia.org/wiki/To_Kill_a_Mockingbird",
            "https://en.wikipedia.org/wiki/The_Great_Gatsby",
            "https://en.wikipedia.org/wiki/1984_(novel)",
            "https://en.wikipedia.org/wiki/Brave_New_World",
            "https://en.wikipedia.org/wiki/Fahrenheit_451",
            "https://en.wikipedia.org/wiki/The_Catcher_in_the_Rye",
            "https://en.wikipedia.org/wiki/Shakespeare%27s_sonnets",
            "https://en.wikipedia.org/wiki/The_Odyssey",
            "https://en.wikipedia.org/wiki/Infinite_Jest",
            "https://en.wikipedia.org/wiki/Simulacra_and_Simulation",
            "https://en.wikipedia.org/wiki/Thus_Spoke_Zarathustra"

        ]

        self.Music = [
            "https://en.wikipedia.org/wiki/Bohemian_Rhapsody",
            "https://en.wikipedia.org/wiki/Hey_Jude",
            "https://en.wikipedia.org/wiki/Smells_Like_Teen_Spirit",
            "https://en.wikipedia.org/wiki/Hotel_California",
            "https://en.wikipedia.org/wiki/Imagine_(John_Lennon_song)",
            "https://en.wikipedia.org/wiki/One_(Metallica_song)",
            "https://en.wikipedia.org/wiki/Thriller_(song)",
            "https://en.wikipedia.org/wiki/My_Way",
            "https://en.wikipedia.org/wiki/Despacito",
            "https://en.wikipedia.org/wiki/Shape_of_You",
            "https://en.wikipedia.org/wiki/Daft_Punk",
            "https://en.wikipedia.org/wiki/Glass_Animals"
        ]

        self.STEM = [
            "https://en.wikipedia.org/wiki/Albert_Einstein",
            "https://en.wikipedia.org/wiki/Isaac_Newton",
            "https://en.wikipedia.org/wiki/Nikola_Tesla",
            "https://en.wikipedia.org/wiki/Thomas_Edison",
            "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
            "https://en.wikipedia.org/wiki/Stephen_Hawking",
            "https://en.wikipedia.org/wiki/Charles_Darwin",
            "https://en.wikipedia.org/wiki/Marie_Curie",
            "https://en.wikipedia.org/wiki/Ada_Lovelace",
            "https://en.wikipedia.org/wiki/Alan_Turing",
            "https://en.wikipedia.org/wiki/Physics",
            "https://en.wikipedia.org/wiki/Chemistry",
            "https://en.wikipedia.org/wiki/Biology",
            "https://en.wikipedia.org/wiki/Mathematics",
            "https://en.wikipedia.org/wiki/Statistics",
            "https://en.wikipedia.org/wiki/Geology",
            "https://en.wikipedia.org/wiki/Astronomy",
            "https://en.wikipedia.org/wiki/Geography",
            "https://en.wikipedia.org/wiki/Environmental_science",
            "https://en.wikipedia.org/wiki/Computer_science",
            "https://en.wikipedia.org/wiki/Software_engineering",
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Machine_learning",
            "https://en.wikipedia.org/wiki/Quantum_computing",
            "https://en.wikipedia.org/wiki/Operating_system",
            "https://en.wikipedia.org/wiki/Computer_network",
            "https://en.wikipedia.org/wiki/Computer_security",
            "https://en.wikipedia.org/wiki/Computer_vision",
            "https://en.wikipedia.org/wiki/Robotics",
            "https://en.wikipedia.org/wiki/Computer_graphics",
            "https://en.wikipedia.org/wiki/Computer_simulation",
            "https://en.wikipedia.org/wiki/Computer_animation",
            "https://en.wikipedia.org/wiki/Computer_music",
            "https://en.wikipedia.org/wiki/Computer_architecture",
            "https://en.wikipedia.org/wiki/Computer_hardware",
            "https://en.wikipedia.org/wiki/Computer_software",
            "https://en.wikipedia.org/wiki/Computer_programming",
            "https://en.wikipedia.org/wiki/Computer_algorithm",
            "https://en.wikipedia.org/wiki/Computer_data"

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
            "https://en.wikipedia.org/wiki/United_Kingdom",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/Germany",
            "https://en.wikipedia.org/wiki/Italy",
            "https://en.wikipedia.org/wiki/Spain",
            "https://en.wikipedia.org/wiki/Poland",
            "https://en.wikipedia.org/wiki/Netherlands",
            "https://en.wikipedia.org/wiki/Belgium",
            "https://en.wikipedia.org/wiki/Sweden",
            "https://en.wikipedia.org/wiki/Norway",
            "https://en.wikipedia.org/wiki/Denmark"
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
            "https://en.wikipedia.org/wiki/George_W._Bush",
            "https://en.wikipedia.org/wiki/Jimmy_Carter",
            "https://en.wikipedia.org/wiki/Gerald_Ford",
            "https://en.wikipedia.org/wiki/Richard_Nixon",
            "https://en.wikipedia.org/wiki/Lyndon_B._Johnson",
            "https://en.wikipedia.org/wiki/Dwight_D._Eisenhower",
            "https://en.wikipedia.org/wiki/Harry_S._Truman",
        ]

        self.MostLinked = [
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://en.wikipedia.org/wiki/Sex",
            "https://en.wikipedia.org/wiki/United States",
            "https://en.wikipedia.org/wiki/India",
            "https://en.wikipedia.org/wiki/Lady_Gaga",
            "https://en.wikipedia.org/wiki/Barack_Obama",
            "https://en.wikipedia.org/wiki/Donald_Trump",
            "https://en.wikipedia.org/wiki/COVID-19_pandemic",
            "https://en.wikipedia.org/wiki/World_War_II",
            "https://en.wikipedia.org/wiki/Chernobyl_disaster",
            "https://en.wikipedia.org/wiki/Star_Wars",
            "https://en.wikipedia.org/wiki/Facebook"

        ]

