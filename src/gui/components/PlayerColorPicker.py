"""
PlayerColorPicker - Widget for players to choose their color in multiplayer games

Provides a color picker with 10 pastel colors optimized for both light and dark themes.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from src.logic.ThemeManager import theme_manager


class ColorButton(QPushButton):
    """Custom button for color selection"""
    
    def __init__(self, color, color_name, parent=None):
        super().__init__(parent)
        self.color = color
        self.color_name = color_name
        self.is_selected = False
        
        self.setFixedSize(28, 28)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Set button color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid {color};
                border-radius: 14px;
            }}
            QPushButton:hover {{
                border: 2px solid #ffffff;
            }}
            QPushButton:checked {{
                border: 3px solid #ffffff;
            }}
        """)


class PlayerColorPicker(QWidget):
    """Color picker widget for player color selection"""
    
    color_selected = pyqtSignal(str, str)  # color_hex, color_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = None
        self.selected_color_name = None
        self.used_colors = set()  # Track colors already selected by other players
        
        # Define color palettes for light and dark themes
        self.light_colors = [
            ("#FFB3BA", "Rose"),
            ("#FFDFBA", "Peach"),
            ("#FFFFBA", "Lemon"),
            ("#BAFFC9", "Mint"),
            ("#BAE1FF", "Sky"),
            ("#E1BAFF", "Lavender"),
            ("#FFB3E6", "Pink"),
            ("#B3FFBA", "Lime"),
            ("#FFE1BA", "Cream"),
            ("#BAE1E1", "Aqua")
        ]
        
        self.dark_colors = [
            ("#8B4A6B", "Deep Rose"),
            ("#8B6A4A", "Warm Brown"),
            ("#8B8B4A", "Olive"),
            ("#4A8B6A", "Forest"),
            ("#4A6A8B", "Navy"),
            ("#6A4A8B", "Purple"),
            ("#8B4A8B", "Magenta"),
            ("#6A8B4A", "Sage"),
            ("#8B6A6A", "Mauve"),
            ("#4A8B8B", "Teal")
        ]
        
        self.initUI()
        self.apply_theme()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def initUI(self):
        """Initialize the color picker UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Color grid container - more compact
        self.color_frame = QFrame()
        self.color_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        color_layout = QVBoxLayout(self.color_frame)
        color_layout.setContentsMargins(8, 8, 8, 8)
        color_layout.setSpacing(4)
        
        # Title inside the color frame - more compact
        self.title_label = QLabel("Choose Your Color")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 4px;
            color: #ffffff;
        """)
        color_layout.addWidget(self.title_label)
        
        # Create color grid (2 columns of 5 colors) - more compact
        self.color_buttons = []
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Get current colors based on theme
        current_colors = self._get_current_colors()
        
        # Create horizontal layout to hold the 2 columns
        colors_horizontal_layout = QHBoxLayout()
        colors_horizontal_layout.setSpacing(4)
        colors_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        
        for i in range(2):  # 2 columns
            col_layout = QVBoxLayout()
            col_layout.setSpacing(2)
            col_layout.setContentsMargins(0, 0, 0, 0)
            
            for j in range(5):  # 5 rows
                color_index = i * 5 + j
                if color_index < len(current_colors):
                    color_hex, color_name = current_colors[color_index]
                    
                    # Create color button
                    color_btn = ColorButton(color_hex, color_name)
                    color_btn.clicked.connect(lambda checked, c=color_hex, n=color_name: self._on_color_selected(c, n))
                    
                    self.color_buttons.append(color_btn)
                    self.button_group.addButton(color_btn, color_index)
                    
                    col_layout.addWidget(color_btn)
                else:
                    # Add spacer for empty slots
                    spacer = QWidget()
                    spacer.setFixedSize(28, 28)
                    col_layout.addWidget(spacer)
            
            colors_horizontal_layout.addLayout(col_layout)
        
        color_layout.addLayout(colors_horizontal_layout)
        
        # Selected color display inside the color frame - more compact
        self.selected_label = QLabel("No color selected")
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_label.setStyleSheet("""
            font-size: 10px;
            font-style: italic;
            margin-top: 4px;
            color: #cccccc;
        """)
        color_layout.addWidget(self.selected_label)
        
        layout.addWidget(self.color_frame)
    
    def _get_current_colors(self):
        """Get the appropriate color palette based on current theme"""
        styles = theme_manager.get_theme_styles()
        is_dark = styles.get('is_dark', False)
        return self.dark_colors if is_dark else self.light_colors
    
    def _on_color_selected(self, color_hex, color_name):
        """Handle color selection"""
        self.selected_color = color_hex
        self.selected_color_name = color_name
        
        # Update selected color display with proper theming
        styles = theme_manager.get_theme_styles()
        self.selected_label.setText(f"Selected: {color_name}")
        self.selected_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: bold;
            color: {color_hex};
            margin-top: 4px;
        """)
        
        # Emit signal
        self.color_selected.emit(color_hex, color_name)
    
    def update_used_colors(self, used_colors):
        """Update the list of colors already used by other players"""
        self.used_colors = set(used_colors)
        self._update_color_buttons()
    
    def _update_color_buttons(self):
        """Update color buttons to show which are available/used"""
        current_colors = self._get_current_colors()
        
        for i, (color_hex, color_name) in enumerate(current_colors):
            if i < len(self.color_buttons):
                btn = self.color_buttons[i]
                is_used = color_hex in self.used_colors
                is_selected = btn.isChecked()
                
                if is_used and not is_selected:
                    # Show slash over used colors
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color_hex};
                            border: 2px solid #ff0000;
                            border-radius: 14px;
                            position: relative;
                        }}
                        QPushButton:hover {{
                            border: 2px solid #ff0000;
                        }}
                        QPushButton:checked {{
                            border: 3px solid #ffffff;
                        }}
                    """)
                    # Add slash effect (simplified - could be enhanced with custom painting)
                    btn.setEnabled(False)
                else:
                    # Normal styling
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color_hex};
                            border: 2px solid {color_hex};
                            border-radius: 14px;
                        }}
                        QPushButton:hover {{
                            border: 2px solid #ffffff;
                        }}
                        QPushButton:checked {{
                            border: 3px solid #ffffff;
                        }}
                    """)
                    btn.setEnabled(True)
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        # Update color palette based on theme
        current_colors = self._get_current_colors()
        
        # Update all color buttons
        for i, (color_hex, color_name) in enumerate(current_colors):
            if i < len(self.color_buttons):
                btn = self.color_buttons[i]
                btn.color = color_hex
                btn.color_name = color_name
                
                # Update button styling
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color_hex};
                        border: 2px solid {color_hex};
                        border-radius: 14px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #ffffff;
                    }}
                    QPushButton:checked {{
                        border: 3px solid #ffffff;
                    }}
                """)
        
        # Update frame styling to match MultiplayerPage styling
        frame_style = f"""
            QFrame {{
                background-color: {styles['card_background']};
                border: 1px solid {styles['border_color']};
                border-radius: 6px;
            }}
        """
        self.color_frame.setStyleSheet(frame_style)
        
        # Update title styling to match MultiplayerPage
        self.title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {styles['text_color']};
            margin-bottom: 4px;
        """)
        
        # Update selected label styling
        self.selected_label.setStyleSheet(f"""
            font-size: 10px;
            font-style: italic;
            margin-top: 4px;
            color: {styles['text_secondary']};
        """)
    
    def get_selected_color(self):
        """Get the currently selected color"""
        return self.selected_color, self.selected_color_name
    
    def set_selected_color(self, color_hex):
        """Set the selected color programmatically"""
        # Find the button with this color
        for i, btn in enumerate(self.color_buttons):
            if btn.color == color_hex:
                btn.setChecked(True)
                self._on_color_selected(color_hex, btn.color_name)
                break
    
    def reset_selection(self):
        """Reset color selection"""
        self.button_group.setExclusive(False)
        for btn in self.color_buttons:
            btn.setChecked(False)
        self.button_group.setExclusive(True)
        
        self.selected_color = None
        self.selected_color_name = None
        self.selected_label.setText("No color selected")
        
        # Use proper theming for reset state
        styles = theme_manager.get_theme_styles()
        self.selected_label.setStyleSheet(f"""
            font-size: 10px;
            font-style: italic;
            margin-top: 4px;
            color: {styles['text_secondary']};
        """)
