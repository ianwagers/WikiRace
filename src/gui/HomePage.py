from PyQt6.QtGui import QIcon, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QFrame, QDialog, QComboBox, QLineEdit
from PyQt6.QtCore import Qt, QSize, QUrl, QRect
from src.logic.GameLogic import GameLogic
from src.gui.components.WikipediaDarkTheme import WikipediaDarkTheme
from src.gui.components.ConfettiEffect import ConfettiWidget


class HomePage(QWidget):

    def __init__(self, tabWidget, mainApplication):
        super().__init__()
        self.darkModeApplied = False  # Track if dark mode has been applied
        self.tabWidget = tabWidget
        self.mainApplication = mainApplication
        
        # ===== TITLE POSITIONING CONFIGURATION =====
        # Easily modify these values to adjust "Race" text positioning
        self.RACE_TEXT_VERTICAL_OFFSET = 0  # Negative values move text up, positive down
        self.RACE_TEXT_HORIZONTAL_OFFSET = 10  # Negative values move text left, positive right
        self.RACE_TEXT_MARGIN_LEFT = 0  # Additional left margin
        self.RACE_TEXT_MARGIN_TOP = 0   # Additional top margin
        # ===========================================

        # Check if tabWidget has a layout, if not, set a new layout
        if tabWidget.layout() is None:
            tabWidget.setLayout(QVBoxLayout())  # Or any other layout

        self.setStyles()

        # Now it's safe to get and modify the layout
        self.layout = tabWidget.layout()
        self.layout.setContentsMargins(20, 15, 20, 20)
        self.layout.setSpacing(8)

        # Title Image - WIKIRACE Logo (single word with WIKI as one block and RACE with gradient)
        self.titleImage = QLabel()
        # Use HTML to create the stylized WIKIRACE text with WIKI as one block and RACE with gradient
        self.titleImage.setText("""
        <html>
        <head>
        <style>
        .wikirace-logo {
            font-family: 'Linux Libertine', 'Times New Roman', 'Times', serif;
            font-size: 36px;
            font-weight: 400;
            color: #ffffff;
            background: #101418;
            letter-spacing: 1px;
            font-style: normal;
            padding: 1px 16px;
            border-radius: 6px;
        }
        .large-w {
            font-size: 48px;
            font-weight: 600;
        }
        .race-text {
            font-family: 'Linux Libertine', 'Times New Roman', 'Times', serif;
            font-size: 36px;
            font-weight: 400;
            background: linear-gradient(90deg, #00FFFF 0%, #8A2BE2 50%, #FF00FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-style: italic;
            letter-spacing: 1px;
        }
        </style>
        </head>
        <body>
        <div class="wikirace-logo">
            <span class="large-w">W</span>IKI<span class="race-text">RACE</span>
        </div>
        </body>
        </html>
        """)
        
        self.titleImage.setScaledContents(True)
        self.titleImage.setMaximumSize(280, 50)
        self.titleImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a container for the single logo
        self.logoContainer = QFrame()
        self.logoLayout = QHBoxLayout(self.logoContainer)
        self.logoLayout.setContentsMargins(0, 0, 0, 0)
        self.logoLayout.setSpacing(0)
        self.logoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add the single WIKIRACE logo to container
        self.logoLayout.addWidget(self.titleImage, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(self.logoContainer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title subscript with modern styling - positioned right edge with low opacity
        self.titleSubscript = QLabel("v1.4 [BETA]")
        self.titleSubscript.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: rgba(102, 102, 102, 0.6);
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 300;
                background: transparent;
            }
        """)
        self.titleSubscript.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.titleSubscript.setContentsMargins(0, 0, 20, 0)
        self.layout.addWidget(self.titleSubscript)
        

        # Frame for the buttons with refined card styling
        self.buttonsFrame = QFrame()
        self.buttonsFrame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 8px;
                border: 1px solid #404040;
                padding: 8px;
            }
        """)
        # Set maximum width to prevent floating appearance
        self.buttonsFrame.setMaximumWidth(400)
        self.buttonsLayout = QHBoxLayout(self.buttonsFrame)
        self.buttonsLayout.setContentsMargins(8, 8, 8, 8)
        self.buttonsLayout.setSpacing(6)
        self.buttonsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Modern styled buttons with proper sizing (15-20% smaller)
        self.soloGameButton = QPushButton("Solo Race")
        self.soloGameButton.setMinimumHeight(36)
        self.soloGameButton.setMinimumWidth(115)
        self.soloGameButton.setMaximumWidth(145)
        self.soloGameButton.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
                font-weight: 500;
                padding: 0 14px;
                height: 36px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
                border-color: #00FFFF;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
                border-color: #8A2BE2;
            }
            QPushButton:focus {
                outline: 2px solid #7dd3fc;
            }
        """)

        self.multiplayerButton = QPushButton("Multiplayer")
        self.multiplayerButton.setMinimumHeight(36)
        self.multiplayerButton.setMinimumWidth(115)
        self.multiplayerButton.setMaximumWidth(145)
        self.multiplayerButton.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
                font-weight: 500;
                padding: 0 14px;
                height: 36px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
                border-color: #00FFFF;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
                border-color: #8A2BE2;
            }
            QPushButton:focus {
                outline: 2px solid #7dd3fc;
            }
        """)

        self.soloGameButton.setCheckable(True)
        self.multiplayerButton.setCheckable(True)
        
        self.settingsButton = QPushButton("Settings")
        self.settingsButton.setMinimumHeight(36)
        self.settingsButton.setMinimumWidth(115)
        self.settingsButton.setMaximumWidth(145)
        self.settingsButton.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
                font-weight: 500;
                padding: 0 14px;
                height: 36px;
            }
            QPushButton:hover {
                background-color: #2f2f2f;
                border-color: #00FFFF;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
                border-color: #8A2BE2;
            }
            QPushButton:focus {
                outline: 2px solid #7dd3fc;
            }
        """)

        # Adding buttons to the layout
        self.buttonsLayout.addWidget(self.soloGameButton)
        self.buttonsLayout.addWidget(self.multiplayerButton)
        self.buttonsLayout.addWidget(self.settingsButton)

        self.layout.addWidget(self.buttonsFrame)

        # Wikipedia content area with dark theme container
        self.contentFrame = QFrame()
        self.contentFrame.setStyleSheet("""
            QFrame {
                background-color: #101418;
                border-radius: 12px;
                border: 1px solid #2a2a2a;
                margin: 10px;
            }
        """)
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        
        # Web view with Wikipedia dark theme
        self.webView = QWebEngineView()
        self.webView.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.webView.setStyleSheet("""
            QWebEngineView {
                background-color: #101418;
                border-radius: 12px;
            }
        """)
        
        # Set up Wikipedia dark theme using the official mwclientpreferences cookie
        WikipediaDarkTheme.setupDarkTheme(self.webView)
        
        # Hide the webview initially to prevent flash of light content
        self.webView.setVisible(False)
        
        # Connect signals before loading
        self.webView.page().loadStarted.connect(self.onLoadStarted)
        self.webView.page().loadFinished.connect(self.onPageLoaded)
        self.webView.urlChanged.connect(self.onUrlChanged)
        
        # Ensure Vector 2022 skin is used for dark mode support
        main_page_url = WikipediaDarkTheme.ensureVector2022Skin("https://en.wikipedia.org/wiki/Main_Page")
        
        # Start loading the page
        self.webView.load(QUrl(main_page_url))
        self.contentLayout.addWidget(self.webView)
        
        self.layout.addWidget(self.contentFrame)
        
        # Show the webview after a brief delay to ensure dark theme is applied
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.showWebView)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Button connections
        self.soloGameButton.clicked.connect(self.onSoloGameClicked)
        self.multiplayerButton.clicked.connect(self.onMultiplayerClicked)
        self.settingsButton.clicked.connect(self.onSettingsClicked)

        # Create an instance of GameLogic before calling startGame()
        self.game_logic_instance = GameLogic()
        
        # Create confetti widget (initially hidden)
        self.confetti_widget = ConfettiWidget(self)
        self.confetti_widget.hide()


    def onLoadStarted(self):
        """Handle page load started - dark theme is already set via cookies"""
        print("🚀 WikiRace: HomePage - Page load started - Wikipedia dark theme should be active via mwclientpreferences cookie")
        print(f"🚀 WikiRace: HomePage - Loading URL: {self.webView.url().toString()}")

    def onPageLoaded(self, success):
        """Handle page load finished - verify dark theme was applied"""
        if success:
            print("✅ WikiRace: HomePage - Page loaded successfully with Wikipedia dark theme")
            print(f"✅ WikiRace: HomePage - Final URL: {self.webView.url().toString()}")
            # Verify dark mode was applied (for debugging)
            print("🔍 WikiRace: HomePage - Running dark mode verification...")
            WikipediaDarkTheme.verifyDarkModeApplied(self.webView)
            
            # Also check what cookies are actually in the browser
            print("🍪 WikiRace: HomePage - Checking cookies in browser...")
            WikipediaDarkTheme.checkCookiesInBrowser(self.webView)
            
            # If dark theme wasn't applied properly, force it
            print("🔧 WikiRace: HomePage - Attempting to force dark theme as fallback...")
            WikipediaDarkTheme.forceDarkTheme(self.webView)
            
            # Hide Wikipedia navigation elements to show only main content
            print("🔧 WikiRace: HomePage - Hiding Wikipedia navigation elements...")
            WikipediaDarkTheme.hideNavigationElements(self.webView)
            
            self.darkModeApplied = True
        else:
            print("❌ WikiRace: HomePage - Page load failed")

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
    
    def triggerConfetti(self):
        """Trigger confetti effect when race is completed"""
        # Position confetti widget to cover the entire home page
        self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
        self.confetti_widget.raise_()  # Bring to front
        self.confetti_widget.startConfetti(3000)  # 3 second confetti effect
    
    def resizeEvent(self, event):
        """Handle resize events to reposition confetti widget"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti_widget'):
            self.confetti_widget.setGeometry(0, 0, self.width(), self.height())

    def onSoloGameClicked(self):
            dialog = CustomGameDialog(self)
            if dialog.exec():
                starting_page_choice = dialog.startPageCombo.currentText()
                ending_page_choice = dialog.endPageCombo.currentText()
                custom_starting_page = dialog.customStartPageEdit.text() if starting_page_choice == 'Custom' else starting_page_choice
                custom_ending_page = dialog.customEndPageEdit.text() if ending_page_choice == 'Custom' else ending_page_choice

                self.start_url, self.end_url = self.game_logic_instance.startGame(self, custom_starting_page, custom_ending_page)
                self.addSoloGameTab(self.start_url, self.end_url)

    def addSoloGameTab(self, start_url, end_url):
        if not hasattr(self.mainApplication, 'soloGamePage'):
            self.mainApplication.addSoloGameTab(start_url, end_url)
            index = self.tabWidget.indexOf(self.mainApplication.soloGamePage)
            self.tabWidget.setCurrentIndex(index)
        else:
            index = self.tabWidget.indexOf(self.mainApplication.soloGamePage)
            self.mainApplication.closeTab(index)
            self.mainApplication.addSoloGameTab(start_url, end_url)
            self.tabWidget.setCurrentIndex(index)

    def onMultiplayerClicked(self):
        dialog = UnderConstructionDialog(self)
        dialog.exec()
        ''' # Placeholder for multiplayer game
        if not hasattr(self.mainApplication, 'multiplayerPage') or self.tabWidget.indexOf(self.mainApplication.multiplayerPage) == -1:
            self.mainApplication.addMultiplayerTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.multiplayerPage)
            self.tabWidget.setCurrentIndex(index)
        '''
    
    def onSettingsClicked(self):
        dialog = UnderConstructionDialog(self)
        dialog.exec()
        ''' # Placeholder for settings page
        if not hasattr(self.mainApplication, 'settingsPage') or self.tabWidget.indexOf(self.mainApplication.settingsPage) == -1:
            self.mainApplication.addSettingsTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.settingsPage)
            self.tabWidget.setCurrentIndex(index)
        '''

    def openLinkInWebView(self, url):
        # Ensure Vector 2022 skin is used for dark mode support
        url_with_skin = WikipediaDarkTheme.ensureVector2022Skin(url)
        # Convert string URL to QUrl object
        qurl = QUrl(url_with_skin)
        self.webView.load(qurl)
        # Dark mode will be applied automatically via mwclientpreferences cookie

    def setStyles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #101418; /* Updated dark background */
            color: #E0E0E0; /* Light text */
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }

        QLabel {
            color: #E0E0E0;
            font-size: 14px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }

        QMainWindow {
            background-color: #101418; /* Updated dark main window background */
        }
        """)

        # Dark Theme for QTabWidget
        self.tabWidget.setStyleSheet("""
        QTabWidget::pane {
            border-top: 2px solid #404040;
            background-color: #101418;
        }

        QTabBar::tab {
            background: #2D2D2D;
            color: #E0E0E0;
            padding: 8px 16px;
            border: 1px solid #404040;
            border-bottom-color: #2D2D2D;
            border-radius: 6px 6px 0px 0px;
            margin-right: 2px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 500;
        }

        QTabBar::tab:selected, QTabBar::tab:hover {
            background: #3E3E3E;
            color: #00FFFF;
            border-color: #00FFFF;
        }

        QWidget {
            background-color: #101418;
            color: #E0E0E0;
        }
        """)

class CustomGameDialog(QDialog):
    def __init__(self, homePage):
        super().__init__(homePage)
        self.homePage = homePage
        self.setWindowTitle('Race Setup')
        self.setStyleSheet("""
            QDialog {
                background-color: #101418;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }
            QComboBox:hover {
                border-color: #00FFFF;
            }
            QLineEdit {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }
            QLineEdit:focus {
                border-color: #00FFFF;
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
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Layout for starting page selection
        startingPageLayout = QHBoxLayout()
        startingPageLabel = QLabel('Starting Page:')
        startingPageLabel.setStyleSheet("QLabel { font-weight: bold; color: #00FFFF; } ") 
        self.startPageCombo = QComboBox()
        self.startPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 'Historical Events', 'Random', 'Custom'])
        if self.startPageCombo.currentText() == 'Custom':
            self.startPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        startingPageLayout.addWidget(startingPageLabel)
        startingPageLayout.addWidget(self.startPageCombo)
        self.layout.addLayout(startingPageLayout)

        # Line edit for custom starting page
        self.customStartPageEdit = QLineEdit()
        self.customStartPageEdit.setPlaceholderText('Enter custom starting page')
        self.customStartPageEdit.setEnabled(False)
        self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")
        self.layout.addWidget(self.customStartPageEdit)

        # Layout for ending page selection
        endingPageLayout = QHBoxLayout()
        endingPageLabel = QLabel('Ending Page:')
        endingPageLabel.setStyleSheet("QLabel { font-weight: bold; color: #00FFFF; } ") 
        self.endPageCombo = QComboBox()
        self.endPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 'Historical Events', 'Random', 'Custom'])
        if self.endPageCombo.currentText() == 'Custom':
            self.endPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        endingPageLayout.addWidget(endingPageLabel)
        endingPageLayout.addWidget(self.endPageCombo)
        self.layout.addLayout(endingPageLayout)

        # Line edit for custom ending page
        self.customEndPageEdit = QLineEdit()
        self.customEndPageEdit.setPlaceholderText('Enter custom ending page')
        self.customEndPageEdit.setEnabled(False)
        self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")
        self.layout.addWidget(self.customEndPageEdit)

        # Start Game button
        self.startGameButton = QPushButton('Start Race!')
        self.layout.addWidget(self.startGameButton)
        
        # Connect signals
        self.startPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        self.endPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        self.startGameButton.clicked.connect(self.startGameAndClose)

        # Set minimum dialog size for better UI experience
        self.setMinimumSize(275, 175)  # Example improvement for resizing
        
    def startGameAndClose(self):
        # Here you can add any logic you need before closing the dialog
        self.startGameButton.clicked.connect(lambda: self.startGameAndClose(self.homePage))  # Assuming homePage is accessible. If not, adjust accordingly.
        self.accept()  # This will close the dialog

    def toggleCustomEntry(self):
        isCustomStart = self.startPageCombo.currentText() == 'Custom'
        isCustomEnd = self.endPageCombo.currentText() == 'Custom'
        
        self.customStartPageEdit.setEnabled(isCustomStart)
        self.customEndPageEdit.setEnabled(isCustomEnd)
        
        # Change background color based on the selection (dark mode)
        if isCustomStart:
            self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")
        else:
            # Set to the default dark background color
            self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")
        
        if isCustomEnd:
            self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")
        else:
            # Set to the default dark background color
            self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: #2D2D2D; color: #E0E0E0; }")

class UnderConstructionDialog(QDialog):
    def __init__(self, parent=None):
        super(UnderConstructionDialog, self).__init__(parent)
        self.setWindowTitle("Under Construction")
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
        self.setFixedSize(300, 180)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        messageLabel = QLabel("Coming Soon...")
        messageLabel.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            padding: 10px;
            color: #00FFFF;
        """)
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(messageLabel)
        
        messageSubscript = QLabel("🚧")
        messageSubscript.setAlignment(Qt.AlignmentFlag.AlignCenter)
        messageSubscript.setStyleSheet("""
            font-size: 40px; 
            padding: 6px;
            color: #8A2BE2;
        """) 
        layout.addWidget(messageSubscript)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)
