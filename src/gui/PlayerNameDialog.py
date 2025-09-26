"""
Player Name Input Dialog for Multiplayer Games
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QFont
from src.logic.ThemeManager import theme_manager


class PlayerNameDialog(QDialog):
    """Dialog for entering player name before joining/creating a game"""
    
    def __init__(self, title="Enter Player Name", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Store the entered name
        self.player_name = None
        self.error_label = None
        
        # For dragging functionality
        self.drag_position = None
        
        # Calculate dynamic sizing based on parent window
        self.calculate_dynamic_size()
        
        # Make dialog draggable and resizable
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Enable resizing
        self.setMinimumSize(350, 280)
        self.setMaximumSize(600, 400)
        
        self.initUI()
        self.apply_theme()
        self.setup_animation()
        
        # Center dialog relative to parent window
        self.center_on_parent()
    
    def initUI(self):
        """Initialize the dialog UI with improved design"""
        # Main layout with tight spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a styled container frame with near-black panel color
        container_frame = QFrame()
        container_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setSpacing(20)  # Increased spacing to prevent cropping
        container_layout.setContentsMargins(24, 24, 24, 24)  # Reduced outer padding
        
        # Header section with unified title style
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title - single header row, bold 16-18px, no border
        title_label = QLabel("Enter Your Name")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("border: none; background-color: transparent;")
        header_layout.addWidget(title_label)
        
        container_layout.addLayout(header_layout)
        
        # Input section - styled as filled dark field with proper spacing
        input_container = QFrame()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(6)  # Increased spacing to prevent cropping
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name input with improved styling
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your display name...")
        self.name_input.setMaxLength(50)
        self.name_input.setMinimumHeight(48)  # Increased height for better visibility
        self.name_input.returnPressed.connect(self.accept_name)
        input_layout.addWidget(self.name_input)
        
        # Character counter integrated as inline hint with proper spacing
        counter_layout = QHBoxLayout()
        counter_layout.setContentsMargins(0, 0, 0, 0)
        counter_layout.setSpacing(0)
        
        # Spacer to push counter to right
        counter_layout.addStretch()
        
        self.char_count_label = QLabel("0/50 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setMinimumHeight(20)  # Ensure minimum height
        counter_layout.addWidget(self.char_count_label)
        input_layout.addLayout(counter_layout)
        
        # Error label for validation messages with reserved space
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.error_label.setMinimumHeight(20)  # Reserve space to prevent layout jumps
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px; margin-top: 4px;")
        self.error_label.setVisible(False)
        input_layout.addWidget(self.error_label)
        
        container_layout.addWidget(input_container)
        
        # Connect character count updates
        self.name_input.textChanged.connect(self.update_char_count)
        
        # Button section - horizontal layout with equal widths
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 8, 0, 0)
        
        # Cancel button (secondary, left)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Continue button (primary, right)
        self.ok_button = QPushButton("Continue")
        self.ok_button.setMinimumHeight(40)
        self.ok_button.setMinimumWidth(120)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept_name)
        button_layout.addWidget(self.ok_button)
        
        container_layout.addLayout(button_layout)
        
        # Add container to main layout
        main_layout.addWidget(container_frame)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def calculate_dynamic_size(self):
        """Calculate dialog size dynamically based on parent window and display"""
        if self.parent():
            # Get parent window size
            parent_size = self.parent().size()
            parent_width = parent_size.width()
            parent_height = parent_size.height()
            
            # Calculate base dialog size (percentage of parent)
            base_width = min(450, max(350, int(parent_width * 0.4)))
            # Increased base height to prevent cropping
            base_height = max(280, int(parent_height * 0.3))
            
            # Ensure minimum and maximum sizes with better height
            dialog_width = max(350, min(500, base_width))
            dialog_height = max(280, min(350, base_height))
            
            # Set initial size (not fixed, so it can be resized)
            self.resize(dialog_width, dialog_height)
        else:
            # Fallback sizing if no parent - increased height
            self.resize(450, 300)
    
    def center_on_parent(self):
        """Center dialog relative to parent window with current position"""
        if self.parent():
            # Get current parent window position (not original)
            parent_window = self.parent()
            if hasattr(parent_window, 'window'):
                # If parent has a window property, use that
                parent_geometry = parent_window.window().geometry()
            else:
                # Get current geometry of parent
                parent_geometry = parent_window.geometry()
            
            # Calculate center position - dialog should be centered on parent
            dialog_size = self.size()
            center_x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
            center_y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
            
            # Ensure dialog stays on screen
            screen_geometry = self.parent().screen().availableGeometry()
            x = max(screen_geometry.left(), min(center_x, screen_geometry.right() - dialog_size.width()))
            y = max(screen_geometry.top(), min(center_y, screen_geometry.bottom() - dialog_size.height()))
            
            # Move dialog to calculated position
            self.move(x, y)
            
            # Force update to ensure positioning works
            self.update()
            self.repaint()
        else:
            # Center on screen if no parent
            self.center()
    
    def update_char_count(self, text):
        """Update character count display with improved styling"""
        count = len(text)
        self.char_count_label.setText(f"{count}/50 characters")
        
        # Clear any previous error state
        self.error_label.setVisible(False)
        
        # Get theme-appropriate colors
        styles = theme_manager.get_theme_styles()
        if styles.get('is_dark', True):
            normal_color = "#95a5a6"
        else:
            normal_color = "#4a4a4a"
        
        # Change color based on character count with consistent styling
        if count > 45:
            self.char_count_label.setStyleSheet(f"""
                font-size: 12px; 
                color: #e74c3c;
                margin-top: 2px;
                opacity: 0.9;
            """)
        elif count > 40:
            self.char_count_label.setStyleSheet(f"""
                font-size: 12px; 
                color: #f39c12;
                margin-top: 2px;
                opacity: 0.9;
            """)
        else:
            self.char_count_label.setStyleSheet(f"""
                font-size: 12px; 
                color: {normal_color};
                margin-top: 2px;
                opacity: 0.7;
            """)
    
    def accept_name(self):
        """Accept the entered name if valid with improved error handling"""
        name = self.name_input.text().strip()
        
        # Clear previous error state
        self.error_label.setVisible(False)
        
        if not name:
            self.show_error("Name is required")
            return
        
        # Validate player name length and characters
        if len(name) > 50:
            self.show_error("Name must be 50 characters or less")
            return
        
        if not name.replace(' ', '').isalnum():
            self.show_error("Name can only contain letters, numbers, and spaces")
            return
        
        self.player_name = name
        self.accept()
    
    def show_error(self, message):
        """Show error message inline without popup"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.name_input.setFocus()
    
    def apply_theme(self):
        """Apply improved theme-based styling with adaptive panel and unified design"""
        styles = theme_manager.get_theme_styles()
        
        # Use adaptive panel color based on theme
        if styles.get('is_dark', True):
            panel_color = "#0F1115"  # Near-black for dark theme
            border_color = "#404040"  # Gray border for dark theme
        else:
            panel_color = "#FFFFFF"  # White for light theme
            border_color = "#CCCCCC"  # Light gray border for light theme
        
        accent_color = styles['accent_color']
        
        # Apply backdrop dimming and remove any default borders
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(0, 0, 0, 0.4);
                color: {styles['text_color']};
                border: none;
            }}
        """)
        
        # Container frame with near-black panel and gray border
        container_frame = self.findChild(QFrame)
        if container_frame:
            container_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {panel_color};
                    border: 1px solid {border_color};
                    border-radius: 12px;
                }}
            """)
            
            # Add subtle shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 80))
            container_frame.setGraphicsEffect(shadow)
        
        # Input field styling - remove borders around input and counter
        if styles.get('is_dark', True):
            input_text_color = "#E6EAF2"
            placeholder_color = "rgba(230, 234, 242, 0.6)"
            hover_color = "rgba(255, 255, 255, 0.05)"
        else:
            input_text_color = "#1A1A1A"
            placeholder_color = "rgba(26, 26, 26, 0.6)"
            hover_color = "rgba(0, 0, 0, 0.05)"
        
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {panel_color};
                border: none;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 15px;
                color: {input_text_color};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                selection-background-color: {accent_color};
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
                background-color: {panel_color};
            }}
            QLineEdit:hover {{
                background-color: {hover_color};
            }}
            QLineEdit::placeholder {{
                color: {placeholder_color};
                font-size: 15px;
            }}
        """)
        
        # Character counter styling - no borders, completely clean
        if styles.get('is_dark', True):
            counter_color = "rgba(149, 165, 166, 0.7)"
        else:
            counter_color = "rgba(74, 74, 74, 0.7)"
        
        self.char_count_label.setStyleSheet(f"""
            font-size: 12px;
            color: {counter_color};
            margin-top: 2px;
            background-color: transparent;
            border: none;
            padding: 0;
            margin: 2px 0 0 0;
        """)
        
        # Error label styling
        self.error_label.setStyleSheet(f"""
            color: #e74c3c;
            font-size: 12px;
            margin-top: 4px;
        """)
        
        # Cancel button (secondary/ghost style) - adaptive styling
        if styles.get('is_dark', True):
            cancel_hover_color = "rgba(255, 255, 255, 0.05)"
            cancel_pressed_color = "rgba(255, 255, 255, 0.1)"
        else:
            cancel_hover_color = "rgba(0, 0, 0, 0.05)"
            cancel_pressed_color = "rgba(0, 0, 0, 0.1)"
        
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border: 1px solid {border_color};
                border-radius: 10px;
                background-color: transparent;
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {cancel_hover_color};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {cancel_pressed_color};
            }}
        """)
        
        # Continue button (primary style) - remove yellow borders
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border: 1px solid {accent_color};
                border-radius: 10px;
                background-color: {accent_color};
                color: #ffffff;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {styles['border_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
            }}
        """)
    
    def setup_animation(self):
        """Setup fade/scale-in animation for dialog appearance"""
        # Set initial state for animation
        self.setWindowOpacity(0.0)
        self.setGeometry(self.geometry().adjusted(0, 0, 0, 0))
        
        # Create fade-in animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start animation when dialog is shown
        self.fade_animation.start()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for better UX"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept_name()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
    
    def showEvent(self, event):
        """Handle dialog show event with animation"""
        super().showEvent(event)
        if hasattr(self, 'fade_animation'):
            self.fade_animation.start()
        # Re-center after showing to ensure proper positioning
        self.center_on_parent()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.drag_position = None
        super().mouseReleaseEvent(event)
    
    @staticmethod
    def get_player_name(title="Enter Player Name", parent=None):
        """Static method to show dialog and return player name"""
        dialog = PlayerNameDialog(title, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.player_name
        return None
