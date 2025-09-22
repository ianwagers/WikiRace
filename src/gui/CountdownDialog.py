"""
CountdownDialog - Visual countdown display for game start

Shows a large countdown timer with a message to prepare players
for the start of a multiplayer game.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from src.logic.ThemeManager import theme_manager


class CountdownDialog(QDialog):
    """Dialog showing a countdown timer before game starts"""
    
    # Signal emitted when countdown completes
    countdown_finished = pyqtSignal()
    
    def __init__(self, countdown_seconds=5, message="Get ready!", parent=None):
        super().__init__(parent)
        self.countdown_seconds = countdown_seconds
        self.current_count = countdown_seconds
        self.message = message
        
        self.initUI()
        self.apply_theme()
        self.start_countdown()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def initUI(self):
        """Initialize the countdown dialog UI"""
        self.setWindowTitle("Game Starting!")
        self.setModal(True)
        self.setFixedSize(450, 400)  # Increased height to prevent text cut-off
        
        # Remove window decorations for full-screen feel
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        # Center on the main application window, not just the immediate parent
        main_window = self.parent()
        while main_window and main_window.parent():
            if hasattr(main_window, 'windowTitle') and 'WikiRace' in main_window.windowTitle():
                break
            main_window = main_window.parent()
        
        if main_window:
            # Center on the main WikiRace window
            parent_geo = main_window.geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            # Fallback to screen center
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)  # Reduced margins for better text fit
        layout.setSpacing(20)  # Reduced spacing
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))  # Slightly smaller
        self.message_label.setWordWrap(True)
        self.message_label.setMaximumHeight(60)  # Limit height to prevent overflow
        layout.addWidget(self.message_label)
        
        # Countdown number
        self.countdown_label = QLabel(str(self.current_count))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Inter", 64, QFont.Weight.Bold))  # Slightly smaller
        layout.addWidget(self.countdown_label)
        
        # Status label
        self.status_label = QLabel("Race starts when countdown reaches 0")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Inter", 11))  # Slightly smaller
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumHeight(40)  # Limit height
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        # Dialog background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {styles['background_color']};
                border: 3px solid {styles['border_color']};
                border-radius: 15px;
            }}
            QLabel {{
                color: {styles['text_color']};
                background-color: transparent;
            }}
        """)
        
        # Countdown number gets special styling
        if styles['is_dark']:
            countdown_color = "#4CAF50"  # Green for dark theme
            status_color = "#adb5bd"
        else:
            countdown_color = "#2E7D32"  # Dark green for light theme  
            status_color = "#6c757d"
        
        self.countdown_label.setStyleSheet(f"color: {countdown_color};")
        self.status_label.setStyleSheet(f"color: {status_color};")
    
    def start_countdown(self):
        """Start the countdown timer"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
    
    def update_countdown(self):
        """Update the countdown display"""
        self.current_count -= 1
        
        if self.current_count > 0:
            self.countdown_label.setText(str(self.current_count))
            
            # Change color as we get closer to 0
            if self.current_count <= 3:
                styles = theme_manager.get_theme_styles()
                warning_color = "#ff6b6b" if styles['is_dark'] else "#dc3545"
                self.countdown_label.setStyleSheet(f"color: {warning_color};")
        
        elif self.current_count == 0:
            self.countdown_label.setText("GO!")
            self.status_label.setText("Race has started! Good luck!")
            
            # Final color change
            styles = theme_manager.get_theme_styles()
            go_color = "#51cf66" if styles['is_dark'] else "#28a745"
            self.countdown_label.setStyleSheet(f"color: {go_color};")
            
            # Auto-close after showing GO! for 1 second
            QTimer.singleShot(1000, self.finish_countdown)
        
        else:
            self.finish_countdown()
    
    def finish_countdown(self):
        """Finish the countdown and close dialog"""
        self.timer.stop()
        self.countdown_finished.emit()
        self.accept()  # Close the dialog
    
    def keyPressEvent(self, event):
        """Handle key press events (disable Escape to close)"""
        # Prevent closing during countdown
        if event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        # Stop timer if dialog is closed
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()
