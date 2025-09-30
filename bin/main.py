# Importing required modules
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.app import MainApplication

def main():
    app = QApplication(sys.argv)
    
    # Set application icon for taskbar
    from PyQt6.QtGui import QIcon
    project_root = Path(__file__).parent.parent
    icon_path = project_root / 'src' / 'resources' / 'icons' / 'favicon.ico'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()