"""
Theme Management System for WikiRace
Handles dynamic theme switching between Dark and Light modes
"""

import os
import json
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication


class ThemeManager(QObject):
    """
    Manages application themes and settings persistence
    """
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"  # Default theme
        self.settings_file = self._get_settings_path()
        self._load_settings()
    
    def _get_settings_path(self) -> str:
        """Get the path to the settings file in AppData"""
        appdata = os.getenv('APPDATA')
        if not appdata:
            # Fallback if APPDATA is not available
            appdata = os.path.expanduser('~')
        
        wikirace_dir = os.path.join(appdata, 'wikirace')
        os.makedirs(wikirace_dir, exist_ok=True)
        
        return os.path.join(wikirace_dir, 'settings.json')
    
    def _load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'dark')
                    print(f"🎨 WikiRace: Loaded theme setting: {self.current_theme}")
            else:
                print("🎨 WikiRace: No settings file found, using default theme: dark")
        except Exception as e:
            print(f"❌ WikiRace: Error loading settings: {e}")
            self.current_theme = "dark"
    
    def _save_settings(self):
        """Save settings to JSON file"""
        try:
            settings = {
                'theme': self.current_theme
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            print(f"💾 WikiRace: Saved theme setting: {self.current_theme}")
        except Exception as e:
            print(f"❌ WikiRace: Error saving settings: {e}")
    
    def set_theme(self, theme: str):
        """Set the current theme and save to settings"""
        if theme not in ['dark', 'light']:
            print(f"⚠️ WikiRace: Invalid theme '{theme}', using 'dark'")
            theme = 'dark'
        
        if self.current_theme != theme:
            self.current_theme = theme
            self._save_settings()
            self.theme_changed.emit(theme)
            print(f"🎨 WikiRace: Theme changed to: {theme}")
    
    def get_theme(self) -> str:
        """Get the current theme"""
        return self.current_theme
    
    def get_theme_styles(self, theme: str = None) -> Dict[str, str]:
        """Get CSS styles for the specified theme"""
        if theme is None:
            theme = self.current_theme
        
        if theme == 'light':
            return self._get_light_theme_styles()
        else:
            return self._get_dark_theme_styles()
    
    def _get_dark_theme_styles(self) -> Dict[str, str]:
        """Get dark theme styles"""
        return {
            'background_color': '#101418',
            'secondary_background': '#2D2D2D',
            'tertiary_background': '#3E3E3E',
            'text_color': '#E0E0E0',
            'text_secondary': '#B0B0B0',
            'border_color': '#404040',
            'border_hover': '#00FFFF',
            'border_pressed': '#8A2BE2',
            'accent_color': '#00FFFF',
            'accent_secondary': '#8A2BE2',
            'button_hover': '#2f2f2f',
            'button_pressed': '#1E1E1E',
            'card_background': '#2D2D2D',
            'card_border': '#404040',
            'input_background': '#2D2D2D',
            'input_border': '#404040',
            'input_focus': '#00FFFF',
            'tab_background': '#2D2D2D',
            'tab_selected': '#3E3E3E',
            'tab_hover': '#3E3E3E',
            'tab_text': '#E0E0E0',
            'tab_text_selected': '#00FFFF'
        }
    
    def _get_light_theme_styles(self) -> Dict[str, str]:
        """Get light theme styles"""
        return {
            'background_color': '#FFFFFF',
            'secondary_background': '#F5F5F5',
            'tertiary_background': '#E8E8E8',
            'text_color': '#1A1A1A',
            'text_secondary': '#4A4A4A',
            'border_color': '#CCCCCC',
            'border_hover': '#0066CC',
            'border_pressed': '#8A2BE2',
            'accent_color': '#0066CC',
            'accent_secondary': '#8A2BE2',
            'button_hover': '#F0F0F0',
            'button_pressed': '#E0E0E0',
            'card_background': '#F5F5F5',
            'card_border': '#CCCCCC',
            'input_background': '#FFFFFF',
            'input_border': '#CCCCCC',
            'input_focus': '#0066CC',
            'tab_background': '#F5F5F5',
            'tab_selected': '#E8E8E8',
            'tab_hover': '#E8E8E8',
            'tab_text': '#1A1A1A',
            'tab_text_selected': '#0066CC'
        }
    
    def apply_theme_to_widget(self, widget: QWidget, theme: str = None):
        """Apply theme styles to a widget"""
        if theme is None:
            theme = self.current_theme
        
        styles = self.get_theme_styles(theme)
        
        # Apply base widget styles
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            
            QLabel {{
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            
            QMainWindow {{
                background-color: {styles['background_color']};
            }}
        """)
    
    def get_wikipedia_theme_setting(self, theme: str = None) -> str:
        """Get the Wikipedia theme setting for the specified theme"""
        if theme is None:
            theme = self.current_theme
        
        if theme == 'light':
            return 'skin-theme-clientpref-day'
        else:
            return 'skin-theme-clientpref-night'
    
    def get_wikipedia_theme_cookie_value(self, theme: str = None) -> bytes:
        """Get the Wikipedia theme cookie value for the specified theme"""
        if theme is None:
            theme = self.current_theme
        
        if theme == 'light':
            return b"skin-theme-clientpref-day"
        else:
            return b"skin-theme-clientpref-night"


# Global theme manager instance
theme_manager = ThemeManager()
