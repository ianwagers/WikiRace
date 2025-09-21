
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt
from src.logic.ThemeManager import theme_manager

class SettingsPage(QWidget):
    def __init__(self, tabWidget, parent = None):
        super().__init__(parent)
        self.tabWidget = tabWidget
        self.initUI()

    def initUI(self):
        # Apply theme styling
        self.apply_theme()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Title label
        self.titleLabel = QLabel("Settings")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.titleLabel)

        # Theme selection (moved to top)
        self.create_theme_section()
        
        # Add stretch to push content to top
        self.layout.addStretch()

        # Set the layout for the widget
        self.setLayout(self.layout)
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def create_theme_section(self):
        """Create the theme selection section"""
        # Theme section container
        self.theme_container = QWidget()
        self.theme_container.setMaximumWidth(300)
        self.update_theme_container_styling()
        
        # Theme selection layout
        theme_layout = QHBoxLayout(self.theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(80)
        
        # Theme label
        self.themeLabel = QLabel("Theme:")
        self.themeLabel.setObjectName("themeLabel")
        theme_layout.addWidget(self.themeLabel)
        
        # Add stretch to push combo to the right
        theme_layout.addStretch()
        
        # Theme combo box
        self.themeCombo = QComboBox()
        self.themeCombo.addItems(['Dark', 'Light'])
        self.themeCombo.setCurrentText(theme_manager.get_theme().title())
        self.themeCombo.currentTextChanged.connect(self.on_theme_combo_changed)
        theme_layout.addWidget(self.themeCombo)
        
        # Center the theme container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(self.theme_container)
        container_layout.addStretch()
        
        # Add theme section to main layout
        self.layout.addLayout(container_layout)
    
    def update_theme_container_styling(self):
        """Update the theme container styling"""
        styles = theme_manager.get_theme_styles()
        self.theme_container.setStyleSheet(f"""
            QWidget {{
                background-color: {styles['card_background']};
                border: 1px solid {styles['card_border']};
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }}
        """)
    
    def apply_theme(self):
        """Apply the current theme to the settings page"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel {{
                color: {styles['text_color']};
                font-size: 18px;
                font-weight: bold;
                padding: 10px 20px;
            }}
            QLabel[objectName="themeLabel"] {{
                color: {styles['accent_color']};
                font-weight: bold;
                font-size: 14px;
            }}
            QComboBox {{
                background-color: {styles['input_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['input_border']};
                border-radius: 6px;
                padding: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                min-width: 80px;
                font-weight: normal;
            }}
            QComboBox:hover {{
                border-color: {styles['border_hover']};
            }}
            QComboBox:focus {{
                border-color: {styles['input_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {styles['text_color']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {styles['input_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['input_border']};
                selection-background-color: {styles['tertiary_background']};
                font-weight: normal;
            }}
            QComboBox QAbstractItemView::item {{
                color: {styles['text_color']};
                background-color: transparent;
                padding: 8px 12px;
                font-weight: normal;
                border: none;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {styles['tertiary_background']};
                color: {styles['text_color']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {styles['tertiary_background']};
                color: {styles['text_color']};
            }}
        """)
    
    def on_theme_combo_changed(self, theme_text):
        """Handle theme change from combo box"""
        theme = theme_text.lower()
        print(f"🎨 WikiRace: Settings page - Theme changed to: {theme}")
        theme_manager.set_theme(theme)
    
    def on_theme_changed(self, theme):
        """Handle theme change from theme manager"""
        print(f"🎨 WikiRace: Settings page - Theme changed to: {theme}")
        # Update the combo box to reflect the new theme
        if hasattr(self, 'themeCombo'):
            self.themeCombo.setCurrentText(theme.title())
        # Reapply theme styles
        self.apply_theme()
        # Update theme container styling
        if hasattr(self, 'theme_container'):
            self.update_theme_container_styling()
