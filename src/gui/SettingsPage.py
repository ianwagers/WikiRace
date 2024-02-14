
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class SettingsPage(QWidget):
    def __init__(self, tabWidget, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)

        # Title label
        self.titleLabel = QLabel("Settings")
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
