
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QListWidget
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super(CustomWebEnginePage, self).__init__(parent)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            # Handle the link click here, e.g., emit a signal or call a method
            print(f"Link clicked: {url.toString()}")
            return False  # Prevent default navigation
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class SoloGamePage(QWidget):
    def __init__(self, tabWidget, parent=None):
        super(SoloGamePage, self).__init__(parent)
        self.webView = QWebEngineView(self)
        self.initUI()
        self.layout().addWidget(self.webView)  # Assuming you have a layout setup
        self.webView.linkClicked.connect(self.handleLinkClicked)
        
        
        # Initialize the stopwatch and links counter
        self.startTime = 0
        self.linksUsed = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStopwatch)
        self.timer.start(1000)  # Update every second

    def initUI(self):
        # Main layout
        self.layout = QHBoxLayout(self)

        # Sidebar layout (25% width)
        self.sidebarLayout = QVBoxLayout()
        
        # Stopwatch label
        self.stopwatchLabel = QLabel("00:00:00")
        self.stopwatchLabel.setStyleSheet("font-size: 20px")
        self.sidebarLayout.addWidget(self.stopwatchLabel)
        
        # Links used counter
        self.linksUsedLabel = QLabel("Links Used: 0")
        self.sidebarLayout.addWidget(self.linksUsedLabel)
        
        # Previous links list
        self.previousLinksList = QListWidget()
        self.sidebarLayout.addWidget(self.previousLinksList)

        # Adding sidebar to the main layout with 25% width
        self.layout.addLayout(self.sidebarLayout, 1)

        # Web view (75% width)
        self.webView = QWebEngineView()
        self.webView.load(QUrl("https://en.wikipedia.org"))
        self.layout.addWidget(self.webView, 3)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Call handleLinkClicked on links
        self.webView.linkClicked.connect(self.handleLinkClicked)

    def updateStopwatch(self):
        self.startTime += 1
        self.stopwatchLabel.setText(self.formatTime(self.startTime))

    def formatTime(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Placeholder method to simulate link click
    def handleLinkClicked(self, url):
        # Increment the links used counter
        self.linksUsed += 1
        # Update any UI component that displays the link history, if applicable
        # For example, adding the url to a QListWidget or similar
        self.linksHistoryWidget.addItem(url.toString())
        # Ensure the web view navigates to the clicked link
        self.webView.setUrl(url)
