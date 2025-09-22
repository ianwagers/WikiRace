"""
Server-side GameLogic for WikiRace Multiplayer Server

Handles Wikipedia page selection and game configuration for multiplayer games.
"""

import requests
import random
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ServerGameLogic:
    """Server-side game logic for Wikipedia page selection"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'WikiRace Multiplayer Server/1.0 (https://github.com/ianwagers/wikirace)'
        }
        
        # Initialize category databases (simplified version)
        self.init_category_databases()
    
    def init_category_databases(self):
        """Initialize category-specific page lists"""
        # These are simplified lists - in a full implementation,
        # you'd want to populate these from Wikipedia API or have larger lists
        
        self.Animals = [
            "https://en.wikipedia.org/wiki/Lion",
            "https://en.wikipedia.org/wiki/Tiger",
            "https://en.wikipedia.org/wiki/Elephant",
            "https://en.wikipedia.org/wiki/Giraffe",
            "https://en.wikipedia.org/wiki/Penguin",
            "https://en.wikipedia.org/wiki/Dolphin",
            "https://en.wikipedia.org/wiki/Eagle",
            "https://en.wikipedia.org/wiki/Shark"
        ]
        
        self.Buildings = [
            "https://en.wikipedia.org/wiki/Eiffel_Tower",
            "https://en.wikipedia.org/wiki/Empire_State_Building",
            "https://en.wikipedia.org/wiki/Burj_Khalifa",
            "https://en.wikipedia.org/wiki/Taj_Mahal",
            "https://en.wikipedia.org/wiki/Colosseum",
            "https://en.wikipedia.org/wiki/Pyramids_of_Giza",
            "https://en.wikipedia.org/wiki/Big_Ben",
            "https://en.wikipedia.org/wiki/Notre-Dame_de_Paris"
        ]
        
        self.Celebrities = [
            "https://en.wikipedia.org/wiki/Leonardo_DiCaprio",
            "https://en.wikipedia.org/wiki/Oprah_Winfrey",
            "https://en.wikipedia.org/wiki/Taylor_Swift",
            "https://en.wikipedia.org/wiki/Elon_Musk",
            "https://en.wikipedia.org/wiki/Beyonc%C3%A9",
            "https://en.wikipedia.org/wiki/Bill_Gates",
            "https://en.wikipedia.org/wiki/Emma_Watson",
            "https://en.wikipedia.org/wiki/Tom_Hanks"
        ]
        
        self.Countries = [
            "https://en.wikipedia.org/wiki/United_States",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/Japan",
            "https://en.wikipedia.org/wiki/Brazil",
            "https://en.wikipedia.org/wiki/Australia",
            "https://en.wikipedia.org/wiki/Canada",
            "https://en.wikipedia.org/wiki/Germany",
            "https://en.wikipedia.org/wiki/Italy"
        ]
        
        self.Gaming = [
            "https://en.wikipedia.org/wiki/Minecraft",
            "https://en.wikipedia.org/wiki/Fortnite",
            "https://en.wikipedia.org/wiki/Pok%C3%A9mon",
            "https://en.wikipedia.org/wiki/Super_Mario",
            "https://en.wikipedia.org/wiki/World_of_Warcraft",
            "https://en.wikipedia.org/wiki/League_of_Legends",
            "https://en.wikipedia.org/wiki/Call_of_Duty",
            "https://en.wikipedia.org/wiki/Grand_Theft_Auto"
        ]
        
        self.Literature = [
            "https://en.wikipedia.org/wiki/Harry_Potter",
            "https://en.wikipedia.org/wiki/Lord_of_the_Rings",
            "https://en.wikipedia.org/wiki/Shakespeare",
            "https://en.wikipedia.org/wiki/Mark_Twain",
            "https://en.wikipedia.org/wiki/Charles_Dickens",
            "https://en.wikipedia.org/wiki/Jane_Austen",
            "https://en.wikipedia.org/wiki/Hemingway",
            "https://en.wikipedia.org/wiki/Tolkien"
        ]
        
        self.Music = [
            "https://en.wikipedia.org/wiki/Beatles",
            "https://en.wikipedia.org/wiki/Michael_Jackson",
            "https://en.wikipedia.org/wiki/Elvis_Presley",
            "https://en.wikipedia.org/wiki/Madonna",
            "https://en.wikipedia.org/wiki/Queen_(band)",
            "https://en.wikipedia.org/wiki/Led_Zeppelin",
            "https://en.wikipedia.org/wiki/Bob_Dylan",
            "https://en.wikipedia.org/wiki/Prince_(musician)"
        ]
        
        self.STEM = [
            "https://en.wikipedia.org/wiki/Albert_Einstein",
            "https://en.wikipedia.org/wiki/Isaac_Newton",
            "https://en.wikipedia.org/wiki/Marie_Curie",
            "https://en.wikipedia.org/wiki/Charles_Darwin",
            "https://en.wikipedia.org/wiki/Nikola_Tesla",
            "https://en.wikipedia.org/wiki/Stephen_Hawking",
            "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
            "https://en.wikipedia.org/wiki/Galileo_Galilei"
        ]
        
        self.HistoricalEvents = [
            "https://en.wikipedia.org/wiki/World_War_II",
            "https://en.wikipedia.org/wiki/American_Revolution",
            "https://en.wikipedia.org/wiki/Renaissance",
            "https://en.wikipedia.org/wiki/Industrial_Revolution",
            "https://en.wikipedia.org/wiki/French_Revolution",
            "https://en.wikipedia.org/wiki/Civil_War",
            "https://en.wikipedia.org/wiki/Space_Race",
            "https://en.wikipedia.org/wiki/Cold_War"
        ]
        
        self.MostLinked = [
            "https://en.wikipedia.org/wiki/United_States",
            "https://en.wikipedia.org/wiki/World_War_II",
            "https://en.wikipedia.org/wiki/United_Kingdom",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/Germany",
            "https://en.wikipedia.org/wiki/Japan",
            "https://en.wikipedia.org/wiki/Russia",
            "https://en.wikipedia.org/wiki/China"
        ]
        
        self.USPresidents = [
            "https://en.wikipedia.org/wiki/George_Washington",
            "https://en.wikipedia.org/wiki/Abraham_Lincoln",
            "https://en.wikipedia.org/wiki/Franklin_D._Roosevelt",
            "https://en.wikipedia.org/wiki/Thomas_Jefferson",
            "https://en.wikipedia.org/wiki/Theodore_Roosevelt",
            "https://en.wikipedia.org/wiki/John_F._Kennedy",
            "https://en.wikipedia.org/wiki/Ronald_Reagan",
            "https://en.wikipedia.org/wiki/Barack_Obama"
        ]
    
    def get_random_wiki_link(self) -> Optional[str]:
        """Get a random Wikipedia page"""
        try:
            response = requests.get('https://en.wikipedia.org/w/api.php', {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 0,
                'rnlimit': 1
            }, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                json_data = response.json()
                page_id = json_data['query']['random'][0]['id']
                random_page_url = f'https://en.wikipedia.org/?curid={page_id}'
                return random_page_url
            else:
                logger.error(f"Error fetching random Wikipedia page: {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_link_from_category(self, category: str) -> Optional[str]:
        """Get a random page from a specific category"""
        try:
            if hasattr(self, category):
                category_list = getattr(self, category)
                if category_list:
                    return random.choice(category_list)
            
            logger.warning(f"Unknown category: {category}")
            return self.get_random_wiki_link()
        except Exception as e:
            logger.error(f"Error getting link from category {category}: {e}")
            return self.get_random_wiki_link()
    
    def find_wiki_page(self, search_text: str) -> Optional[str]:
        """Find a Wikipedia page by search text"""
        api_url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_text,
            "format": "json",
            "srlimit": 1
        }
        
        try:
            response = requests.get(api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["query"]["search"]:
                page_id = data["query"]["search"][0]["pageid"]
                wiki_url = f"https://en.wikipedia.org/?curid={page_id}"
                logger.info(f"Found Wikipedia page for '{search_text}': {wiki_url}")
                return wiki_url
            else:
                logger.warning(f"No results found for '{search_text}'")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for '{search_text}': {e}")
            return self.get_random_wiki_link()
        except Exception as e:
            logger.error(f"Unexpected error searching for '{search_text}': {e}")
            return self.get_random_wiki_link()
    
    def get_title_from_url(self, url: str) -> Optional[str]:
        """Get the title of a Wikipedia page from its URL"""
        if not url:
            return None
        
        try:
            import urllib.parse
            
            # Handle /wiki/ URLs (extract title from path)
            if "/wiki/" in url:
                path_parts = url.split("/wiki/")
                if len(path_parts) > 1:
                    title_part = path_parts[-1].split("?")[0].split("#")[0]
                    # Decode URL encoding and replace underscores with spaces
                    title = urllib.parse.unquote(title_part).replace("_", " ")
                    return title
            
            # Handle curid URLs (use API)
            elif "curid=" in url:
                parsed = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed.query)
                if "curid" in query_params:
                    page_id = query_params["curid"][0]
                    
                    api_url = "https://en.wikipedia.org/w/api.php"
                    params = {
                        "action": "query",
                        "pageids": page_id,
                        "format": "json"
                    }
                    
                    response = requests.get(api_url, params=params, headers=self.headers, timeout=5)
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_data in pages.values():
                        return page_data.get("title", None)
            
            return None  # Couldn't extract title from URL
            
        except Exception as e:
            logger.error(f"Error getting title from URL {url}: {e}")
            return None
    
    def select_game_pages(self, start_selection: str, end_selection: str, 
                         custom_start: Optional[str] = None, 
                         custom_end: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Select start and end pages for a game
        
        Returns:
            Tuple of (start_url, end_url, start_title, end_title)
        """
        
        # Select start page
        if start_selection == 'Custom' and custom_start:
            start_url = self.find_wiki_page(custom_start)
        elif start_selection == 'Random':
            start_url = self.get_random_wiki_link()
        else:
            start_url = self.get_link_from_category(start_selection)
        
        # Select end page
        if end_selection == 'Custom' and custom_end:
            end_url = self.find_wiki_page(custom_end)
        elif end_selection == 'Random':
            end_url = self.get_random_wiki_link()
        else:
            end_url = self.get_link_from_category(end_selection)
        
        # Get titles
        start_title = self.get_title_from_url(start_url) if start_url else None
        end_title = self.get_title_from_url(end_url) if end_url else None
        
        logger.info(f"Selected game pages - Start: {start_title} ({start_url}), End: {end_title} ({end_url})")
        
        return start_url, end_url, start_title, end_title


# Global instance
server_game_logic = ServerGameLogic()
