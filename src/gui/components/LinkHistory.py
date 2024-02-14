
from PyQt5.QtWidgets import QListWidget

class LinkHistory(QListWidget):
    def __init__(self):
        super().__init__()

    def addLink(self, linkTitle):
        self.addItem(linkTitle)

    def clearHistory(self):
        self.clear()
