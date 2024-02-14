# Importing required modules
import sys
sys.path.append('C:\Project_Workspace\WikiRace')
from PyQt5.QtWidgets import QApplication
from src.app import MainApplication

def main():
    app = QApplication(sys.argv)
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()