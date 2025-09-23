
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

class CustomTimer(QObject):
    # Signal to emit the elapsed time in the format hh:mm:ss
    timeChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.elapsedTime = 0
        self.timer.start(1000)  # Timer updates every second

    def updateTime(self):
        self.elapsedTime += 1
        self.timeChanged.emit(self.formatTime(self.elapsedTime))

    @staticmethod
    def formatTime(seconds):
        # Convert to integer to avoid float formatting issues
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
