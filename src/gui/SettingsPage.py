
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, tabWidget, parent = None):
        super().__init__(parent)
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
        self.titleLabel = QLabel("Settings")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.titleLabel)

        # Placeholder buttons for future settings options
        self.optionButton1 = QPushButton("Option 1")
        self.layout.addWidget(self.optionButton1)

        self.optionButton2 = QPushButton("Option 2")
        self.layout.addWidget(self.optionButton2)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Placeholder connections for the buttons
        self.optionButton1.clicked.connect(self.onOption1Clicked)
        self.optionButton2.clicked.connect(self.onOption2Clicked)

    def onOption1Clicked(self):
        # Placeholder for option 1 functionality
        pass

    def onOption2Clicked(self):
        # Placeholder for option 2 functionality
        pass
