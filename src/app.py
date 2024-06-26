from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

import sys
sys.path.append('C:/Project_Workspace/WikiRace')
from src.gui.HomePage import HomePage
from src.gui.SoloGamePage import SoloGamePage
from src.gui.MultiplayerPage import MultiplayerPage
from src.gui.SettingsPage import SettingsPage

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.projectPath = 'C:/Project_Workspace/WikiRace/src/'

        self.setWindowIcon(QIcon(self.projectPath + 'resources/icons/game_icon.ico'))
        self.setWindowTitle("Wikipedia Race")
        self.setGeometry(100, 100, 1000, 1100)  # Adjust size as needed

        # Initialize tab widget and add tabs
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabWidget)

        self.initUI()

    def initUI(self):
        # Initialize landing page
        self.homePage = HomePage(self.tabWidget, self)

        # Add home tab
        self.tabWidget.addTab(self.homePage, "Home")

    def addSoloGameTab(self, start_url, end_url):
        # Adds the Solo Game tab only if it doesn't exist
        if not hasattr(self, 'soloGamePage'):
            self.soloGamePage = SoloGamePage(self.tabWidget, start_url, end_url)
            self.tabWidget.addTab(self.soloGamePage, "Solo Game")
        else:
            self.closeTab(self.tabWidget.indexOf(self.soloGamePage))
            self.soloGamePage = SoloGamePage(self.tabWidget, start_url, end_url)
            self.tabWidget.addTab(self.soloGamePage, "Solo Game")

    def addMultiplayerTab(self):
        # Adds the Multiplayer tab only if it doesn't exist
        if not hasattr(self, 'multiplayerPage'):
            self.multiplayerPage = MultiplayerPage(self.tabWidget)
            self.tabWidget.addTab(self.multiplayerPage, "Multiplayer")

    def addSettingsTab(self):
        # Adds the Settings tab only if it doesn't exist
        if not hasattr(self, 'settingsPage'):
            self.settingsPage = SettingsPage(self.tabWidget)
            self.tabWidget.addTab(self.settingsPage, "Settings")
    
    def closeTab(self, index):
        if index >= 0:
            widget = self.tabWidget.widget(index)
            widgetType = type(widget).__name__

            # Delete the widget to free up resources
            widget.deleteLater()

            # Remove the attribute based on the widget type to allow reopening
            if widgetType == 'SoloGamePage':
                delattr(self, 'soloGamePage')
            elif widgetType == 'MultiplayerPage':
                delattr(self, 'multiplayerPage')
            elif widgetType == 'SettingsPage':
                delattr(self, 'settingsPage')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainApp = MainApplication()
    mainApp.show()
    sys.exit(app.exec_())
