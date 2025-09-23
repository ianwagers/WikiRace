import time
from PyQt6.QtGui import QIcon, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QFrame, QDialog, QComboBox, QLineEdit
from PyQt6.QtCore import Qt, QSize, QUrl, QRect
from PyQt6.QtWebEngineCore import QWebEngineProfile
from src.logic.GameLogic import GameLogic
from src.gui.components.WikipediaTheme import WikipediaTheme
from src.gui.components.ConfettiEffect import ConfettiWidget
from src.logic.ThemeManager import theme_manager

# Import the URL interceptor
from src.gui.components.UrlInterceptor import WikipediaUrlInterceptor


class HomePage(QWidget):

    def __init__(self, tabWidget, mainApplication):
        super().__init__()
        self.darkModeApplied = False  # Track if dark mode has been applied
        self.tabWidget = tabWidget
        self.mainApplication = mainApplication
        
        # ===== TITLE POSITIONING CONFIGURATION =====
        # Easily modify these values to adjust "Race" text positioning
        self.RACE_TEXT_VERTICAL_OFFSET = 0  # Negative values move text up, positive down
        self.RACE_TEXT_HORIZONTAL_OFFSET = 10  # Negative values move text left, positive right
        self.RACE_TEXT_MARGIN_LEFT = 0  # Additional left margin
        self.RACE_TEXT_MARGIN_TOP = 0   # Additional top margin
        # ===========================================

        # Check if tabWidget has a layout, if not, set a new layout
        if tabWidget.layout() is None:
            tabWidget.setLayout(QVBoxLayout())  # Or any other layout

        self.setStyles()

        # Now it's safe to get and modify the layout
        self.layout = tabWidget.layout()
        self.layout.setContentsMargins(20, 15, 20, 20)
        self.layout.setSpacing(8)

        # Title Image - WIKIRACE Logo (single word with WIKI as one block and RACE with gradient)
        self.titleImage = QLabel()
        # Use HTML to create the stylized WIKIRACE text with WIKI as one block and RACE with gradient
        self.updateTitleStyling()
        
        self.titleImage.setScaledContents(True)
        self.titleImage.setMaximumSize(280, 50)
        self.titleImage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a container for the single logo
        self.logoContainer = QFrame()
        self.logoLayout = QHBoxLayout(self.logoContainer)
        self.logoLayout.setContentsMargins(0, 0, 0, 0)
        self.logoLayout.setSpacing(0)
        self.logoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add the single WIKIRACE logo to container
        self.logoLayout.addWidget(self.titleImage, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(self.logoContainer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title subscript with modern styling - positioned right edge with low opacity
        self.titleSubscript = QLabel("v1.7 [BETA]")
        self.titleSubscript.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: rgba(102, 102, 102, 0.6);
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 300;
                background: transparent;
            }
        """)
        self.titleSubscript.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.titleSubscript.setContentsMargins(0, 0, 20, 0)
        self.layout.addWidget(self.titleSubscript)
        

        # Frame for the buttons with refined card styling
        self.buttonsFrame = QFrame()
        # Set maximum width to prevent floating appearance
        self.buttonsFrame.setMaximumWidth(400)
        self.buttonsLayout = QHBoxLayout(self.buttonsFrame)
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setSpacing(6)
        self.buttonsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Modern styled buttons with proper sizing (15-20% smaller)
        self.soloGameButton = QPushButton("Solo Race")
        self.soloGameButton.setMinimumHeight(36)
        self.soloGameButton.setMinimumWidth(115)
        self.soloGameButton.setMaximumWidth(145)

        self.multiplayerButton = QPushButton("Multiplayer")
        self.multiplayerButton.setMinimumHeight(36)
        self.multiplayerButton.setMinimumWidth(115)
        self.multiplayerButton.setMaximumWidth(145)

        self.soloGameButton.setCheckable(True)
        self.multiplayerButton.setCheckable(True)
        
        self.settingsButton = QPushButton("Settings")
        self.settingsButton.setMinimumHeight(36)
        self.settingsButton.setMinimumWidth(115)
        self.settingsButton.setMaximumWidth(145)

        # Adding buttons to the layout
        self.buttonsLayout.addWidget(self.soloGameButton)
        self.buttonsLayout.addWidget(self.multiplayerButton)
        self.buttonsLayout.addWidget(self.settingsButton)

        # Add modest outer margin to prevent buttons from feeling glued to the edge
        self.buttonsFrame.setContentsMargins(8, 0, 0, 0)
        self.layout.addWidget(self.buttonsFrame)

        # Wikipedia content area with theme container
        self.contentFrame = QFrame()
        self.contentLayout = QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        
        # Web view with Wikipedia theme
        self.webView = QWebEngineView()
        self.webView.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # OPTIMIZED: Set up persistent profile with disk cache for better performance
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50MB cache
        
        # Set up URL interceptor to handle useskin=vector-2022 before navigation
        self.url_interceptor = WikipediaUrlInterceptor()
        profile.setUrlRequestInterceptor(self.url_interceptor)
        
        # OPTIMIZED: Set up Wikipedia theme with navigation hiding in one go
        WikipediaTheme.setupThemeWithNavigation(self.webView, theme_manager.get_theme())
        
        # Hide the webview initially to prevent flash of light content
        self.webView.setVisible(False)
        
        # Connect signals before loading
        self.webView.page().loadStarted.connect(self.onLoadStarted)
        self.webView.page().loadFinished.connect(self.onPageLoaded)
        self.webView.urlChanged.connect(self.onUrlChanged)
        
        # Ensure Vector 2022 skin is used for theme support
        main_page_url = WikipediaTheme.ensureVector2022Skin("https://en.wikipedia.org/wiki/Main_Page")
        
        # Start loading the page
        self.webView.load(QUrl(main_page_url))
        self.contentLayout.addWidget(self.webView)
        
        self.layout.addWidget(self.contentFrame)
        
        # OPTIMIZED: No delay needed - theme is applied instantly at DocumentCreation
        self.webView.setVisible(True)
        
        # Apply initial styling after all widgets are created
        self.updateButtonStyling()
        self.updateContentFrameStyling()

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Button connections
        self.soloGameButton.clicked.connect(self.onSoloGameClicked)
        self.multiplayerButton.clicked.connect(self.onMultiplayerClicked)
        self.settingsButton.clicked.connect(self.onSettingsClicked)

        # Create an instance of GameLogic before calling startGame()
        self.game_logic_instance = GameLogic()
        
        # Create confetti widget (initially hidden)
        self.confetti_widget = ConfettiWidget(self)
        self.confetti_widget.hide()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Connect to tab widget changes to uncheck buttons when returning to home page
        self.tabWidget.currentChanged.connect(self.on_tab_changed)


    def onLoadStarted(self):
        """Handle page load started - theme is already set via cookies"""
        current_theme = theme_manager.get_theme()
        print(f"🚀 WikiRace: HomePage - Page load started - Wikipedia {current_theme} theme should be active via mwclientpreferences cookie")
        print(f"🚀 WikiRace: HomePage - Loading URL: {self.webView.url().toString()}")

    def onPageLoaded(self, success):
        """Handle page load finished - verify theme was applied"""
        if success:
            current_theme = theme_manager.get_theme()
            print(f"✅ WikiRace: HomePage - Page loaded successfully with Wikipedia {current_theme} theme")
            print(f"✅ WikiRace: HomePage - Final URL: {self.webView.url().toString()}")
            
            # Check if this is the Wikipedia main page and apply customization
            current_url = self.webView.url().toString()
            if "en.wikipedia.org/wiki/Main_Page" in current_url:
                print("🏠 WikiRace: HomePage - Detected Wikipedia main page, applying customization...")
                WikipediaTheme.applyMainPageCustomization(self.webView)
            
            # Verify theme was applied (for debugging)
            print(f"🔍 WikiRace: HomePage - Running {current_theme} mode verification...")
            WikipediaTheme.verifyDarkModeApplied(self.webView)
            
            # Also check what cookies are actually in the browser
            print("🍪 WikiRace: HomePage - Checking cookies in browser...")
            WikipediaTheme.checkCookiesInBrowser(self.webView)
            
            # If theme wasn't applied properly, force it
            print(f"🔧 WikiRace: HomePage - Attempting to force {current_theme} theme as fallback...")
            WikipediaTheme.forceTheme(self.webView, current_theme)
            
            # OPTIMIZED: Navigation elements are hidden automatically by DOMContentLoaded script
            print(f"✅ WikiRace: [{time.time():.3f}] HomePage - Navigation elements handled by automatic script")
            
            self.darkModeApplied = True
        else:
            print("❌ WikiRace: HomePage - Page load failed")

    def onUrlChanged(self, url):
        """Handle URL changes - URL interceptor handles useskin parameter automatically"""
        url_str = url.toString()
        print(f"🔄 WikiRace: HomePage - URL changed to: {url_str}")
        
        # OPTIMIZED: URL interceptor handles useskin=vector-2022 automatically
        # No need to reload - prevents redirect loops and double loading
        self.darkModeApplied = False  # Reset flag for new page
        
        # Check if this is the Wikipedia main page and apply customization
        if "en.wikipedia.org/wiki/Main_Page" in url_str:
            print("🏠 WikiRace: HomePage - Detected Wikipedia main page in URL change, applying customization...")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: WikipediaTheme.applyMainPageCustomization(self.webView))
        
        # Schedule hiding navigation elements after a brief delay to ensure page is loaded
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, lambda: WikipediaTheme.hideNavigationElements(self.webView))

    def showWebView(self):
        """Show the webview after theme has been applied"""
        self.webView.setVisible(True)
    
    def triggerConfetti(self):
        """Trigger confetti effect when race is completed"""
        # Position confetti widget to cover the entire home page
        self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
        self.confetti_widget.raise_()  # Bring to front
        self.confetti_widget.startConfetti(3000)  # 3 second confetti effect
    
    def resizeEvent(self, event):
        """Handle resize events to reposition confetti widget"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti_widget'):
            self.confetti_widget.setGeometry(0, 0, self.width(), self.height())

    def onSoloGameClicked(self):
            # Uncheck the button immediately after click
            self.soloGameButton.setChecked(False)
            
            dialog = CustomGameDialog(self)
            if dialog.exec():
                starting_page_choice = dialog.startPageCombo.currentText()
                ending_page_choice = dialog.endPageCombo.currentText()
                custom_starting_page = dialog.customStartPageEdit.text() if starting_page_choice == 'Custom' else starting_page_choice
                custom_ending_page = dialog.customEndPageEdit.text() if ending_page_choice == 'Custom' else ending_page_choice

                result = self.game_logic_instance.startGame(self, custom_starting_page, custom_ending_page)
                if len(result) == 4:
                    self.start_url, self.end_url, self.start_title, self.end_title = result
                else:
                    # Backward compatibility
                    self.start_url, self.end_url = result
                    self.start_title, self.end_title = None, None
                self.addSoloGameTab(self.start_url, self.end_url, self.start_title, self.end_title)

    def addSoloGameTab(self, start_url, end_url, start_title=None, end_title=None):
        if not hasattr(self.mainApplication, 'soloGamePage'):
            self.mainApplication.addSoloGameTab(start_url, end_url, start_title, end_title)
            index = self.tabWidget.indexOf(self.mainApplication.soloGamePage)
            self.tabWidget.setCurrentIndex(index)
        else:
            index = self.tabWidget.indexOf(self.mainApplication.soloGamePage)
            self.mainApplication.closeTab(index)
            self.mainApplication.addSoloGameTab(start_url, end_url, start_title, end_title)
            self.tabWidget.setCurrentIndex(index)

    def onMultiplayerClicked(self):
        # Uncheck the button immediately after click
        self.multiplayerButton.setChecked(False)
        
        # Open the multiplayer tab
        if not hasattr(self.mainApplication, 'multiplayerPage') or self.tabWidget.indexOf(self.mainApplication.multiplayerPage) == -1:
            self.mainApplication.addMultiplayerTab()
            # Switch to the newly created tab
            index = self.tabWidget.indexOf(self.mainApplication.multiplayerPage)
            self.tabWidget.setCurrentIndex(index)
        else:
            index = self.tabWidget.indexOf(self.mainApplication.multiplayerPage)
            self.tabWidget.setCurrentIndex(index)
    
    def onSettingsClicked(self):
        # Uncheck the button immediately after click
        self.settingsButton.setChecked(False)
        
        if not hasattr(self.mainApplication, 'settingsPage') or self.tabWidget.indexOf(self.mainApplication.settingsPage) == -1:
            self.mainApplication.addSettingsTab()
            # Switch to the newly created tab
            index = self.tabWidget.indexOf(self.mainApplication.settingsPage)
            self.tabWidget.setCurrentIndex(index)
        else:
            index = self.tabWidget.indexOf(self.mainApplication.settingsPage)
            self.tabWidget.setCurrentIndex(index)

    def openLinkInWebView(self, url):
        # Ensure Vector 2022 skin is used for theme support
        url_with_skin = WikipediaTheme.ensureVector2022Skin(url)
        # Convert string URL to QUrl object
        qurl = QUrl(url_with_skin)
        self.webView.load(qurl)
        # Theme will be applied automatically via mwclientpreferences cookie

    def updateTitleStyling(self):
        """Update the WIKIRACE title styling based on current theme"""
        styles = theme_manager.get_theme_styles()
        
        self.titleImage.setText(f"""
        <html>
        <head>
        <style>
        .wikirace-logo {{
            font-family: 'Linux Libertine', 'Times New Roman', 'Times', serif;
            font-size: 36px;
            font-weight: 400;
            color: {styles['text_color']};
            background: {styles['background_color']};
            letter-spacing: 1px;
            font-style: normal;
            padding: 1px 16px;
            border-radius: 6px;
        }}
        .large-w {{
            font-size: 48px;
            font-weight: 600;
        }}
        .large-e {{
            font-size: 36px;
            font-weight: 400;
        }}
        .race-text {{
            font-family: 'Linux Libertine', 'Times New Roman', 'Times', serif;
            font-size: 36px;
            font-weight: 400;
            background: linear-gradient(90deg, #00FFFF 0%, #8A2BE2 50%, #FF00FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-style: italic;
            letter-spacing: 1px;
        }}
        </style>
        </head>
        <body>
        <div class="wikirace-logo">
            <span class="large-w">W</span>IKIRAC<span class="large-e">E</span></span>
        </div>
        </body>
        </html>
        """)
    
    def updateButtonStyling(self):
        """Update button styling based on current theme"""
        styles = theme_manager.get_theme_styles()
        
        # Update buttons frame styling - remove grey card background
        self.buttonsFrame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Update button styling - cleaner design with better hover states
        button_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.2px;
                padding: 0 14px;
                height: 36px;
            }}
            QPushButton:hover {{
                background-color: {styles.get('accent_weak', styles['button_hover'])};
                border-color: {styles.get('border_hover', styles['border_color'])};
            }}
            QPushButton:pressed, QPushButton:checked {{
                background-color: {styles.get('accent', styles['button_pressed'])};
                color: {styles.get('background_color', styles['text_color'])};
                border-color: {styles.get('border_pressed', styles['border_color'])};
            }}
            QPushButton:focus {{
                outline: none;
                border: 1px solid {styles['border_color']};
            }}
            QPushButton:focus-visible {{
                outline: none;
                border: 1px solid {styles['border_color']};
            }}
        """
        
        self.soloGameButton.setStyleSheet(button_style)
        self.multiplayerButton.setStyleSheet(button_style)
        self.settingsButton.setStyleSheet(button_style)
    
    def updateContentFrameStyling(self):
        """Update content frame styling based on current theme"""
        styles = theme_manager.get_theme_styles()
        
        self.contentFrame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles['background_color']};
                border-radius: 0px;
                border: 0px solid {styles['border_color']};
                margin: 0px;
            }}
        """)
        
        self.webView.setStyleSheet(f"""
            QWebEngineView {{
                background-color: {styles['background_color']};
                border-radius: 0px;
            }}
        """)
    
    def refreshWikipediaPage(self):
        """Refresh the Wikipedia page to apply new theme"""
        if hasattr(self, 'webView') and self.webView:
            current_url = self.webView.url().toString()
            if current_url and "wikipedia.org" in current_url:
                print(f"🔄 WikiRace: Refreshing Wikipedia page to apply {theme_manager.get_theme()} theme")
                # OPTIMIZED: Re-setup theme with navigation hiding in one go
                WikipediaTheme.setupThemeWithNavigation(self.webView, theme_manager.get_theme())
                # Reload the page
                self.webView.reload()
    
    def on_theme_changed(self, theme):
        """Handle theme changes"""
        print(f"🎨 WikiRace: HomePage - Theme changed to: {theme}")
        
        # Update all styling
        self.updateTitleStyling()
        self.updateButtonStyling()
        self.updateContentFrameStyling()
        self.setStyles()
        
        # Refresh Wikipedia page to apply new theme
        self.refreshWikipediaPage()
    
    def on_tab_changed(self, index):
        """Handle tab changes to uncheck buttons when returning to home page"""
        # Get the current tab widget
        current_widget = self.tabWidget.widget(index)
        
        # If we're on the home page (this widget), uncheck all buttons
        if current_widget == self:
            self.uncheck_all_buttons()
    
    def uncheck_all_buttons(self):
        """Uncheck all buttons to remove highlighting"""
        self.soloGameButton.setChecked(False)
        self.multiplayerButton.setChecked(False)
        self.settingsButton.setChecked(False)

    def setStyles(self):
        """Apply theme-based styles"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {styles['background_color']};
            color: {styles['text_color']};
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }}

        QLabel {{
            color: {styles['text_color']};
            font-size: 14px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        }}

        QMainWindow {{
            background-color: {styles['background_color']};
        }}
        """)

        # Theme for QTabWidget
        self.tabWidget.setStyleSheet(f"""
        QTabWidget::pane {{
            border-top: 2px solid {styles['border_color']};
            background-color: {styles['background_color']};
        }}

        QTabBar::tab {{
            background: {styles['tab_background']};
            color: {styles['tab_text']};
            padding: 8px 16px;
            border: 1px solid {styles['border_color']};
            border-bottom-color: {styles['tab_background']};
            border-radius: 6px 6px 0px 0px;
            margin-right: 2px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 500;
        }}

        QTabBar::tab:selected, QTabBar::tab:hover {{
            background: {styles['tab_selected']};
            color: {styles['tab_text_selected']};
            border-color: {styles['border_hover']};
        }}

        QWidget {{
            background-color: {styles['background_color']};
            color: {styles['text_color']};
        }}
        """)

