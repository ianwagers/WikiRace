
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class MultiplayerPage(QWidget):
    def __init__(self, tabWidget, parent=None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        self.initUI()

    def initUI(self):
        # Apply dark mode styling
        self.setStyleSheet("""
            QWidget {
                background-color: #101418;
                color: #E0E0E0;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 16px;
                font-weight: 600;
                padding: 16px 24px;
                margin: 8px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
                border-color: #00FFFF;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
                border-color: #8A2BE2;
            }
        """)
        
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
