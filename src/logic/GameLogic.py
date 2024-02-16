
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
import requests, sys


sys.path.append('C:\Project_Workspace\WikiRace')
from src import app

class GameLogic(QObject):
    def __init__(self, mainApplication):
        super().__init__()
        self.mainApplication = mainApplication
    linkClicked = pyqtSignal(str)
    openGameTab = pyqtSignal(str, str)
        

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

    def startGame(self, start_url=None, end_url=None, gameType='solo'):
        # Check if start_url or end_url is None and fetch a random link
        if start_url is None:
            start_url = GameLogic.getRandomWikiLink(self)
        if end_url is None:
            end_url = GameLogic.getRandomWikiLink(self)

        # Setup game logic here (e.g., resetting counters, starting timers)

        # Notify the UI to open a new game tab with the start and end URLs
        self.mainApplication.addSoloGameTab(start_url, end_url)

    def endGame(self):
        # This method will stop the game and perform any cleanup necessary
        pass  # Placeholder for actual stop game logic

    def linkClicked(self, url):
        # This method will be called when a link is clicked
        self.links_used += 1
        self.linkClicked.emit(url)

    def getLinksUsed(self):
        # This method will return the number of links clicked
        return self.links_used
    
class CustomGameDialog(QDialog):
    def __init__(self, soloGamePage):
        super().__init__(soloGamePage)
        self.setWindowTitle('Select Starting and Ending Pages')
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # Added padding around the dialog content

        # Layout for starting page selection
        startingPageLayout = QHBoxLayout()
        startingPageLabel = QLabel('Starting Page:')
        self.startPageCombo = QComboBox()
        self.startPageCombo.addItems(['Random', 'Custom [Coming Soon]'])
        self.startPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        startingPageLayout.addWidget(startingPageLabel)
        startingPageLayout.addWidget(self.startPageCombo)
        self.layout.addLayout(startingPageLayout)

        # Line edit for custom starting page
        self.customStartPageEdit = QLineEdit()
        self.customStartPageEdit.setPlaceholderText('Enter custom starting page')
        self.customStartPageEdit.setEnabled(False)
        self.layout.addWidget(self.customStartPageEdit)

        # Layout for ending page selection
        endingPageLayout = QHBoxLayout()
        endingPageLabel = QLabel('Ending Page:')
        self.endPageCombo = QComboBox()
        self.endPageCombo.addItems(['Random', 'Custom [Coming Soon]'])
        self.endPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        endingPageLayout.addWidget(endingPageLabel)
        endingPageLayout.addWidget(self.endPageCombo)
        self.layout.addLayout(endingPageLayout)

        # Line edit for custom ending page
        self.customEndPageEdit = QLineEdit()
        self.customEndPageEdit.setPlaceholderText('Enter custom ending page')
        self.customEndPageEdit.setEnabled(False)
        self.layout.addWidget(self.customEndPageEdit)

        # Start Game button
        self.startGameButton = QPushButton('Start Game')
        self.layout.addWidget(self.startGameButton)
        self.startGameButton.clicked.connect(GameLogic.startGame(None, None, 'solo'))

        # Set minimum dialog size for better UI experience
        self.setMinimumSize(275, 175)  # Example improvement for resizing


    def toggleCustomEntry(self):
        self.customStartPageEdit.setEnabled(self.startPageCombo.currentText() == 'Custom')
        self.customEndPageEdit.setEnabled(self.endPageCombo.currentText() == 'Custom')
