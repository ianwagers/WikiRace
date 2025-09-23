"""
Player Name Input Dialog for Multiplayer Games
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from src.logic.ThemeManager import theme_manager


class PlayerNameDialog(QDialog):
    """Dialog for entering player name before joining/creating a game"""
    
    def __init__(self, title="Enter Player Name", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(420, 280)  # Further increased size to prevent any text cutoff
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)  # Remove window frame for modern look
        
        # Store the entered name
        self.player_name = None
        
        self.initUI()
        self.apply_theme()
    
    def initUI(self):
        """Initialize the dialog UI with a modern, clean design"""
        # Main layout with proper spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a styled container frame
        container_frame = QFrame()
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setSpacing(25)
        container_layout.setContentsMargins(35, 35, 35, 35)
        
        # Header section with title only
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel("Enter Your Name")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            margin-bottom: 4px;
        """)
        header_layout.addWidget(title_label)
        
        # Subtitle removed as requested
        
        container_layout.addLayout(header_layout)
        
        # Simple input section
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your display name...")
        self.name_input.setMaxLength(50)
        self.name_input.setMinimumHeight(40)
        self.name_input.returnPressed.connect(self.accept_name)
        container_layout.addWidget(self.name_input)
        
        # Character count
        self.char_count_label = QLabel("0/50 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("""
            font-size: 11px; 
            margin-top: -8px;
        """)
        container_layout.addWidget(self.char_count_label)
        
        # Connect character count updates
        self.name_input.textChanged.connect(self.update_char_count)
        
        # Button section with proper spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 20, 0, 0)  # Further increased top margin to prevent cutoff
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # OK button
        self.ok_button = QPushButton("Continue")
        self.ok_button.setMinimumHeight(45)
        self.ok_button.setMinimumWidth(110)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept_name)
        button_layout.addWidget(self.ok_button)
        
        container_layout.addLayout(button_layout)
        
        # Add container to main layout
        main_layout.addWidget(container_frame)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def update_char_count(self, text):
        """Update character count display"""
        count = len(text)
        self.char_count_label.setText(f"{count}/50 characters")
        
        # Change color based on character count
        if count > 45:
            self.char_count_label.setStyleSheet("""
                font-size: 12px; 
                color: #e74c3c;
                margin-top: -5px;
            """)
        elif count > 40:
            self.char_count_label.setStyleSheet("""
                font-size: 12px; 
                color: #f39c12;
                margin-top: -5px;
            """)
        else:
            self.char_count_label.setStyleSheet("""
                font-size: 12px; 
                color: #95a5a6;
                margin-top: -5px;
            """)
    
    def accept_name(self):
        """Accept the entered name if valid"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter your display name.")
            return
        
        # Validate player name length and characters
        if len(name) > 50:
            QMessageBox.warning(self, "Invalid Name", "Display name must be 50 characters or less.")
            return
        
        if not name.replace(' ', '').isalnum():
            QMessageBox.warning(self, "Invalid Name", "Display name can only contain letters, numbers, and spaces.")
            return
        
        self.player_name = name
        self.accept()
    
    def apply_theme(self):
        """Apply theme-based styling to match the application theme"""
        styles = theme_manager.get_theme_styles()
        
        # Apply consistent theme styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
            }}
            QFrame {{
                background-color: {styles['secondary_background']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
            }}
            QLabel {{
                color: {styles['text_color']};
                background-color: transparent;
            }}
            QLineEdit {{
                background-color: {styles['input_background']};
                border: 2px solid {styles['border_color']};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: {styles['text_color']};
            }}
            QLineEdit:focus {{
                border-color: {styles['accent_color']};
                background-color: {styles['tertiary_background']};
            }}
            QLineEdit:hover {{
                border-color: {styles['border_hover']};
            }}
        """)
        
        # Update button styling to match application theme
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                border: 2px solid {styles['border_color']};
                border-radius: 6px;
                background-color: {styles['button_background']};
                color: {styles['text_color']};
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
            }}
        """)
        
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                border: 2px solid {styles['accent_color']};
                border-radius: 6px;
                background-color: {styles['accent_color']};
                color: #ffffff;
            }}
            QPushButton:hover {{
                background-color: {styles['border_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
            }}
        """)
    
    @staticmethod
    def get_player_name(title="Enter Player Name", parent=None):
        """Static method to show dialog and return player name"""
        dialog = PlayerNameDialog(title, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.player_name
        return None
