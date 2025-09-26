"""
CountdownDialog - Visual countdown display for game start

Shows a responsive countdown timer with drag race lights to prepare players
for the start of a multiplayer game.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from src.logic.ThemeManager import theme_manager


class DragRaceLight(QWidget):
    """Custom widget for drag race style lights"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_lit = False
        self.light_color = QColor(128, 128, 128)  # Default gray
        self.setMinimumSize(40, 40)
        self.setMaximumSize(80, 80)
    
    def set_light(self, color, is_lit=True):
        """Set the light color and state"""
        self.light_color = color
        self.is_lit = is_lit
        self.update()
    
    def paintEvent(self, event):
        """Paint the circular light"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center and radius
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 5
        
        # Draw outer ring
        painter.setPen(QPen(QColor(64, 64, 64), 2))
        painter.setBrush(QColor(32, 32, 32))
        painter.drawEllipse(center, radius + 3, radius + 3)
        
        # Draw light
        if self.is_lit:
            # Bright version with glow effect
            painter.setPen(QPen(self.light_color, 1))
            painter.setBrush(self.light_color)
        else:
            # Dim version
            dim_color = QColor(self.light_color.red() // 4, 
                             self.light_color.green() // 4, 
                             self.light_color.blue() // 4)
            painter.setPen(QPen(dim_color, 1))
            painter.setBrush(dim_color)
        
        painter.drawEllipse(center, radius, radius)
        
        # Add highlight for lit lights
        if self.is_lit:
            highlight = QColor(255, 255, 255, 100)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(highlight)
            # Convert to integers to avoid float division issues
            highlight_radius = int(radius / 1.5)
            highlight_x = center.x() - highlight_radius // 2
            highlight_y = center.y() - highlight_radius // 2
            painter.drawEllipse(highlight_x, highlight_y, highlight_radius, highlight_radius)


class CountdownDialog(QDialog):
    """Dialog showing a countdown timer before game starts"""
    
    # Signal emitted when countdown completes
    countdown_finished = pyqtSignal()
    
    def __init__(self, countdown_seconds=5, message="Get ready!", parent=None):
        super().__init__(parent)
        self.countdown_seconds = countdown_seconds
        self.current_count = countdown_seconds
        self.message = message
        
        # Add unique identifier for debugging
        import time
        self.dialog_id = f"CD_{int(time.time() * 1000) % 10000}"
        print(f"🎬 DEBUG: Created CountdownDialog {self.dialog_id}")
        
        # Calculate responsive size based on parent window
        self.calculate_responsive_size()
        
        self.initUI()
        self.apply_theme()
        self.start_countdown()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def calculate_responsive_size(self):
        """Calculate responsive size based on parent window"""
        # Get parent window size
        parent = self.parent()
        while parent and parent.parent():
            if hasattr(parent, 'geometry'):
                parent_geo = parent.geometry()
                break
            parent = parent.parent()
        else:
            # Fallback to screen size
            from PyQt6.QtWidgets import QApplication
            parent_geo = QApplication.primaryScreen().geometry()
        
        # Calculate responsive dimensions - halved size as requested
        width = max(200, min(int(parent_geo.width() * 0.25), 400))  # Halved from 0.5 to 0.25
        height = max(550, min(int(parent_geo.height() * 0.25), 600))  # Increased minimum height to 550px to prevent text cropping
        
        self.dialog_width = width
        self.dialog_height = height
        
        # Calculate font sizes based on dialog size
        self.message_font_size = max(14, int(width / 25))
        self.countdown_font_size = max(60, int(width / 6))
        self.status_font_size = max(10, int(width / 35))
        self.light_size = max(30, min(int(width / 12), 60))
        
        print(f"🎬 Countdown sizing: {width}x{height}, fonts: {self.message_font_size}/{self.countdown_font_size}/{self.status_font_size}")
    
    def initUI(self):
        """Initialize the responsive countdown dialog UI with drag race lights"""
        self.setWindowTitle("Game Starting!")
        self.setModal(True)
        self.setFixedSize(self.dialog_width, self.dialog_height)
        
        # Remove window decorations for full-screen feel
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        # Center on the main application window
        self.center_on_parent()
        
        # Main layout with responsive spacing
        layout = QVBoxLayout(self)
        margin = max(20, int(self.dialog_width / 20))
        spacing = max(15, int(self.dialog_width / 30))
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)
        
        # Drag race lights at the top
        lights_layout = QHBoxLayout()
        lights_layout.setSpacing(max(10, int(self.dialog_width / 40)))
        
        # Create drag race lights (Red, Yellow, Green)
        self.red_light = DragRaceLight()
        self.red_light.setFixedSize(self.light_size, self.light_size)
        self.red_light.set_light(QColor(220, 53, 69), False)  # Bootstrap red
        
        self.yellow_light = DragRaceLight()
        self.yellow_light.setFixedSize(self.light_size, self.light_size)
        self.yellow_light.set_light(QColor(255, 193, 7), False)  # Bootstrap yellow
        
        self.green_light = DragRaceLight()
        self.green_light.setFixedSize(self.light_size, self.light_size)
        self.green_light.set_light(QColor(40, 167, 69), False)  # Bootstrap green
        
        lights_layout.addStretch()
        lights_layout.addWidget(self.red_light)
        lights_layout.addWidget(self.yellow_light)
        lights_layout.addWidget(self.green_light)
        lights_layout.addStretch()
        
        layout.addLayout(lights_layout)
        
        # Message label with text wrapping enabled
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("Inter", self.message_font_size, QFont.Weight.Bold))
        self.message_label.setWordWrap(True)  # Ensure text wrapping is enabled
        self.message_label.setMaximumHeight(int(self.dialog_height * 0.2))  # Slightly more space for wrapped text
        layout.addWidget(self.message_label)
        
        # Countdown number
        self.countdown_label = QLabel(str(self.current_count))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Inter", self.countdown_font_size, QFont.Weight.Bold))
        self.countdown_label.setMinimumHeight(int(self.dialog_height * 0.3))
        layout.addWidget(self.countdown_label)
        
        # Status label with text wrapping enabled
        self.status_label = QLabel("Race starts when countdown reaches 0")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Inter", self.status_font_size))
        self.status_label.setWordWrap(True)  # Ensure text wrapping is enabled
        self.status_label.setMaximumHeight(int(self.dialog_height * 0.15))  # Slightly more space for wrapped text
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def center_on_parent(self):
        """Center the dialog on the parent window with current position"""
        parent = self.parent()
        while parent and parent.parent():
            if hasattr(parent, 'geometry'):
                parent_geo = parent.geometry()
                break
            parent = parent.parent()
        else:
            # Fallback to screen center
            from PyQt6.QtWidgets import QApplication
            parent_geo = QApplication.primaryScreen().geometry()
        
        # Get current parent window position (not original)
        if hasattr(parent, 'window'):
            # If parent has a window property, use that
            parent_geometry = parent.window().geometry()
        else:
            # Get current geometry of parent
            parent_geometry = parent_geo
        
        # Calculate center position - dialog should be centered on parent
        dialog_size = self.size()
        center_x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
        center_y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
        
        # Add small offset for multiple dialogs (stagger them slightly)
        offset_x = (int(self.dialog_id.split('_')[1]) % 3) * 20  # Reduced offset
        offset_y = (int(self.dialog_id.split('_')[1]) % 3) * 15  # Reduced offset
        
        x = center_x + offset_x
        y = center_y + offset_y
        
        # Ensure dialog stays on screen
        screen_geometry = self.parent().screen().availableGeometry()
        x = max(screen_geometry.left(), min(x, screen_geometry.right() - dialog_size.width()))
        y = max(screen_geometry.top(), min(y, screen_geometry.bottom() - dialog_size.height()))
        
        print(f"🎬 DEBUG: Positioning CountdownDialog {self.dialog_id} at ({x}, {y})")
        self.move(x, y)
        
        # Force update to ensure positioning works
        self.update()
        self.repaint()
    
    def apply_theme(self):
        """Apply theme-based styling with responsive fonts"""
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
        
        # Countdown number gets special styling with responsive font sizes
        if styles['is_dark']:
            countdown_color = "#4CAF50"  # Green for dark theme
            status_color = "#adb5bd"
        else:
            countdown_color = "#2E7D32"  # Dark green for light theme  
            status_color = "#6c757d"
        
        # Apply colors while preserving responsive font sizes
        self.countdown_label.setStyleSheet(f"color: {countdown_color}; font-size: {self.countdown_font_size}px; font-weight: bold;")
        self.status_label.setStyleSheet(f"color: {status_color}; font-size: {self.status_font_size}px;")
        self.message_label.setStyleSheet(f"font-size: {self.message_font_size}px; font-weight: bold;")
        
        # Ensure fonts are properly set after theme application
        self.message_label.setFont(QFont("Inter", self.message_font_size, QFont.Weight.Bold))
        self.countdown_label.setFont(QFont("Inter", self.countdown_font_size, QFont.Weight.Bold))
        self.status_label.setFont(QFont("Inter", self.status_font_size))
    
    def start_countdown(self):
        """Start the countdown timer"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
    
    def update_countdown(self):
        """Update the countdown display with drag race lights"""
        self.current_count -= 1
        print(f"🎬 DEBUG: CountdownDialog {self.dialog_id} updating: {self.current_count}")
        
        if self.current_count > 0:
            self.countdown_label.setText(str(self.current_count))
            
            # Drag race lights sequence - Fixed sequence: Red on 3, Yellow on 2, Green on 1 and GO!
            if self.current_count == 3:
                # Red light on
                self.red_light.set_light(QColor(220, 53, 69), True)
                self.yellow_light.set_light(QColor(255, 193, 7), False)
                self.green_light.set_light(QColor(40, 167, 69), False)
            elif self.current_count == 2:
                # Yellow light on (red stays on)
                self.red_light.set_light(QColor(220, 53, 69), True)
                self.yellow_light.set_light(QColor(255, 193, 7), True)
                self.green_light.set_light(QColor(40, 167, 69), False)
            elif self.current_count == 1:
                # Green light on (red and yellow stay on)
                self.red_light.set_light(QColor(220, 53, 69), True)
                self.yellow_light.set_light(QColor(255, 193, 7), True)
                self.green_light.set_light(QColor(40, 167, 69), True)
            
            # Change countdown color as we get closer to 0
            if self.current_count <= 3:
                styles = theme_manager.get_theme_styles()
                warning_color = "#ff6b6b" if styles['is_dark'] else "#dc3545"
                self.countdown_label.setStyleSheet(f"color: {warning_color}; font-size: {self.countdown_font_size}px; font-weight: bold;")
        
        elif self.current_count == 0:
            # ALL GREEN LIGHTS! GO!
            self.red_light.set_light(QColor(40, 167, 69), True)    # Red light turns green
            self.yellow_light.set_light(QColor(40, 167, 69), True)  # Yellow light turns green
            self.green_light.set_light(QColor(40, 167, 69), True)   # Green light stays green
            
            self.countdown_label.setText("GO!")
            self.status_label.setText("Race has started! Good luck!")
            
            # Final color change
            styles = theme_manager.get_theme_styles()
            go_color = "#51cf66" if styles['is_dark'] else "#28a745"
            self.countdown_label.setStyleSheet(f"color: {go_color}; font-size: {self.countdown_font_size}px; font-weight: bold;")
            
            # Auto-close after showing GO! for 1 second
            QTimer.singleShot(1000, self.finish_countdown)
        
        else:
            self.finish_countdown()
    
    def finish_countdown(self):
        """Finish the countdown and close dialog"""
        print(f"🎬 DEBUG: CountdownDialog {self.dialog_id} finishing countdown")
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
