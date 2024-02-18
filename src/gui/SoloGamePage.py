from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QListWidget
from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class SoloGamePage(QWidget):
    def __init__(self, parent=None):
        super(SoloGamePage, self).__init__(parent)
        self.initUI()  # Initialize the UI components
        
        # Now that self.webView is properly initialized in initUI, you don't need to add it to the layout again here.
        # Just proceed with any additional configuration if needed.

    def initUI(self):
        # Main layout
        self.layout = QHBoxLayout(self)

        # Sidebar layout (25% width)
        self.sidebarLayout = QVBoxLayout()
        
        # Initialize and configure the web view first
        self.webView = QWebEngineView()
        #TODO This should be passed the starting page from GameLogic 
        self.webView.load(QUrl("https://en.wikipedia.org"))
        self.webView.urlChanged.connect(self.handleLinkClicked)

        # Stopwatch label, links used counter, and previous links list setup
        self.stopwatchLabel = QLabel("00:00:00")
        self.stopwatchLabel.setStyleSheet("font-size: 20px")
        self.sidebarLayout.addWidget(self.stopwatchLabel)

        self.linksUsedLabel = QLabel("Links Used: 0")
        self.sidebarLayout.addWidget(self.linksUsedLabel)

        self.previousLinksList = QListWidget()
        self.sidebarLayout.addWidget(self.previousLinksList)

        # Adding sidebar to the main layout
        self.layout.addLayout(self.sidebarLayout, 1)

        # Add the web view to the layout after it's been initialized
        self.layout.addWidget(self.webView, 3)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Initialize the stopwatch and links counter
        self.startTime = 0
        self.linksUsed = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStopwatch)
        self.timer.start(1000)  # Update every second

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
        # Convert the QUrl object to a string
        urlString = url.toString()
        # Remove the specified prefix from the URL string
        displayString = urlString.replace("https://en.wikipedia.org/wiki/", "")
        # Add the modified string to the previousLinksList
        self.previousLinksList.addItem(displayString)
        # Navigate the webView to the clicked URL
        self.webView.setUrl(url)