class CustomGameDialog(QDialog):
    def __init__(self, homePage):
        super().__init__(homePage)
        self.homePage = homePage
        self.setWindowTitle('Race Setup')
        self.apply_theme()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Layout for starting page selection
        startingPageLayout = QHBoxLayout()
        startingPageLabel = QLabel('Starting Page:')
        startingPageLabel.setObjectName("sectionLabel")
        self.startPageCombo = QComboBox()
        self.startPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 'Historical Events', 'Random', 'Custom'])
        if self.startPageCombo.currentText() == 'Custom':
            self.startPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        startingPageLayout.addWidget(startingPageLabel)
        startingPageLayout.addWidget(self.startPageCombo)
        self.layout.addLayout(startingPageLayout)

        # Line edit for custom starting page
        self.customStartPageEdit = QLineEdit()
        self.customStartPageEdit.setPlaceholderText('Enter custom starting page')
        self.customStartPageEdit.setEnabled(False)
        self.layout.addWidget(self.customStartPageEdit)

        # Layout for ending page selection
        endingPageLayout = QHBoxLayout()
        endingPageLabel = QLabel('Ending Page:')
        endingPageLabel.setObjectName("sectionLabel")
        self.endPageCombo = QComboBox()
        self.endPageCombo.addItems(['Animals', 'Buildings', 'Celebrities', 'Countries', 'Gaming', 'Literature', 'Music', 'STEM', 'Most Linked', 'US Presidents', 'Historical Events', 'Random', 'Custom'])
        if self.endPageCombo.currentText() == 'Custom':
            self.endPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        endingPageLayout.addWidget(endingPageLabel)
        endingPageLayout.addWidget(self.endPageCombo)
        self.layout.addLayout(endingPageLayout)

        # Line edit for custom ending page
        self.customEndPageEdit = QLineEdit()
        self.customEndPageEdit.setPlaceholderText('Enter custom ending page')
        self.customEndPageEdit.setEnabled(False)
        self.layout.addWidget(self.customEndPageEdit)

        # Start Game button
        self.startGameButton = QPushButton('Start Race!')
        self.layout.addWidget(self.startGameButton)
        
        # Connect signals
        self.startPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        self.endPageCombo.currentIndexChanged.connect(self.toggleCustomEntry)
        self.startGameButton.clicked.connect(self.startGameAndClose)

        # Set minimum dialog size for better UI experience
        self.setMinimumSize(275, 175)  # Example improvement for resizing
    
    def apply_theme(self):
        """Apply theme-based styles to the dialog"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
            }}
            QLabel {{
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel[objectName="sectionLabel"] {{
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
            }}
            QComboBox:hover {{
                border-color: {styles['border_hover']};
            }}
            QLineEdit {{
                background-color: {styles['input_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['input_border']};
                border-radius: 6px;
                padding: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {styles['input_focus']};
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
        """)
        
    def startGameAndClose(self):
        """Validate custom pages and start the game"""
        # Get the selected options
        starting_page_choice = self.startPageCombo.currentText()
        ending_page_choice = self.endPageCombo.currentText()
        
        # Check if custom pages need validation
        if starting_page_choice == 'Custom':
            custom_start = self.customStartPageEdit.text().strip()
            if not custom_start:
                self.showWarning("Please enter a starting page name.")
                return
            
            # Validate starting page exists
            url, title = self.homePage.game_logic_instance.findWikiPageWithTitle(custom_start)
            if url is None:
                self.showWarning(f'No page named "{custom_start}" exists. Please try something else.')
                return
        
        if ending_page_choice == 'Custom':
            custom_end = self.customEndPageEdit.text().strip()
            if not custom_end:
                self.showWarning("Please enter a destination page name.")
                return
            
            # Validate ending page exists
            url, title = self.homePage.game_logic_instance.findWikiPageWithTitle(custom_end)
            if url is None:
                self.showWarning(f'No page named "{custom_end}" exists. Please try something else.')
                return
        
        # If we get here, validation passed
        self.accept()  # Close the dialog
    
    def showWarning(self, message):
        """Show a warning dialog to the user"""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Page Not Found")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Apply theme to the message box
        styles = theme_manager.get_theme_styles()
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
            }}
            QMessageBox QLabel {{
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
                background-color: transparent;
            }}
            QMessageBox QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 500;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {styles['button_pressed']};
                border-color: {styles['border_pressed']};
            }}
            QMessageBox QIcon {{
                background-color: transparent;
            }}
        """)
        
        msg.exec()

    def toggleCustomEntry(self):
        isCustomStart = self.startPageCombo.currentText() == 'Custom'
        isCustomEnd = self.endPageCombo.currentText() == 'Custom'
        
        self.customStartPageEdit.setEnabled(isCustomStart)
        self.customEndPageEdit.setEnabled(isCustomEnd)
        
        # Reapply theme styling to ensure proper colors
        self.apply_theme()

class UnderConstructionDialog(QDialog):
    def __init__(self, parent=None):
        super(UnderConstructionDialog, self).__init__(parent)
        self.setWindowTitle("Under Construction")
        self.apply_theme()
        self.setFixedSize(300, 180)
        self.initUI()
    
    def apply_theme(self):
        """Apply theme-based styles to the dialog"""
        styles = theme_manager.get_theme_styles()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {styles['background_color']};
                color: {styles['text_color']};
            }}
            QLabel {{
                color: {styles['text_color']};
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            }}
            QLabel[objectName="titleLabel"] {{
                color: {styles['accent_color']};
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }}
            QLabel[objectName="iconLabel"] {{
                color: {styles['accent_secondary']};
                font-size: 40px;
                padding: 6px;
            }}
            QPushButton {{
                background-color: {styles['secondary_background']};
                color: {styles['text_color']};
                border: 1px solid {styles['border_color']};
                border-radius: 8px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {styles['button_hover']};
                border-color: {styles['border_hover']};
            }}
        """)

    def initUI(self):
        layout = QVBoxLayout(self)

        messageLabel = QLabel("Coming Soon...")
        messageLabel.setObjectName("titleLabel")
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(messageLabel)
        
        messageSubscript = QLabel("🚧")
        messageSubscript.setObjectName("iconLabel")
        messageSubscript.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(messageSubscript)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)
