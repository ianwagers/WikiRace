from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt6.QtGui import QIcon

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gui.HomePage import HomePage
from src.gui.SoloGamePage import SoloGamePage
from src.gui.MultiplayerPage import MultiplayerPage
from src.gui.SettingsPage import SettingsPage
from src.logic.ThemeManager import theme_manager

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        # Use relative path instead of hardcoded path
        self.projectPath = str(project_root / 'src')

        # Set window icon if it exists
        icon_path = project_root / 'src' / 'resources' / 'icons' / 'game_icon.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowTitle("Wikipedia Race")
        self.setGeometry(100, 100, 1000, 1100)  # Adjust size as needed

        # Initialize tab widget and add tabs
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabWidget)

        self.initUI()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def initUI(self):
        # Initialize landing page
        self.homePage = HomePage(self.tabWidget, self)

        # Add home tab
        self.tabWidget.addTab(self.homePage, "Home")
        
        # Apply initial theme
        self.apply_theme()

    def addSoloGameTab(self, start_url, end_url, start_title=None, end_title=None):
        # Adds the Solo Game tab only if it doesn't exist
        if not hasattr(self, 'soloGamePage'):
            self.soloGamePage = SoloGamePage(self.tabWidget, start_url, end_url, start_title, end_title)
            self.tabWidget.addTab(self.soloGamePage, "Solo Game")
        else:
            self.closeTab(self.tabWidget.indexOf(self.soloGamePage))
            self.soloGamePage = SoloGamePage(self.tabWidget, start_url, end_url, start_title, end_title)
            self.tabWidget.addTab(self.soloGamePage, "Solo Game")

    def addMultiplayerTab(self):
        # CRITICAL FIX: Always create a new multiplayer tab to ensure clean state
        # Remove any existing multiplayer tab first
        if hasattr(self, 'multiplayerPage'):
            try:
                existing_index = self.tabWidget.indexOf(self.multiplayerPage)
                if existing_index >= 0:
                    self.tabWidget.removeTab(existing_index)
                delattr(self, 'multiplayerPage')
            except:
                pass  # Ignore errors if tab doesn't exist
        
        # Create new multiplayer tab
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
    
    def apply_theme(self):
        """Apply theme to the main application"""
        styles = theme_manager.get_theme_styles()
        
        # Apply theme to main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
            }}
        """)
        
        # Apply theme to tab widget
        self.tabWidget.setStyleSheet(f"""
            QTabWidget::pane {{
                border-top: 2px solid {styles['border_color']};
                background-color: {styles['background_color']};
            }}

            QTabBar::tab {{
                background: {styles['tab_background']};
                color: {styles['tab_text']};
                padding: 8px 16px;
                border: 1px solid {styles['border_color']};
                border-bottom-color: {styles['tab_background']};
                border-radius: 6px 6px 0px 0px;
                margin-right: 2px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 500;
            }}

            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {styles['tab_selected']};
                color: {styles['tab_text_selected']};
                border-color: {styles['border_hover']};
            }}

            QWidget {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
            }}
        """)
    
    def on_theme_changed(self, theme):
        """Handle theme changes"""
        print(f"🎨 WikiRace: Main application - Theme changed to: {theme}")
        self.apply_theme()

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    mainApp = MainApplication()
    mainApp.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
