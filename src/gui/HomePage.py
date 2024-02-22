from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QFrame, QDialog, QComboBox, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from src.logic.GameLogic import GameLogic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout


class HomePage(QWidget):
    def __init__(self, tabWidget, mainApplication):
        super().__init__()
        self.tabWidget = tabWidget
        self.mainApplication = mainApplication

        # Check if tabWidget has a layout, if not, set a new layout
        if tabWidget.layout() is None:
            tabWidget.setLayout(QVBoxLayout())  # Or any other layout

        self.setStyles()

        # Now it's safe to get and modify the layout
        self.layout = tabWidget.layout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Title Image  # Placeholder for title image
        self.titleImage = QLabel()
        self.titleImage.setPixmap(QPixmap(mainApplication.projectPath + "resources/TitlePageHeader.png"))  # Placeholder path
        self.titleImage.setScaledContents(True)
        self.titleImage.setMaximumSize(350, 325)
        self.titleImage.setAlignment(Qt.AlignCenter)

                # Top bar layout
        # self.topBarLayout = QHBoxLayout()
        # self.topBarLayout.addWidget(self.titleImage, alignment=Qt.AlignCenter)
        
        self.layout.addWidget(self.titleImage, alignment=Qt.AlignCenter)

        # Title subscript
        self.titleSubscript = QLabel("Version 1.4 [BETA]")
        self.titleSubscript.setStyleSheet("font-size: 12px;")
        self.titleSubscript.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.titleSubscript)
        

        # Frame for the buttons
        self.buttonsFrame = QFrame()
        self.buttonsLayout = QHBoxLayout(self.buttonsFrame)
        self.buttonsLayout.setContentsMargins(10, 0, 10, 0) # Reduced bottom margin to decrease whitespace

        # Buttons
        self.soloGameButton = QPushButton("Solo Race")
        self.soloGameButton.setMinimumHeight(40)
        self.soloGameButton.setMaximumWidth(500)
        self.soloGameButton.setMinimumWidth(200)
        self.soloGameButton.setStyleSheet("font-size: 16px;")

        self.multiplayerButton = QPushButton("Multiplayer")
        self.multiplayerButton.setMinimumHeight(40)
        self.multiplayerButton.setMinimumWidth(200)
        self.multiplayerButton.setMaximumWidth(500)
        self.multiplayerButton.setStyleSheet("font-size: 16px;")

        self.soloGameButton.setCheckable(True)
        self.multiplayerButton.setCheckable(True)
        
        self.settingsButton = QPushButton()
        self.settingsButton.setIcon(QIcon(mainApplication.projectPath + "resources/icons/settings_icon.png"))  # Placeholder path
        self.settingsButton.setIconSize(QSize(28, 28))
        self.settingsButton.setFlat(True)
        self.settingsButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        # Adding buttons to the layout
        self.buttonsLayout.addWidget(self.soloGameButton)
        self.buttonsLayout.addWidget(self.multiplayerButton)
        self.buttonsLayout.addWidget(self.settingsButton)

        # Adjusting spacing to reduce excess whitespace
        self.buttonsLayout.addStretch(1)
        self.layout.addWidget(self.buttonsFrame)

        # Web view        
        self.webView = QWebEngineView()
        self.webView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.webView.load(QUrl("https://en.wikipedia.org/wiki/Main_Page"))
        self.layout.addWidget(self.webView)

        self.webView.page().loadFinished.connect(self.injectCSS)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Button connections
        self.soloGameButton.clicked.connect(self.onSoloGameClicked)
        self.multiplayerButton.clicked.connect(self.onMultiplayerClicked)
        self.settingsButton.clicked.connect(self.onSettingsClicked)

        # Create an instance of GameLogic before calling startGame()
        self.game_logic_instance = GameLogic()

    def injectCSS(self):
        # CSS to hide the entire VectorHeaderContainer and its contents
        css = """
        .vector-header-container {display: none !important;}
        """
        # JavaScript to inject CSS
        js = f"""
        var css = `{css}`;
        var style = document.createElement('style');
        if (style.styleSheet) {{
            style.styleSheet.cssText = css;
        }} else {{
            style.appendChild(document.createTextNode(css));
        }}
        document.head.appendChild(style);
        """
        self.webView.page().runJavaScript(js)

    def onSoloGameClicked(self):
            dialog = CustomGameDialog(self)
            if dialog.exec_():
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
        dialog.exec_()
        ''' # Placeholder for multiplayer game
        if not hasattr(self.mainApplication, 'multiplayerPage') or self.tabWidget.indexOf(self.mainApplication.multiplayerPage) == -1:
            self.mainApplication.addMultiplayerTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.multiplayerPage)
            self.tabWidget.setCurrentIndex(index)
        '''
    
    def onSettingsClicked(self):
        dialog = UnderConstructionDialog(self)
        dialog.exec_()
        ''' # Placeholder for settings page
        if not hasattr(self.mainApplication, 'settingsPage') or self.tabWidget.indexOf(self.mainApplication.settingsPage) == -1:
            self.mainApplication.addSettingsTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.settingsPage)
            self.tabWidget.setCurrentIndex(index)
        '''

    def openLinkInWebView(self, url):
        # Convert string URL to QUrl object
        qurl = QUrl(url)
        self.webView.load(qurl)

    def setStyles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #FFFFFF; /* General background */
            color: #154360; /* General text color */
        }

        QPushButton {
            background-color: #D3D3D3; /* Light grey for buttons */
            border: 1px solid #9FC3E8;
            padding: 5px;
            border-radius: 5px;
        }

        QPushButton:hover {
            background-color: #85C1E9; /* Hover state */
        }

        QPushButton:pressed {
            background-color: #5499C7; /* Pressed state */
        }

        QLabel {
            font-size: 14px;
        }

        QMainWindow {
            background-color: #D3D3D3; /* Light grey for main window background */
        }
        """)

        # Light Blue Theme with QTabWidget, adjusted for light grey in specific areas
        self.tabWidget.setStyleSheet("""
        QTabWidget::pane { /* The tab widget frame */
            border-top: 2px solid #DADCDF; /* Light grey to match the tab bar */
        }

        QTabBar::tab {
            background: #D3D3D3; /* Light grey for unselected tabs */
            color: #154360;
            padding: 5px;
            border: 1px solid #9FC3E8;
            border-bottom-color: #D3D3D3; /* Light grey to match the tab background */
        }

        QTabBar::tab:selected, QTabBar::tab:hover {
            background: #D6EAF8; /* Original light blue for selected/hovered tab */
            color: #154360;
        }

        QWidget {
            background-color: #FFFFFF; /* Keeping original light blue for general widgets */
            color: #154360;
        }
        """)

class CustomGameDialog(QDialog):
    def __init__(self, homePage):
        super().__init__(homePage)
        self.homePage = homePage
        self.setWindowTitle('Race Setup')
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)  # Added padding around the dialog content

        # Layout for starting page selection
        startingPageLayout = QHBoxLayout()
        startingPageLabel = QLabel('Starting Page:')
        startingPageLabel.setStyleSheet("QLabel { font-weight: bold; color: #3366cc; } ") 
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
        self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        self.layout.addWidget(self.customStartPageEdit)

        # Layout for ending page selection
        endingPageLayout = QHBoxLayout()
        endingPageLabel = QLabel('Ending Page:')
        endingPageLabel.setStyleSheet("QLabel { font-weight: bold; color: #3366cc; } ") 
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
        self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
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
        
        # Change background color based on the selection
        if isCustomStart:
            self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: white; }")
        else:
            # Set to the default or original background color
            self.customStartPageEdit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")  # Example color
        
        if isCustomEnd:
            self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: white; }")
        else:
            # Set to the default or original background color
            self.customEndPageEdit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")  # Example color

class UnderConstructionDialog(QDialog):
    def __init__(self, parent=None):
        super(UnderConstructionDialog, self).__init__(parent)
        self.setWindowTitle("L")
        self.setStyleSheet("background-color: #FFFFFF")
        self.setFixedSize(300, 180)  # Adjust size as needed
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        messageLabel = QLabel("i'll work on this..")
        messageLabel.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        messageLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(messageLabel)
        messageSubscript = QLabel("L")
        messageSubscript.setAlignment(Qt.AlignCenter)
        messageSubscript.setStyleSheet("font-size: 40px; padding: 6px;") 
        layout.addWidget(messageSubscript)

        closeButton = QPushButton("Close")
        closeButton.setStyleSheet("background-color: #D3D3D3")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)
