"""
PlayerColorPicker - Widget for players to choose their color in multiplayer games

Provides a color picker with 10 pastel colors optimized for both light and dark themes.
Uses proper dynamic sizing and layout management.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QButtonGroup, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from src.logic.ThemeManager import theme_manager


def clamp(value, min_val, max_val):
    """Helper function to clamp a value between min and max"""
    return max(min_val, min(value, max_val))


class ColorButton(QPushButton):
    """Custom button for color selection with proper dynamic sizing"""
    
    def __init__(self, color, color_name, parent=None):
        super().__init__(parent)
        self.color = color
        self.color_name = color_name
        self.is_selected = False
        
        # Set proper size policy instead of fixed size
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFlat(True)  # Remove default button styling
        
        # Set object name for scoped styling
        self.setObjectName("ColorSwatch")


class PlayerColorPicker(QWidget):
    """Color picker widget for player color selection with proper dynamic sizing"""
    
    color_selected = pyqtSignal(str, str)  # color_hex, color_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = None
        self.selected_color_name = None
        self.used_colors = set()  # Track colors already selected by other players
        self.tile_size = 80  # Will be calculated dynamically
        
        # Set object name for scoped styling
        self.setObjectName("ColorPickerDialog")
        
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
        """Initialize the color picker UI with proper layout management"""
        # Main layout with proper size constraint
        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add stretch above the grid
        layout.addStretch(1)
        
        # Color grid container - no fixed sizes
        self.color_frame = QFrame()
        self.color_frame.setObjectName("ColorPickerFrame")
        color_layout = QVBoxLayout(self.color_frame)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(0)
        
        # Title inside the color frame
        self.title_label = QLabel("Choose Your Color")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("ColorPickerTitle")
        color_layout.addWidget(self.title_label)
        
        # Create proper grid layout (2 columns)
        self.color_buttons = []
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Get current colors based on theme
        current_colors = self._get_current_colors()
        
        # Create grid layout with proper column stretches
        self.grid_layout = QGridLayout()
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        
        # Create color buttons in 2 columns
        for i, (color_hex, color_name) in enumerate(current_colors):
            color_btn = ColorButton(color_hex, color_name)
            color_btn.clicked.connect(lambda checked, c=color_hex, n=color_name: self._on_color_selected(c, n))
            
            self.color_buttons.append(color_btn)
            self.button_group.addButton(color_btn, i)
            
            # Add to grid (2 columns, 5 rows)
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(color_btn, row, col)
        
        color_layout.addLayout(self.grid_layout)
        
        # Selected color display
        self.selected_label = QLabel("No color selected")
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_label.setObjectName("ColorPickerStatus")
        color_layout.addWidget(self.selected_label)
        
        layout.addWidget(self.color_frame)
        
        # Add stretch below the grid (more weight)
        layout.addStretch(2)
    
    def _get_current_colors(self):
        """Get the appropriate color palette based on current theme"""
        styles = theme_manager.get_theme_styles()
        is_dark = styles.get('is_dark', False)
        return self.dark_colors if is_dark else self.light_colors
    
    def _on_color_selected(self, color_hex, color_name):
        """Handle color selection"""
        self.selected_color = color_hex
        self.selected_color_name = color_name
        
        # Update selected color display
        self.selected_label.setText(f"Selected: {color_name}")
        
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
                    btn.setEnabled(False)
                else:
                    btn.setEnabled(True)
    
    def apply_theme(self):
        """Apply theme-based styling with centralized stylesheet"""
        styles = theme_manager.get_theme_styles()
        
        # Update color palette based on theme
        current_colors = self._get_current_colors()
        
        # Update all color buttons
        for i, (color_hex, color_name) in enumerate(current_colors):
            if i < len(self.color_buttons):
                btn = self.color_buttons[i]
                btn.color = color_hex
                btn.color_name = color_name
        
        # Centralized stylesheet to prevent dark-mode border leaks
        self.setStyleSheet(f"""
            #ColorPickerDialog {{
                background-color: {styles['card_background']};
                border: none;
                border-radius: 6px;
            }}
            
            #ColorPickerFrame {{
                background-color: transparent;
                border: none;
            }}
            
            #ColorPickerTitle {{
                font-size: 16px;
                font-weight: bold;
                color: {styles['text_color']};
                margin-bottom: 8px;
                background-color: transparent;
            }}
            
            #ColorPickerStatus {{
                font-size: 14px;
                font-style: italic;
                color: {styles['text_secondary']};
                margin-top: 8px;
                background-color: transparent;
            }}
            
            #ColorPickerDialog QPushButton#ColorSwatch {{
                background-color: {self.color_buttons[0].color if self.color_buttons else '#CCCCCC'};
                border: none;
                border-radius: {self.tile_size // 6}px;
                outline: none;
                min-width: {self.tile_size}px;
                min-height: {self.tile_size}px;
            }}
            
            #ColorPickerDialog QPushButton#ColorSwatch:hover {{
                border: 3px solid #ffffff;
            }}
            
            #ColorPickerDialog QPushButton#ColorSwatch:checked {{
                border: 4px solid #ffffff;
            }}
            
            #ColorPickerDialog QPushButton#ColorSwatch:focus {{
                box-shadow: 0 0 0 2px rgba(255,255,255,0.25);
            }}
            
            #ColorPickerDialog QPushButton#ColorSwatch:disabled {{
                opacity: 0.5;
            }}
            
            QFrame {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        # Update individual button colors
        for i, (color_hex, color_name) in enumerate(current_colors):
            if i < len(self.color_buttons):
                btn = self.color_buttons[i]
                # Update the stylesheet to use the correct color for this button
                btn_style = f"""
                    QPushButton#ColorSwatch {{
                        background-color: {color_hex};
                        border: none;
                        border-radius: {self.tile_size // 6}px;
                        outline: none;
                        min-width: {self.tile_size}px;
                        min-height: {self.tile_size}px;
                    }}
                    QPushButton#ColorSwatch:hover {{
                        border: 3px solid #ffffff;
                    }}
                    QPushButton#ColorSwatch:checked {{
                        border: 4px solid #ffffff;
                    }}
                    QPushButton#ColorSwatch:focus {{
                        box-shadow: 0 0 0 2px rgba(255,255,255,0.25);
                    }}
                    QPushButton#ColorSwatch:disabled {{
                        opacity: 0.5;
                    }}
                """
                btn.setStyleSheet(btn_style)
    
    def resizeEvent(self, event):
        """Handle resize events to recalculate tile size"""
        super().resizeEvent(event)
        self._update_tile_size()
        self.updateGeometry()
    
    def _update_tile_size(self):
        """Calculate and apply dynamic tile size based on parent height"""
        if self.parent():
            parent_height = self.parent().height()
            # Calculate tile size: 6% of parent height, clamped between 32 and 96
            new_tile_size = clamp(int(parent_height * 0.06), 32, 96)
            
            if new_tile_size != self.tile_size:
                self.tile_size = new_tile_size
                
                # Update grid spacing based on tile size
                spacing = self.tile_size // 6
                self.grid_layout.setHorizontalSpacing(spacing)
                self.grid_layout.setVerticalSpacing(spacing)
                
                # Update margins based on tile size
                margin = self.tile_size // 4
                self.color_frame.layout().setContentsMargins(margin, margin, margin, margin)
                
                # Reapply theme to update button sizes
                self.apply_theme()
    
    def showEvent(self, event):
        """Calculate tile size when dialog is shown"""
        super().showEvent(event)
        self._update_tile_size()
    
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