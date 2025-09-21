import time
import re
import urllib.parse
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QDialog
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings, QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt6.QtGui import QIcon
from src.gui.components.WikipediaTheme import WikipediaTheme
from src.gui.components.ConfettiEffect import ConfettiWidget
from src.gui.components.UrlInterceptor import WikipediaUrlInterceptor
from src.logic.ThemeManager import theme_manager

# PERFORMANCE: Disable debug DOM manipulation in production
DEBUG_THEME = False

class SoloGamePage(QWidget):

    def __init__(self, tabWidget, start_url, end_url, start_title=None, end_title=None, parent=None):
        init_start = time.time()
        print(f"🏁 WikiRace: [{init_start:.3f}] SoloGamePage initialization starting...")
        
        super(SoloGamePage, self).__init__(parent)
        self.tabWidget = tabWidget  # Assuming you need to use tabWidget as well
        self.start_url = start_url
        self.end_url = end_url
        self.start_title = start_title
        self.end_title = end_title
        self.startTime = 0
        self.linksUsed = 0  # Start at 0, will increment on first link click
        self.darkModeApplied = False  # Track if dark mode has been applied
        
        # Track page loading phases
        self.page_load_start_time = None
        self.url_change_time = None
        self.page_load_finish_time = None
        
        ui_start = time.time()
        self.initUI()  # Initialize the UI components
        ui_time = (time.time() - ui_start) * 1000
        total_init_time = (time.time() - init_start) * 1000
        print(f"🏁 WikiRace: [{time.time():.3f}] SoloGamePage initialization completed (UI: {ui_time:.1f}ms, TOTAL: {total_init_time:.1f}ms)")

    def getTitleFromUrlPath(self, url):
        """Extract page title from Wikipedia URL path - fast, no network calls"""
        try:
            # Parse the URL to extract the path
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            
            # Extract title from Wikipedia URL patterns
            if "/wiki/" in path:
                # Standard format: /wiki/Page_Title
                title = path.split("/wiki/")[1].split("?")[0].split("#")[0]
                # URL decode and replace underscores with spaces
                title = urllib.parse.unquote(title).replace("_", " ")
                return title
            elif "curid=" in url:
                # Page ID format - extract from query parameters
                query_params = urllib.parse.parse_qs(parsed.query)
                if "curid" in query_params:
                    return f"Page {query_params['curid'][0]}"
            elif "title=" in url:
                # Alternative format with title parameter
                query_params = urllib.parse.parse_qs(parsed.query)
                if "title" in query_params:
                    title = query_params["title"][0]
                    return urllib.parse.unquote(title).replace("_", " ")
            
            # Fallback: try to extract from any recognizable pattern
            if "wikipedia.org" in url:
                # Look for the last meaningful path segment
                path_parts = [p for p in path.split("/") if p and p != "wiki"]
                if path_parts:
                    title = path_parts[-1].split("?")[0].split("#")[0]
                    return urllib.parse.unquote(title).replace("_", " ")
            
            return "Unknown Page"
            
        except Exception as e:
            print(f"Error parsing title from URL {url}: {e}")
            return "Unknown Page"
    
    def getExactTitleFromJavaScript(self, callback):
        """Get exact display title using JavaScript after page load"""
        script = "document.title.split(' - Wikipedia')[0] || 'Unknown Page'"
        self.webView.page().runJavaScript(script, callback)

    def initUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)  # Main widget's layout

        # Container for sidebar and main content
        self.contentContainer = QWidget()  # Container widget
        self.contentLayout = QHBoxLayout(self.contentContainer)  # Layout for the container

        # Sidebar layout (25% width)
        self.sidebarLayout = QVBoxLayout()
        
        # Stopwatch label, links used counter, and previous links list setup
        self.stopwatchLabel = QLabel("00:00:00")
        self.stopwatchLabel.setStyleSheet("font-size: 26px")
        self.sidebarLayout.addWidget(self.stopwatchLabel)

        self.linksUsedLabel = QLabel("Links Used: " + str(self.linksUsed))
        self.linksUsedLabel.setStyleSheet("font-size: 16px")
        self.sidebarLayout.addWidget(self.linksUsedLabel)

        self.previousLinksList = QListWidget()
        self.sidebarLayout.addWidget(self.previousLinksList)

        # Sidebar container widget
        self.sidebarContainer = QWidget()
        self.sidebarContainer.setLayout(self.sidebarLayout)
        self.contentLayout.addWidget(self.sidebarContainer, 1)

        # Main content area layout
        self.mainContentLayout = QVBoxLayout()
        
        # Top-bar section
        destinationTitle = self.end_title if self.end_title else self.getTitleFromUrlPath(self.end_url)
        self.topBarLabel = QLabel("Destination page: " + destinationTitle)
        self.topBarLabel.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        self.mainContentLayout.addWidget(self.topBarLabel)

        # Initialize and configure the web view with Wikipedia theme
        # CRITICAL: Create fresh WebView to avoid profile contamination
        # DO NOT REMOVE: This ensures clean state for theme switching
        self.webView = QWebEngineView()
        
        # OPTIMIZED: Set up persistent profile with disk cache for better performance
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50MB cache
        
        # Set up URL interceptor to handle useskin=vector-2022 before navigation
        self.url_interceptor = WikipediaUrlInterceptor()
        profile.setUrlRequestInterceptor(self.url_interceptor)
        
        # Use default profile but clear its state aggressively
        print(f"🔧 WikiRace: [{time.time():.3f}] Using default profile but will clear all theme state")
        
        # Hide the webview initially to prevent flash of light content
        self.webView.setVisible(False)
        
        # Set initial background to prevent any flash
        styles = theme_manager.get_theme_styles()
        self.webView.setStyleSheet(f"background-color: {styles['background_color']};")
        
        # Connect signals before loading
        self.webView.page().loadStarted.connect(self.onLoadStarted)
        self.webView.page().loadFinished.connect(self.onPageLoaded)
        self.webView.urlChanged.connect(self.onUrlChanged)
        
        # Navigation counting is now handled in onUrlChanged method instead of navigationRequested
        # This avoids conflicts with the URL interceptor which redirects navigation requests
        
        # AGGRESSIVE: Force clear and setup theme regardless of profile state
        current_theme = theme_manager.get_theme()
        print(f"🎨 WikiRace: [{time.time():.3f}] SoloGamePage AGGRESSIVE theme setup with theme: {current_theme}")
        print(f"🔍 WikiRace: [{time.time():.3f}] Theme manager current state: {theme_manager.get_theme()}")
        
        # STEP 1: Clear all existing theme state first
        print(f"🧹 WikiRace: [{time.time():.3f}] Step 1: Clearing all theme state...")
        WikipediaTheme._clearThemeState(self.webView)
        
        # STEP 2: Force setup theme from scratch
        print(f"🔧 WikiRace: [{time.time():.3f}] Step 2: Setting up {current_theme} theme from scratch...")
        WikipediaTheme._setupInitialTheme(self.webView, current_theme)
        WikipediaTheme._setupNavigationScripts(self.webView, current_theme)
        
        # VERIFICATION: Double-check theme was applied
        print(f"✅ WikiRace: [{time.time():.3f}] AGGRESSIVE theme setup completed with theme: {current_theme}")
        
        # Ensure Vector 2022 skin is used for theme support
        start_url_with_skin = WikipediaTheme.ensureVector2022Skin(self.start_url)
        end_url_with_skin = WikipediaTheme.ensureVector2022Skin(self.end_url)
        
        # Update the URLs to use Vector 2022 skin
        self.start_url = start_url_with_skin
        self.end_url = end_url_with_skin
        
        # Start loading the page
        self.webView.load(QUrl(self.start_url))
        
        # OPTIMIZED: No delay needed - theme is applied instantly at DocumentCreation
        self.webView.setVisible(True)
        
        self.mainContentLayout.addWidget(self.webView, 3)
        
        # Main content area container widget
        self.mainContentContainer = QWidget()
        self.mainContentContainer.setLayout(self.mainContentLayout)
        self.contentLayout.addWidget(self.mainContentContainer, 3)

        # Add the content container to the main layout
        self.layout.addWidget(self.contentContainer)

        

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Initialize the stopwatch and links counter
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStopwatch)
        self.timer.start(1000)  # Update every second
        
        # Create confetti widget (initially hidden)
        self.confetti_widget = ConfettiWidget(self)
        self.confetti_widget.hide()
        
        # CRITICAL: Connect to theme changes - DO NOT REMOVE
        # This connection is ESSENTIAL for theme switching functionality
        # Without this, solo game pages won't update when theme changes
        # REGRESSION PREVENTION: This MUST remain connected for theme switching to work
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def onLoadStarted(self):
        """Handle page load started - theme is already set via cookies"""
        self.page_load_start_time = time.time()
        current_theme = theme_manager.get_theme()
        print(f"🚀 WikiRace: [{self.page_load_start_time:.3f}] SoloGamePage - Page load started - Wikipedia {current_theme} theme should be active via mwclientpreferences cookie")
        print(f"🚀 WikiRace: [{self.page_load_start_time:.3f}] SoloGamePage - Loading URL: {self.webView.url().toString()}")
        
        # Theme should already be properly set up during initialization
        print(f"✅ WikiRace: [{time.time():.3f}] Page load started - {current_theme} theme already configured")

    def onPageLoaded(self, success):
        """Handle page load finished - verify theme was applied"""
        self.page_load_finish_time = time.time()
        
        if success:
            current_theme = theme_manager.get_theme()
            load_duration = (self.page_load_finish_time - self.page_load_start_time) * 1000 if self.page_load_start_time else 0
            print(f"✅ WikiRace: [{self.page_load_finish_time:.3f}] SoloGamePage - Page loaded successfully with Wikipedia {current_theme} theme (load time: {load_duration:.1f}ms)")
            print(f"✅ WikiRace: [{self.page_load_finish_time:.3f}] SoloGamePage - Final URL: {self.webView.url().toString()}")
            # Skip verification for performance - theme should be working via cookies
            print(f"✅ WikiRace: [{time.time():.3f}] SoloGamePage - Page loaded - {current_theme} theme should be active")
            
            # OPTIMIZED: Scroll to top after page load to fix CSS injection scroll issues
            # This runs asynchronously to not slow down page loading
            scroll_to_top_script = """
            try {
                // Scroll to top smoothly without affecting loading performance
                window.scrollTo({ top: 0, behavior: 'instant' });
            } catch (e) {
                // Fallback for older browsers
                try {
                    window.scrollTo(0, 0);
                } catch (fallback_error) {
                    // Silent fallback - don't block page loading
                }
            }
            """
            # Run scroll-to-top asynchronously after a minimal delay
            QTimer.singleShot(50, lambda: self.webView.page().runJavaScript(scroll_to_top_script))
            
            # PRODUCTION: Skip post-load DOM manipulation to prevent late reflows
            if DEBUG_THEME:
                # OPTIMIZED: Navigation elements should be hidden automatically by DocumentReady script
                # Only add fallback if DocumentReady script fails (minimal stutter)
                def check_and_inject_if_needed():
                    # Quick check if navigation is still visible, only inject if needed
                    check_script = """
                    (function() {
                        var header = document.querySelector('#mw-head, .vector-header');
                        return header && getComputedStyle(header).display !== 'none';
                    })();
                    """
                    def handle_check(visible):
                        if visible:
                            print(f"🔧 WikiRace: [{time.time():.3f}] Navigation still visible, applying fallback CSS...")
                            WikipediaTheme._injectNavigationCSS(self.webView)
                        else:
                            print(f"✅ WikiRace: [{time.time():.3f}] Navigation already hidden by DocumentReady script")
                    
                    self.webView.page().runJavaScript(check_script, handle_check)
                
                # Only check after a brief delay to avoid stutter
                QTimer.singleShot(300, check_and_inject_if_needed)
                
                # DEBUGGING: Verify what theme is actually active in the browser
                def verify_actual_theme():
                    verify_script = f"""
                    (function() {{
                        var actualTheme = 'unknown';
                        var cookie = document.cookie.match(/mwclientpreferences=([^;]+)/);
                        if (cookie) {{
                            actualTheme = cookie[1].includes('night') ? 'dark' : cookie[1].includes('day') ? 'light' : cookie[1];
                        }}
                        var bgColor = getComputedStyle(document.documentElement).backgroundColor;
                        var classes = document.documentElement.className;
                        
                        console.log('WikiRace: THEME VERIFICATION - Expected: {current_theme}, Cookie: ' + actualTheme + ', BG: ' + bgColor);
                        console.log('WikiRace: THEME VERIFICATION - Classes: ' + classes);
                        
                        return {{
                            expectedTheme: '{current_theme}',
                            cookieTheme: actualTheme,
                            backgroundColor: bgColor,
                            classes: classes,
                            matches: actualTheme === '{current_theme}'
                        }};
                    }})();
                    """
                    
                    def handle_verification(result):
                        if result:
                            expected = result.get('expectedTheme', 'unknown')
                            actual = result.get('cookieTheme', 'unknown')
                            matches = result.get('matches', False)
                            bg = result.get('backgroundColor', 'unknown')
                            
                            print(f"🔍 WikiRace: [{time.time():.3f}] THEME VERIFICATION - Expected: {expected}, Actual: {actual}, Matches: {matches}")
                            print(f"🔍 WikiRace: [{time.time():.3f}] THEME VERIFICATION - Background: {bg}")
                            
                            if not matches:
                                print(f"❌ WikiRace: [{time.time():.3f}] THEME MISMATCH DETECTED! Forcing correct theme...")
                                WikipediaTheme.forceTheme(self.webView, current_theme)
                    
                    self.webView.page().runJavaScript(verify_script, handle_verification)
                
                QTimer.singleShot(1000, verify_actual_theme)
            else:
                print(f"⚡ WikiRace: [{time.time():.3f}] PRODUCTION MODE - Skipping post-load DOM manipulation for optimal performance")
            
            self.darkModeApplied = True
        else:
            print("❌ WikiRace: Page load failed")

    def onUrlChanged(self, url):
        """Handle URL changes - URL interceptor handles useskin parameter automatically"""
        self.url_change_time = time.time()
        url_str = url.toString()
        print(f"🔄 WikiRace: [{self.url_change_time:.3f}] URL changed to: {url_str}")
        
        # OPTIMIZED: URL interceptor handles useskin=vector-2022 automatically
        # No need to reload - prevents redirect loops and double loading
        self.darkModeApplied = False  # Reset flag for new page
        
        # Count link navigation and add page titles (skip initial page load)
        if hasattr(self, '_initial_load_complete'):
            # Only count if this is not the initial page load
            if url_str != self.start_url and "wikipedia.org" in url_str:
                self.linksUsed += 1
                self.linksUsedLabel.setText("Links Used: " + str(self.linksUsed))
                print(f"🔗 WikiRace: [{time.time():.3f}] Link navigation detected - Links used: {self.linksUsed}")
                
                # OPTIMIZED: Use fast URL path parser to get page title
                titleString = self.getTitleFromUrlPath(url_str)
                
                # Add the title to previous links if it's not already there
                existing_titles = [self.previousLinksList.item(i).text() for i in range(self.previousLinksList.count())]
                if titleString not in existing_titles:
                    self.previousLinksList.addItem(titleString)
                    print(f"📄 WikiRace: [{time.time():.3f}] Added page title to list: {titleString}")
                    
                    # Optionally get exact title after page loads (non-blocking)
                    def update_exact_title(exact_title):
                        if exact_title and exact_title != titleString:
                            # Update the last item with exact title
                            last_item = self.previousLinksList.item(self.previousLinksList.count() - 1)
                            if last_item and last_item.text() == titleString:
                                last_item.setText(exact_title)
                                print(f"✏️ WikiRace: [{time.time():.3f}] Updated title from '{titleString}' to '{exact_title}'")
                    
                    # Get exact title after page loads (non-blocking)
                    QTimer.singleShot(1000, lambda: self.getExactTitleFromJavaScript(update_exact_title))
                
                # Check if we've reached the destination
                self.checkEndGame(url)
        else:
            # Mark that initial load is complete and add starting page to list
            self._initial_load_complete = True
            
            # Add starting page to the list (without incrementing counter)
            starting_title = self.getTitleFromUrlPath(url_str)
            self.previousLinksList.addItem(f"🏁 {starting_title}")
            print(f"🏁 WikiRace: [{time.time():.3f}] Added starting page to list: {starting_title}")
            
            # Get exact title for starting page (non-blocking)
            def update_starting_title(exact_title):
                if exact_title and exact_title != starting_title:
                    # Update the starting page item with exact title
                    first_item = self.previousLinksList.item(0)
                    if first_item and first_item.text() == f"🏁 {starting_title}":
                        first_item.setText(f"🏁 {exact_title}")
                        print(f"✏️ WikiRace: [{time.time():.3f}] Updated starting page title to: {exact_title}")
            
            QTimer.singleShot(1000, lambda: self.getExactTitleFromJavaScript(update_starting_title))
            print(f"🏁 WikiRace: [{time.time():.3f}] Initial page load complete - future navigations will be counted")
        
        # OPTIMIZED: Navigation hiding should be handled by DocumentReady script
        print(f"✅ WikiRace: [{time.time():.3f}] New page loading - DocumentReady script will handle navigation hiding")

    def showWebView(self):
        """Show the webview after theme has been applied"""
        self.webView.setVisible(True)
    
    def refreshWikipediaPage(self):
        """
        CRITICAL: Refresh Wikipedia page to apply new theme
        
        This method is ESSENTIAL for theme switching on existing pages.
        DO NOT REMOVE OR MODIFY without understanding the consequences:
        
        1. Re-runs setupThemeWithNavigation() with current theme
        2. Reloads the page to apply new theme scripts
        3. Without this, theme changes won't affect existing Wikipedia pages
        
        REGRESSION PREVENTION:
        - setupThemeWithNavigation() MUST be called before reload()
        - Page MUST be reloaded for theme scripts to take effect
        - Theme parameter MUST use theme_manager.get_theme() for current theme
        """
        if hasattr(self, 'webView') and self.webView:
            current_url = self.webView.url().toString()
            if current_url and "wikipedia.org" in current_url:
                current_theme = theme_manager.get_theme()
                print(f"🔄 WikiRace: SoloGamePage - Refreshing Wikipedia page to apply {current_theme} theme")
                print(f"🔍 WikiRace: SoloGamePage - Current URL: {current_url}")
                
                # CRITICAL: Re-setup theme with navigation hiding for new theme
                # DO NOT REMOVE: This cleans up old theme scripts and applies new ones
                print(f"🔧 WikiRace: SoloGamePage - Calling setupThemeWithNavigation with theme: {current_theme}")
                WikipediaTheme.setupThemeWithNavigation(self.webView, current_theme)
                
                # CRITICAL: Reload page to apply new theme scripts
                # DO NOT REMOVE: Theme scripts only take effect after page reload
                print(f"🔄 WikiRace: SoloGamePage - Reloading page to apply {current_theme} theme")
                self.webView.reload()
    
    def on_theme_changed(self, theme):
        """
        CRITICAL: Handle theme changes for existing SoloGamePage instances
        
        This method is ESSENTIAL for theme switching functionality.
        DO NOT REMOVE OR MODIFY without understanding the consequences:
        
        1. Updates webview background to prevent flash during theme switch
        2. Calls refreshWikipediaPage() to re-setup theme scripts
        3. Without this, switching themes will leave solo games in old theme
        
        REGRESSION PREVENTION:
        - This method MUST be connected to theme_manager.theme_changed signal
        - refreshWikipediaPage() MUST be called to update Wikipedia theme
        - WebView background MUST be updated to match new theme
        """
        print(f"🎨 WikiRace: SoloGamePage - Theme changed to: {theme}")
        print(f"🔍 WikiRace: SoloGamePage - Current theme manager state: {theme_manager.get_theme()}")
        
        # CRITICAL: Update webview background to prevent visual flash
        # DO NOT REMOVE: This prevents white/dark flash during theme transition
        styles = theme_manager.get_theme_styles()
        self.webView.setStyleSheet(f"background-color: {styles['background_color']};")
        print(f"🎨 WikiRace: SoloGamePage - Updated webview background to: {styles['background_color']}")
        
        # CRITICAL: Refresh Wikipedia page to apply new theme
        # DO NOT REMOVE: This re-applies theme scripts for the new theme
        print(f"🔄 WikiRace: SoloGamePage - About to refresh page for theme: {theme}")
        self.refreshWikipediaPage()

    # REMOVED: Old blocking network methods getTitleFromUrl and getTitleFromPageId
    # Replaced with fast getTitleFromUrlPath and optional getExactTitleFromJavaScript

    def updateStopwatch(self):
        self.startTime += 1
        self.stopwatchLabel.setText(self.formatTime(self.startTime))

    def formatTime(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # REMOVED: onNavigationRequested method - replaced with URL change tracking
    # The old method conflicted with URL interceptor redirects
    # Navigation counting is now handled in onUrlChanged method

    # Adjust the checkEndGame method in SoloGamePage to include the tabWidget and homePageIndex
    def checkEndGame(self, newUrl):
        from PyQt6.QtCore import QTimer  # Import QTimer at the top of the method
        
        currentPage = self.getTitleFromUrlPath(newUrl.toString())
        
        # Use stored destination title if available, otherwise parse from URL
        if self.end_title:
            destinationPage = self.end_title
        else:
            destinationPage = self.getTitleFromUrlPath(self.end_url)
        
        print(f"🎯 WikiRace: [{time.time():.3f}] Checking end game - Current: '{currentPage}' vs Destination: '{destinationPage}'")
        print(f"🔍 WikiRace: [{time.time():.3f}] URL comparison - Current URL: '{newUrl.toString()}' vs Destination URL: '{self.end_url}'")
        print(f"🔍 WikiRace: [{time.time():.3f}] Title comparison (lower): '{currentPage.lower().strip()}' == '{destinationPage.lower().strip()}' ? {currentPage.lower().strip() == destinationPage.lower().strip()}")
        
        # Check for exact match (case-insensitive to handle minor differences)
        if currentPage.lower().strip() == destinationPage.lower().strip():
            print(f"🏆 WikiRace: [{time.time():.3f}] GAME COMPLETED! Player reached destination page!")
            
            # Stop the timer immediately
            self.timer.stop()
            
            # Wait for page to load, then show confetti, then dialog
            QTimer.singleShot(500, self.showConfettiAndDialog)  # Wait 500ms for page load
        else:
            print(f"🎯 WikiRace: [{time.time():.3f}] Game continues - pages don't match")
            
            # Also try getting exact current page title via JavaScript for more accuracy
            def check_with_exact_title(exact_current_title):
                if exact_current_title:
                    # Normalize both titles for comparison
                    exact_current_normalized = exact_current_title.lower().strip().replace('_', ' ')
                    destination_normalized = destinationPage.lower().strip().replace('_', ' ')
                    
                    print(f"🔍 WikiRace: [{time.time():.3f}] Exact title comparison: '{exact_current_normalized}' == '{destination_normalized}' ? {exact_current_normalized == destination_normalized}")
                    
                    if exact_current_normalized == destination_normalized:
                        print(f"🏆 WikiRace: [{time.time():.3f}] GAME COMPLETED! (via exact title check) Player reached destination page!")
                        self.timer.stop()
                        QTimer.singleShot(500, self.showConfettiAndDialog)
            
            # Get exact title for more accurate comparison
            QTimer.singleShot(200, lambda: self.getExactTitleFromJavaScript(check_with_exact_title))
    
    def showConfettiAndDialog(self):
        """Show confetti first, then dialog after confetti finishes"""
        # Show confetti on the current game page
        self.triggerConfetti()
        
        # After confetti finishes (4 seconds), show the dialog
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(4000, self.showEndGameDialog)
    
    def triggerConfetti(self):
        """Trigger confetti effect on the game page"""
        # Position confetti widget to cover the entire game page
        self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
        self.confetti_widget.raise_()  # Bring to front
        self.confetti_widget.startConfetti(4000)  # 4 second QUICK confetti effect
    
    def resizeEvent(self, event):
        """Handle resize events to reposition confetti widget"""
        super().resizeEvent(event)
        if hasattr(self, 'confetti_widget'):
            self.confetti_widget.setGeometry(0, 0, self.width(), self.height())
    
    def showEndGameDialog(self):
        """Show the end game dialog"""
        homePageIndex = 0  # HomePage is typically at index 0
        dialog = EndGameDialog(self, self.tabWidget, homePageIndex)
        dialog.exec()


class EndGameDialog(QDialog):
    def __init__(self, gamePage, tabWidget, homePageIndex, parent=None):
        super(EndGameDialog, self).__init__(parent)
        self.gamePage = gamePage
        self.tabWidget = tabWidget
        self.homePageIndex = homePageIndex
        self.setWindowTitle("Game Over")
        self.setWindowIcon(QIcon('C:/Project_Workspace/WikiRace/src/resources/icons/game_icon.ico'))
        # self.setWindowIcon(QIcon(self.projectPath + 'resources/icons/game_icon.ico'))
        self.apply_theme()
        self.setFixedSize(400, 280)  # Further increased size to prevent text cutoff
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
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding to prevent text cutoff
        layout.setSpacing(10)  # Add spacing between elements

        # Get theme styles for dynamic coloring
        styles = theme_manager.get_theme_styles()
        
        messageLabel = QLabel("Congratulations!")
        messageLabel.setStyleSheet(f"""
            font-size: 24px; 
            color: {styles['accent_color']}; 
            padding: 10px;
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            font-weight: bold;
            background-color: transparent;
        """)
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(messageLabel)
        
        messageSubscript = QLabel("You finished the race!")
        messageSubscript.setAlignment(Qt.AlignmentFlag.AlignCenter)
        messageSubscript.setStyleSheet(f"""
            font-size: 14px; 
            padding: 6px;
            color: {styles['text_secondary']};
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            background-color: transparent;
        """) 
        layout.addWidget(messageSubscript)

        totalTimeLabel = QLabel("Total time (hh:mm:ss): " + self.gamePage.formatTime(self.gamePage.startTime))
        totalTimeLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        totalTimeLabel.setStyleSheet(f"""
            color: {styles['text_color']}; 
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            background-color: transparent;
        """)
        layout.addWidget(totalTimeLabel)

        totalLinksLabel = QLabel("Total Links: " + str(self.gamePage.linksUsed))
        totalLinksLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        totalLinksLabel.setStyleSheet(f"""
            color: {styles['text_color']}; 
            font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
            background-color: transparent;
        """)
        layout.addWidget(totalLinksLabel)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.returnToHomePage)
        layout.addWidget(closeButton)

    def returnToHomePage(self):
        self.tabWidget.setCurrentIndex(self.homePageIndex)
        self.close()

