from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QListWidget
from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from bs4 import BeautifulSoup
import requests

class SoloGamePage(QWidget):
    def __init__(self, tabWidget, start_url, end_url, parent=None):
        super(SoloGamePage, self).__init__(parent)
        self.tabWidget = tabWidget  # Assuming you need to use tabWidget as well
        self.start_url = start_url
        self.end_url = end_url
        self.startTime = 0
        self.linksUsed = -1  # Start at -1 to account for the initial page
        self.initUI()  # Initialize the UI components

        
        # Now that self.webView is properly initialized in initUI, you don't need to add it to the layout again here.
        # Just proceed with any additional configuration if needed.

    def initUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)  # Main widget's layout

        # Container for sidebar and main content
        self.contentContainer = QWidget()  # Container widget
        self.contentLayout = QHBoxLayout(self.contentContainer)  # Layout for the container

        # Sidebar layout (25% width)
        self.sidebarLayout = QVBoxLayout()
        
        # Stopwatch label, links used counter, and previous links list setup
        self.stopwatchLabel = QLabel("00:00:00")
        self.stopwatchLabel.setStyleSheet("font-size: 20px")
        self.sidebarLayout.addWidget(self.stopwatchLabel)

        self.linksUsedLabel = QLabel("Links Used: " + str(self.linksUsed))
        self.sidebarLayout.addWidget(self.linksUsedLabel)

        self.previousLinksList = QListWidget()
        self.sidebarLayout.addWidget(self.previousLinksList)

        # Sidebar container widget
        self.sidebarContainer = QWidget()
        self.sidebarContainer.setLayout(self.sidebarLayout)
        self.contentLayout.addWidget(self.sidebarContainer, 1)

        # Main content area layout
        self.mainContentLayout = QVBoxLayout()
        
        # Top-bar section
        destinationTitle = self.getTitleFromUrl(self.end_url)
        self.topBarLabel = QLabel("Destination page: " + destinationTitle)
        self.topBarLabel.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        self.mainContentLayout.addWidget(self.topBarLabel)

        # Initialize and configure the web view
        self.webView = QWebEngineView()
        self.webView.load(QUrl(self.start_url))
        self.webView.urlChanged.connect(self.handleLinkClicked)
        self.mainContentLayout.addWidget(self.webView, 3)

        # Main content area container widget
        self.mainContentContainer = QWidget()
        self.mainContentContainer.setLayout(self.mainContentLayout)
        self.contentLayout.addWidget(self.mainContentContainer, 3)

        # Add the content container to the main layout
        self.layout.addWidget(self.contentContainer)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Initialize the stopwatch and links counter
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStopwatch)
        self.timer.start(1000)  # Update every second


        # Set the layout for the widget
        self.setLayout(self.layout)

    def getTitleFromUrl(self, url):
        # Fetch the content of the page
        response = requests.get(url)
        if response.status_code != 200:
            return "Unable to fetch the page"

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title from the <title> tag and clean it up
        # Wikipedia titles end with " - Wikipedia", which we remove
        pageTitle = soup.title.string.split(" - Wikipedia")[0]

        return pageTitle

    def updateStopwatch(self):
        self.startTime += 1
        self.stopwatchLabel.setText(self.formatTime(self.startTime))

    def formatTime(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def handleLinkClicked(self, url):
        self.linksUsed += 1
        self.linksUsedLabel.setText("Links Used: " + str(self.linksUsed))
        # Convert the QUrl object to a string
        titleString = self.getTitleFromUrl(url.toString())
        # Add the title to previous links if it's not already there
        if titleString not in [self.previousLinksList.item(i).text() for i in range(self.previousLinksList.count())]:
            self.previousLinksList.addItem(titleString)
        # Navigate the webView to the clicked URL
        self.webView.setUrl(url)
