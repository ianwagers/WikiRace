
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.logic.ThemeManager import theme_manager

class MultiplayerPage(QWidget):
    def __init__(self, tabWidget, parent=None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)

    def apply_theme(self):
        """Apply theme-based styles to the multiplayer page"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel {{
                color: {styles['text_color']};
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 16px;
                font-weight: 600;
                padding: 16px 24px;
                margin: 8px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
                border-color: {styles['border_pressed']};
            }}
        """)

    def initUI(self):
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title label
        self.titleLabel = QLabel("Multiplayer")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.titleLabel)

        # Host Game button
        self.hostGameButton = QPushButton("Host Game")
        self.layout.addWidget(self.hostGameButton)

        # Join Game button
        self.joinGameButton = QPushButton("Join Game")
        self.layout.addWidget(self.joinGameButton)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Placeholder connections for the buttons
        self.hostGameButton.clicked.connect(self.onHostGameClicked)
        self.joinGameButton.clicked.connect(self.onJoinGameClicked)

    def onHostGameClicked(self):
        # Placeholder for hosting a game functionality
        pass

    def onJoinGameClicked(self):
        # Placeholder for joining a game functionality
        pass
