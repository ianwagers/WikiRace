
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QSpacerItem, QFrame, QTabWidget, QDialog, QComboBox, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

import sys
sys.path.append('C:\Project_Workspace\WikiRace')
from src import app
from src.logic.GameLogic import GameLogic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QBoxLayout, QVBoxLayout, QHBoxLayout


class HomePage(QWidget):
    def __init__(self, tabWidget, mainApplication):
        super().__init__()
        self.tabWidget = tabWidget
        self.mainApplication = mainApplication

        # Check if tabWidget has a layout, if not, set a new layout
        if tabWidget.layout() is None:
            tabWidget.setLayout(QVBoxLayout())  # Or any other layout

        self.setStyleSheet("""
        QWidget {
            background-color: #D6EAF8; /* General background */
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
            border-top: 2px solid #7DA2CE;
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
            background-color: #D6EAF8; /* Keeping original light blue for general widgets */
            color: #154360;
        }
        """)


        # Now it's safe to get and modify the layout
        self.layout = tabWidget.layout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
         # Top bar layout
        self.topBarLayout = QHBoxLayout()
        self.settingsButton = QPushButton()
        self.settingsButton.setIcon(QIcon("C://Project_Workspace/WikiRace/src/resources/icons/settings_icon.png"))  # Placeholder path
        self.settingsButton.setIconSize(QSize(40, 40))
        self.settingsButton.setFlat(True)
        self.settingsButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        
        # Spacer to push settings to the right
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.topBarLayout.addItem(self.spacer)
        self.topBarLayout.addWidget(self.settingsButton)

        # Adding top bar layout to main layout
        self.layout.addLayout(self.topBarLayout)

        # Title above the buttons
        self.titleLabel = QLabel('<a href="https://en.wikipedia.org/wiki/Wikiracing">Wikipedia Race</a>')
        self.titleLabel.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.linkActivated.connect(self.openLinkInWebView)
        self.layout.addWidget(self.titleLabel)

        # Title subscript
        self.titleSubscript = QLabel("Version 1.1 [Alpha Asf]")
        self.titleSubscript.setStyleSheet("font-size: 14px;")
        self.titleSubscript.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.titleSubscript)
        

        # Frame for the buttons
        self.buttonsFrame = QFrame()
        self.buttonsLayout = QHBoxLayout(self.buttonsFrame)
        self.buttonsLayout.setContentsMargins(10, 0, 10, 0) # Reduced bottom margin to decrease whitespace

        # Buttons
        self.soloGameButton = QPushButton("Solo Game")
        self.soloGameButton.setMinimumHeight(50)
        self.soloGameButton.setMaximumWidth(300)
        self.soloGameButton.setStyleSheet("font-size: 16px;")
        self.multiplayerButton = QPushButton("Multiplayer")
        self.multiplayerButton.setMinimumHeight(50)
        self.multiplayerButton.setMaximumWidth(300)
        self.multiplayerButton.setStyleSheet("font-size: 16px;")

        self.soloGameButton.setCheckable(True)
        self.multiplayerButton.setCheckable(True)
        self.buttonsLayout.addWidget(self.soloGameButton)
        self.buttonsLayout.addWidget(self.multiplayerButton)

        # Adjusting spacing to reduce excess whitespace
        self.buttonsLayout.addStretch(1)
        

        # Web view
        #self.layout = QVBoxLayout(self)  # Initialize the layout
        self.layout.addWidget(self.buttonsFrame)
        self.webView = QWebEngineView()
        self.webView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.webView.load(QUrl("https://en.wikipedia.org/wiki/Main_Page"))
        self.layout.addWidget(self.webView)

        # Sytling the web view
        # Light Gray Theme - Fixed for Main Window Background
        # Dark Gray Theme - Fixed for Main Window Background



        # Set the layout for the widget
        self.setLayout(self.layout)

        # Button connections
        self.soloGameButton.clicked.connect(self.onSoloGameClicked)
        self.multiplayerButton.clicked.connect(self.onMultiplayerClicked)
        self.settingsButton.clicked.connect(self.onSettingsClicked)

        # Create an instance of GameLogic before calling startGame()
        self.game_logic_instance = GameLogic()

    def onSoloGameClicked(self):
            dialog = CustomGameDialog(self)
            if dialog.exec_():
                starting_page_choice = dialog.startPageCombo.currentText()
                ending_page_choice = dialog.endPageCombo.currentText()
                custom_starting_page = dialog.customStartPageEdit.text() if starting_page_choice == 'Custom' else None
                custom_ending_page = dialog.customEndPageEdit.text() if ending_page_choice == 'Custom' else None
                
                if starting_page_choice == 'Random' and ending_page_choice == 'Random':
                    self.mainApplication.addSoloGameTab()
                    self.game_logic_instance.startGame()
                else:
                    print("[ERROR] Custom start/end not implemented")

    def onMultiplayerClicked(self):
        if not hasattr(self.mainApplication, 'multiplayerPage') or self.tabWidget.indexOf(self.mainApplication.multiplayerPage) == -1:
            self.mainApplication.addMultiplayerTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.multiplayerPage)
            self.tabWidget.setCurrentIndex(index)

    def onSettingsClicked(self):
        if not hasattr(self.mainApplication, 'settingsPage') or self.tabWidget.indexOf(self.mainApplication.settingsPage) == -1:
            self.mainApplication.addSettingsTab()
        else:
            index = self.tabWidget.indexOf(self.mainApplication.settingsPage)
            self.tabWidget.setCurrentIndex(index)

    def openLinkInWebView(self, url):
        # Convert string URL to QUrl object
        qurl = QUrl(url)
        self.webView.load(qurl)

class CustomGameDialog(QDialog):
    def __init__(self, homePage):
        super().__init__(homePage)
        self.setWindowTitle('Select Game Mode')
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
        self.startGameButton.clicked.connect(homePage.mainApplication.addSoloGameTab)

        # Set minimum dialog size for better UI experience
        self.setMinimumSize(275, 175)  # Example improvement for resizing

    def toggleCustomEntry(self):
        self.customStartPageEdit.setEnabled(self.startPageCombo.currentText() == 'Custom')
        self.customEndPageEdit.setEnabled(self.endPageCombo.currentText() == 'Custom')

