"""
ServerConfigDialog - Configuration dialog for multiplayer server settings

Allows users to change server host, port, and connection settings
from the client interface.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QSpinBox, QCheckBox,
                            QGroupBox, QFormLayout, QMessageBox, QTabWidget,
                            QWidget, QSlider, QSpacerItem, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator
from src.logic.ThemeManager import theme_manager
import json
import os


class ServerConfigDialog(QDialog):
    """Dialog for configuring multiplayer server connection settings"""
    
    # Signal emitted when configuration is saved
    config_saved = pyqtSignal(dict)
    
    def __init__(self, current_config=None, parent=None):
        super().__init__(parent)
        self.current_config = current_config or self.get_default_config()
        
        self.initUI()
        self.apply_theme()
        self.load_config()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def get_default_config(self):
        """Get default configuration values"""
        return {
            'server_host': 'wikirace.duckdns.org',  # Updated to use your DDNS domain
            'server_port': 8001,  # Changed to match server default
            'auto_reconnect': True,
            'max_reconnection_attempts': 5,
            'reconnection_delay': 2.0,
            'max_reconnection_delay': 30.0,
            'connection_timeout': 10.0,
            'auto_discovery': True  # Enable auto-discovery by default
        }
    
    def initUI(self):
        """Initialize the configuration dialog UI"""
        self.setWindowTitle("Multiplayer Server Configuration")
        self.setModal(True)
        self.setFixedSize(750, 600)  # Further increased for better visibility and to prevent cutoff
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🔧 Server Configuration")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Connection tab
        self.create_connection_tab()
        
        # Reconnection tab
        self.create_reconnection_tab()
        
        # Advanced tab
        self.create_advanced_tab()
        
        # Auto-discovery tab
        self.create_auto_discovery_tab()
        
        # Buttons with improved layout for better readability
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Add spacing between buttons
        
        button_layout.addStretch()
        
        # Reset to defaults
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setMinimumWidth(150)  # Ensure adequate width
        button_layout.addWidget(reset_button)
        
        # Cancel/Save buttons
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumWidth(100)  # Ensure adequate width
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save & Apply")
        save_button.setDefault(True)
        save_button.clicked.connect(self.save_config)
        save_button.setMinimumWidth(120)  # Ensure adequate width
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def create_connection_tab(self):
        """Create the connection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Server connection group
        conn_group = QGroupBox("Server Connection")
        conn_layout = QFormLayout(conn_group)
        conn_layout.setSpacing(10)
        
        # Server host
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g., 127.0.0.1 or server.example.com")
        conn_layout.addRow("Server Host:", self.host_input)
        
        # Server port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8001)
        conn_layout.addRow("Server Port:", self.port_input)
        
        # Connection timeout
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(5, 60)
        self.timeout_input.setSuffix(" seconds")
        conn_layout.addRow("Connection Timeout:", self.timeout_input)
        
        layout.addWidget(conn_group)
        
        # Connection info
        info_label = QLabel("💡 Enter the host and port of your WikiRace multiplayer server.\n"
                          "For local testing, use 127.0.0.1:8001")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Connection")
    
    def create_reconnection_tab(self):
        """Create the reconnection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Auto-reconnect group
        reconnect_group = QGroupBox("Automatic Reconnection")
        reconnect_layout = QVBoxLayout(reconnect_group)
        reconnect_layout.setSpacing(15)
        
        # Enable auto-reconnect
        self.auto_reconnect_checkbox = QCheckBox("Enable automatic reconnection")
        self.auto_reconnect_checkbox.setChecked(True)
        self.auto_reconnect_checkbox.toggled.connect(self.on_auto_reconnect_toggled)
        reconnect_layout.addWidget(self.auto_reconnect_checkbox)
        
        # Reconnection settings (in a form)
        self.reconnect_form = QWidget()
        form_layout = QFormLayout(self.reconnect_form)
        form_layout.setSpacing(10)
        
        # Max attempts
        self.max_attempts_input = QSpinBox()
        self.max_attempts_input.setRange(1, 20)
        self.max_attempts_input.setValue(5)
        form_layout.addRow("Max Reconnection Attempts:", self.max_attempts_input)
        
        # Initial delay
        self.initial_delay_input = QSpinBox()
        self.initial_delay_input.setRange(1, 30)
        self.initial_delay_input.setSuffix(" seconds")
        self.initial_delay_input.setValue(2)
        form_layout.addRow("Initial Delay:", self.initial_delay_input)
        
        # Max delay
        self.max_delay_input = QSpinBox()
        self.max_delay_input.setRange(5, 120)
        self.max_delay_input.setSuffix(" seconds")
        self.max_delay_input.setValue(30)
        form_layout.addRow("Maximum Delay:", self.max_delay_input)
        
        reconnect_layout.addWidget(self.reconnect_form)
        
        layout.addWidget(reconnect_group)
        
        # Reconnection info
        info_label = QLabel("💡 Automatic reconnection will attempt to restore your connection\n"
                          "if the server becomes temporarily unavailable.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Reconnection")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(10)
        
        # Server URL display
        self.server_url_label = QLabel()
        # Theme will be applied in apply_theme method
        advanced_layout.addRow("Full Server URL:", self.server_url_label)
        
        # Update URL when host/port changes
        self.host_input.textChanged.connect(self.update_server_url)
        self.port_input.valueChanged.connect(self.update_server_url)
        
        layout.addWidget(advanced_group)
        
        # Configuration file info
        config_group = QGroupBox("Configuration Storage")
        config_layout = QVBoxLayout(config_group)
        
        config_info = QLabel("Settings are stored locally and will persist between sessions.\n"
                           "You can reset to defaults at any time.")
        config_info.setWordWrap(True)
        config_info.setStyleSheet("color: #666;")
        config_layout.addWidget(config_info)
        
        # Show config file location
        config_file = self.get_config_file_path()
        config_path_label = QLabel(f"Config file: {config_file}")
        config_path_label.setStyleSheet("font-family: monospace; font-size: 10px; color: #888;")
        config_path_label.setWordWrap(True)
        config_layout.addWidget(config_path_label)
        
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Advanced")
    
    def create_auto_discovery_tab(self):
        """Create auto-discovery tab for finding available servers"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Auto-discovery section
        discovery_group = QGroupBox("🔍 Auto-Discovery")
        discovery_layout = QVBoxLayout()
        
        # Description
        desc_label = QLabel("Automatically find and connect to available WikiRace servers")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-style: italic;")
        discovery_layout.addWidget(desc_label)
        
        # Discover button
        self.discover_button = QPushButton("🔍 Discover Available Servers")
        self.discover_button.clicked.connect(self.discover_servers)
        discovery_layout.addWidget(self.discover_button)
        
        # Server list
        self.server_list = QComboBox()
        self.server_list.setPlaceholderText("No servers discovered yet")
        discovery_layout.addWidget(self.server_list)
        
        # Connect button
        self.connect_button = QPushButton("🚀 Connect to Selected Server")
        self.connect_button.clicked.connect(self.connect_to_selected_server)
        self.connect_button.setEnabled(False)
        discovery_layout.addWidget(self.connect_button)
        
        # Enable server selection when combo box changes
        self.server_list.currentTextChanged.connect(
            lambda: self.connect_button.setEnabled(bool(self.server_list.currentText()))
        )
        
        discovery_group.setLayout(discovery_layout)
        layout.addWidget(discovery_group)
        
        # Manual entry section
        manual_group = QGroupBox("✏️ Manual Entry")
        manual_layout = QFormLayout()
        
        self.manual_host = QLineEdit()
        self.manual_host.setPlaceholderText("wikirace.duckdns.org")
        self.manual_host.setText("wikirace.duckdns.org")  # Default to your domain
        manual_layout.addRow("Server Address:", self.manual_host)
        
        self.manual_port = QSpinBox()
        self.manual_port.setRange(1, 65535)
        self.manual_port.setValue(8001)
        manual_layout.addRow("Port:", self.manual_port)
        
        self.manual_connect = QPushButton("Connect Manually")
        self.manual_connect.clicked.connect(self.connect_manually)
        manual_layout.addWidget(self.manual_connect)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        # Quick connect section
        quick_group = QGroupBox("⚡ Quick Connect")
        quick_layout = QVBoxLayout()
        
        quick_desc = QLabel("One-click connection to common WikiRace servers:")
        quick_desc.setWordWrap(True)
        quick_desc.setStyleSheet("color: #666; font-style: italic;")
        quick_layout.addWidget(quick_desc)
        
        # Quick connect buttons
        quick_buttons_layout = QHBoxLayout()
        
        self.quick_local = QPushButton("🏠 Local Server")
        self.quick_local.clicked.connect(lambda: self.quick_connect("127.0.0.1:8001"))
        quick_buttons_layout.addWidget(self.quick_local)
        
        self.quick_domain = QPushButton("🌐 WikiRace Server")
        self.quick_domain.clicked.connect(lambda: self.quick_connect("wikirace.duckdns.org:8001"))
        quick_buttons_layout.addWidget(self.quick_domain)
        
        self.quick_ip = QPushButton("📡 Direct IP")
        self.quick_ip.clicked.connect(lambda: self.quick_connect("71.237.25.28:8001"))
        quick_buttons_layout.addWidget(self.quick_ip)
        
        quick_layout.addLayout(quick_buttons_layout)
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Auto-Discovery")
    
    def on_auto_reconnect_toggled(self, enabled):
        """Handle auto-reconnect toggle"""
        self.reconnect_form.setEnabled(enabled)
    
    def update_server_url(self):
        """Update the server URL display"""
        host = self.host_input.text() or "127.0.0.1"
        port = self.port_input.value()
        url = f"http://{host}:{port}"
        self.server_url_label.setText(url)
    
    def load_config(self):
        """Load configuration into the UI"""
        config = self.current_config
        
        # Connection settings
        self.host_input.setText(config.get('server_host', '127.0.0.1'))
        self.port_input.setValue(config.get('server_port', 8001))
        self.timeout_input.setValue(int(config.get('connection_timeout', 10)))
        
        # Reconnection settings
        self.auto_reconnect_checkbox.setChecked(config.get('auto_reconnect', True))
        self.max_attempts_input.setValue(config.get('max_reconnection_attempts', 5))
        self.initial_delay_input.setValue(int(config.get('reconnection_delay', 2)))
        self.max_delay_input.setValue(int(config.get('max_reconnection_delay', 30)))
        
        # Update dependent UI
        self.on_auto_reconnect_toggled(self.auto_reconnect_checkbox.isChecked())
        self.update_server_url()
    
    def get_config(self):
        """Get current configuration from UI"""
        return {
            'server_host': self.host_input.text().strip() or '127.0.0.1',
            'server_port': self.port_input.value(),
            'auto_reconnect': self.auto_reconnect_checkbox.isChecked(),
            'max_reconnection_attempts': self.max_attempts_input.value(),
            'reconnection_delay': float(self.initial_delay_input.value()),
            'max_reconnection_delay': float(self.max_delay_input.value()),
            'connection_timeout': float(self.timeout_input.value())
        }
    
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_config = self.get_default_config()
            self.load_config()
    
    def save_config(self):
        """Save configuration and close dialog"""
        config = self.get_config()
        
        # Validate configuration
        if not config['server_host']:
            QMessageBox.warning(self, "Invalid Configuration", "Server host cannot be empty.")
            return
        
        if config['reconnection_delay'] >= config['max_reconnection_delay']:
            QMessageBox.warning(self, "Invalid Configuration", 
                              "Initial delay must be less than maximum delay.")
            return
        
        # Save to file
        try:
            self.save_config_to_file(config)
            self.config_saved.emit(config)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{e}")
    
    def get_config_file_path(self):
        """Get the path to the configuration file"""
        # Use AppData on Windows, fallback to home directory on other platforms
        import os
        from pathlib import Path
        
        appdata = os.getenv('APPDATA')
        if appdata:
            config_dir = Path(appdata) / "wikirace"
        else:
            # Fallback for non-Windows systems
            config_dir = Path.home() / ".wikirace"
        
        config_dir.mkdir(exist_ok=True)
        return config_dir / "multiplayer_config.json"
    
    def save_config_to_file(self, config):
        """Save configuration to file"""
        config_file = self.get_config_file_path()
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config_from_file(self):
        """Load configuration from file"""
        config_file = self.get_config_file_path()
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
        
        return self.get_default_config()
    
    def apply_theme(self):
        """Apply theme-based styling"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel {{
                color: {styles['text_color']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {styles['border_color']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 6px;
                padding: 10px 20px;  # Increased padding for better readability
                font-weight: 600;
                font-size: 14px;  # Ensure consistent font size
                min-width: 140px;  # Further increased for button text visibility
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {styles['button_pressed']};
            }}
            QPushButton:default {{
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
                color: white;
            }}
            QPushButton:default:hover {{
                background-color: #45a049;
                border-color: #45a049;
            }}
            QLineEdit, QSpinBox {{
                border: 1px solid {styles['border_color']};
                border-radius: 4px;
                padding: 6px;
                background-color: {styles['input_background']};
                color: {styles['text_color']};
            }}
            QTabWidget::pane {{
                border: 1px solid {styles['border_color']};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {styles['button_hover']};
                border-bottom: 1px solid {styles['background_color']};
            }}
            QCheckBox {{
                color: {styles['text_color']};
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {styles['border_color']};
                border-radius: 3px;
                background-color: {styles['input_background']};
            }}
            QCheckBox::indicator:checked {{
                background-color: #4CAF50;
                border-color: #4CAF50;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #45a049;
                border-color: #45a049;
            }}
            QPushButton:disabled {{
                background-color: #495057;
                color: #6c757d;
                border-color: #6c757d;
            }}
        """)
        
        # Apply theme-specific styling to server URL label
        if hasattr(self, 'server_url_label'):
            url_bg_color = styles['input_background'] if 'input_background' in styles else styles['secondary_background']
            self.server_url_label.setStyleSheet(f"""
                font-family: monospace; 
                background-color: {url_bg_color}; 
                color: {styles['text_color']};
                padding: 8px; 
                border: 1px solid {styles['border_color']};
                border-radius: 4px;
            """)
    
    def discover_servers(self):
        """Discover available WikiRace servers"""
        from src.logic.Network import NetworkManager
        
        # Disable button during discovery
        self.discover_button.setEnabled(False)
        self.discover_button.setText("🔍 Discovering...")
        
        # Clear previous results
        self.server_list.clear()
        
        try:
            # Create a temporary NetworkManager for discovery
            temp_network = NetworkManager()
            
            # Get list of possible servers (including your specific ones)
            possible_servers = [
                "127.0.0.1:8001",  # Localhost
                "localhost:8001",  # Localhost alternative
                "71.237.25.28:8001",  # Your external IP
                "wikirace.duckdns.org:8001",  # Your dynamic DNS domain
            ]
            
            # Discover working servers
            working_servers = temp_network.auto_discover_servers(possible_servers)
            
            if working_servers:
                for server in working_servers:
                    display_text = f"{server['address']} ({server['status']})"
                    self.server_list.addItem(display_text, server)
                
                # Select first server by default
                self.server_list.setCurrentIndex(0)
                self.connect_button.setEnabled(True)
                
                QMessageBox.information(self, "Discovery Complete", 
                                      f"Found {len(working_servers)} working server(s)!")
            else:
                self.server_list.addItem("No servers found")
                QMessageBox.warning(self, "No Servers Found", 
                                  "No WikiRace servers are currently available.\n"
                                  "Make sure the server is running and accessible.")
                
        except Exception as e:
            QMessageBox.critical(self, "Discovery Error", f"Error discovering servers: {e}")
        finally:
            # Re-enable button
            self.discover_button.setEnabled(True)
            self.discover_button.setText("🔍 Discover Available Servers")
    
    def connect_to_selected_server(self):
        """Connect to the selected server from discovery"""
        if not self.server_list.currentData():
            QMessageBox.warning(self, "No Server Selected", "Please select a server first.")
            return
        
        server_data = self.server_list.currentData()
        host = server_data['host']
        port = server_data['port']
        
        # Update the main configuration
        self.host_input.setText(host)
        self.port_input.setValue(port)
        self.update_server_url()
        
        QMessageBox.information(self, "Server Selected", 
                              f"Connected to {host}:{port}\n\n"
                              f"Click 'Save & Apply' to use this server.")
    
    def connect_manually(self):
        """Connect to manually entered server"""
        host = self.manual_host.text().strip()
        port = self.manual_port.value()
        
        if not host:
            QMessageBox.warning(self, "Invalid Input", "Please enter a server address.")
            return
        
        # Update the main configuration
        self.host_input.setText(host)
        self.port_input.setValue(port)
        self.update_server_url()
        
        QMessageBox.information(self, "Manual Server Set", 
                              f"Server set to {host}:{port}\n\n"
                              f"Click 'Save & Apply' to use this server.")
    
    def quick_connect(self, server_address: str):
        """Quick connect to a predefined server"""
        if ':' not in server_address:
            server_address += ':8001'
        
        host, port = server_address.split(':')
        port = int(port)
        
        # Update the main configuration
        self.host_input.setText(host)
        self.port_input.setValue(port)
        self.update_server_url()
        
        QMessageBox.information(self, "Quick Connect", 
                              f"Connected to {server_address}\n\n"
                              f"Click 'Save & Apply' to use this server.")

    @staticmethod
    def get_saved_config():
        """Static method to get saved configuration"""
        dialog = ServerConfigDialog()
        return dialog.load_config_from_file()
