from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QDialog
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtGui import QIcon
from bs4 import BeautifulSoup
import requests
from src.gui.components.WikipediaDarkTheme import WikipediaDarkTheme
from src.gui.components.ConfettiEffect import ConfettiWidget

class SoloGamePage(QWidget):

    def __init__(self, tabWidget, start_url, end_url, parent=None):
        super(SoloGamePage, self).__init__(parent)
        self.tabWidget = tabWidget  # Assuming you need to use tabWidget as well
        self.start_url = start_url
        self.end_url = end_url
        self.startTime = 0
        self.linksUsed = -1  # Start at -1 to account for the initial page
        self.darkModeApplied = False  # Track if dark mode has been applied
        self.initUI()  # Initialize the UI components

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
        self.stopwatchLabel.setStyleSheet("font-size: 26px")
        self.sidebarLayout.addWidget(self.stopwatchLabel)

        self.linksUsedLabel = QLabel("Links Used: " + str(self.linksUsed))
        self.linksUsedLabel.setStyleSheet("font-size: 16px")
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
        self.topBarLabel.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        self.mainContentLayout.addWidget(self.topBarLabel)

        # Initialize and configure the web view with Wikipedia dark theme
        self.webView = QWebEngineView()
        
        # Set up Wikipedia dark theme using the official mwclientpreferences cookie
        WikipediaDarkTheme.setupDarkTheme(self.webView)
        
        # Hide the webview initially to prevent flash of light content
        self.webView.setVisible(False)
        
        # Set initial dark background to prevent any flash
        self.webView.setStyleSheet("background-color: #101418;")
        
        # Connect signals before loading
        self.webView.page().loadStarted.connect(self.onLoadStarted)
        self.webView.urlChanged.connect(self.handleLinkClicked)
        self.webView.page().loadFinished.connect(self.onPageLoaded)
        self.webView.urlChanged.connect(self.onUrlChanged)
        
        # Ensure Vector 2022 skin is used for dark mode support
        start_url_with_skin = WikipediaDarkTheme.ensureVector2022Skin(self.start_url)
        end_url_with_skin = WikipediaDarkTheme.ensureVector2022Skin(self.end_url)
        
        # Update the URLs to use Vector 2022 skin
        self.start_url = start_url_with_skin
        self.end_url = end_url_with_skin
        
        # Start loading the page
        self.webView.load(QUrl(self.start_url))
        
        # Show the webview after a brief delay to ensure dark theme is applied
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.showWebView)
        
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
        
        # Create confetti widget (initially hidden)
        self.confetti_widget = ConfettiWidget(self)
        self.confetti_widget.hide()

    def onLoadStarted(self):
        """Handle page load started - dark theme is already set via cookies"""
        print("🚀 WikiRace: Page load started - Wikipedia dark theme should be active via mwclientpreferences cookie")
        print(f"🚀 WikiRace: Loading URL: {self.webView.url().toString()}")

    def onPageLoaded(self, success):
        """Handle page load finished - verify dark theme was applied"""
        if success:
            print("✅ WikiRace: Page loaded successfully with Wikipedia dark theme")
            print(f"✅ WikiRace: Final URL: {self.webView.url().toString()}")
            # Verify dark mode was applied (for debugging)
            print("🔍 WikiRace: Running dark mode verification...")
            WikipediaDarkTheme.verifyDarkModeApplied(self.webView)
            
            # Also check what cookies are actually in the browser
            print("🍪 WikiRace: Checking cookies in browser...")
            WikipediaDarkTheme.checkCookiesInBrowser(self.webView)
            
            # If dark theme wasn't applied properly, force it
            print("🔧 WikiRace: Attempting to force dark theme as fallback...")
            WikipediaDarkTheme.forceDarkTheme(self.webView)
            
            # Hide Wikipedia navigation elements to show only main content
            print("🔧 WikiRace: Hiding Wikipedia navigation elements...")
            WikipediaDarkTheme.hideNavigationElements(self.webView)
            
            self.darkModeApplied = True
        else:
            print("❌ WikiRace: Page load failed")

    def onUrlChanged(self, url):
        """Handle URL changes - ensure Vector 2022 skin is used"""
        # Ensure the new URL uses Vector 2022 skin for dark mode support
        url_str = url.toString()
        if "wikipedia.org" in url_str and "useskin=vector-2022" not in url_str:
            new_url = WikipediaDarkTheme.ensureVector2022Skin(url_str)
            if new_url != url_str:
                self.webView.load(QUrl(new_url))
                return
        self.darkModeApplied = False  # Reset flag for new page
        
        # Schedule hiding navigation elements after a brief delay to ensure page is loaded
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, lambda: WikipediaDarkTheme.hideNavigationElements(self.webView))

    def showWebView(self):
        """Show the webview after dark theme has been applied"""
        self.webView.setVisible(True)

    def getTitleFromUrl(self, url):
        try:
            # First try to get title from Wikipedia API (more reliable)
            if "wikipedia.org" in url and "curid=" in url:
                page_id = url.split("curid=")[1].split("&")[0]
                return self.getTitleFromPageId(page_id)
            
            # Fallback to HTML parsing with proper headers
            headers = {
                'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
            }
            
            # Fetch the content of the page with proper headers
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"HTTP {response.status_code} error for {url}")
                return "Unable to fetch the page"

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the title from the <title> tag and clean it up
            # Wikipedia titles end with " - Wikipedia", which we remove
            if soup.title and soup.title.string:
                pageTitle = soup.title.string.split(" - Wikipedia")[0]
                return pageTitle
            else:
                print(f"No title found for {url}")
                return "Unknown Page"
                
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            return "Unable to fetch the page"
        except Exception as e:
            print(f"Unexpected error for {url}: {e}")
            return "Unable to fetch the page"
    
    def getTitleFromPageId(self, page_id):
        """Get page title from Wikipedia API using page ID."""
        try:
            headers = {
                'User-Agent': 'WikiRace Game/1.0 (https://github.com/ianwagers/wikirace)'
            }
            
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "pageids": page_id,
                "prop": "info",
                "inprop": "displaytitle"
            }
            
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "query" in data and "pages" in data["query"]:
                    pages = data["query"]["pages"]
                    if page_id in pages:
                        page_info = pages[page_id]
                        if "title" in page_info:
                            return page_info["title"]
            
            print(f"Could not get title for page ID {page_id}")
            return f"Page {page_id}"
            
        except Exception as e:
            print(f"Error getting title for page ID {page_id}: {e}")
            return f"Page {page_id}"

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

        # Check if the URL matches the destination URL
        self.checkEndGame(url)

    # Adjust the checkEndGame method in SoloGamePage to include the tabWidget and homePageIndex
    def checkEndGame(self, newUrl):
        currentPage = self.getTitleFromUrl(newUrl.toString())
        destinationPage = self.getTitleFromUrl(self.end_url)
        if currentPage == destinationPage:
            # Stop the timer immediately
            self.timer.stop()
            
            # Wait for page to load, then show confetti, then dialog
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self.showConfettiAndDialog)  # Wait 500ms for page load
    
    def showConfettiAndDialog(self):
        """Show confetti first, then dialog after confetti finishes"""
        # Show confetti on the current game page
        self.triggerConfetti()
        
        # After confetti finishes (4 seconds), show the dialog
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(4000, self.showEndGameDialog)
    
    def triggerConfetti(self):
        """Trigger confetti effect on the game page"""
        # Position confetti widget to cover the entire game page
        self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
        self.confetti_widget.raise_()  # Bring to front
        self.confetti_widget.startConfetti(4000)  # 4 second QUICK confetti effect
    
    def resizeEvent(self, event):
        """Handle resize events to reposition confetti widget"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti_widget'):
            self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
    
    def showEndGameDialog(self):
        """Show the end game dialog"""
        homePageIndex = 0  # HomePage is typically at index 0
        dialog = EndGameDialog(self, self.tabWidget, homePageIndex)
        dialog.exec()


class EndGameDialog(QDialog):
    def __init__(self, gamePage, tabWidget, homePageIndex, parent=None):
        super(EndGameDialog, self).__init__(parent)
        self.gamePage = gamePage
        self.tabWidget = tabWidget
        self.homePageIndex = homePageIndex
        self.setWindowTitle("Game Over")
        self.setWindowIcon(QIcon('C:/Project_Workspace/WikiRace/src/resources/icons/game_icon.ico'))
        # self.setWindowIcon(QIcon(self.projectPath + 'resources/icons/game_icon.ico'))
        self.setStyleSheet("""
            QDialog {
                background-color: #101418;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
                border-color: #00FFFF;
            }
        """)
        self.setFixedSize(400, 280)  # Further increased size to prevent text cutoff
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding to prevent text cutoff
        layout.setSpacing(10)  # Add spacing between elements

        messageLabel = QLabel("Congratulations!")
        messageLabel.setStyleSheet("""
            font-size: 24px; 
            color: #00FFFF; 
            padding: 10px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            font-weight: bold;
        """)
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(messageLabel)
        messageSubscript = QLabel("You finished the race!")
        messageSubscript.setAlignment(Qt.AlignmentFlag.AlignCenter)
        messageSubscript.setStyleSheet("""
            font-size: 14px; 
            padding: 6px;
            color: #E0E0E0;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        """) 
        layout.addWidget(messageSubscript)

        totalTimeLabel = QLabel("Total time (hh:mm:ss): " + self.gamePage.formatTime(self.gamePage.startTime))
        totalTimeLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        totalTimeLabel.setStyleSheet("color: #E0E0E0; font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;")
        layout.addWidget(totalTimeLabel)

        totalLinksLabel = QLabel("Total Links: " + str(self.gamePage.linksUsed))
        totalLinksLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        totalLinksLabel.setStyleSheet("color: #E0E0E0; font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;")
        layout.addWidget(totalLinksLabel)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.returnToHomePage)
        layout.addWidget(closeButton)

    def returnToHomePage(self):
        self.tabWidget.setCurrentIndex(self.homePageIndex)
        self.close()

