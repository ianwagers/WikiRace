"""
Wikipedia Dark Theme Implementation
Implements the "Wikipedia way" of dark theme using mwclientpreferences cookie
"""

from PyQt6.QtCore import QDateTime, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtNetwork import QNetworkCookie


class WikipediaDarkTheme:
    """
    Handles Wikipedia dark theme implementation using the official mwclientpreferences cookie
    This prevents the white flash (FOUC) by setting the cookie before navigation
    """
    
    @staticmethod
    def setupDarkTheme(webView: QWebEngineView):
        """
        Set up Wikipedia dark theme for a QWebEngineView
        This should be called before any Wikipedia navigation
        """
        print("🔧 WikiRace: Setting up Wikipedia dark theme...")
        
        if not webView:
            print("❌ WikiRace: WebView is None, cannot setup dark theme")
            return
            
        try:
            # Get the profile and cookie store
            profile = webView.page().profile()
            store = profile.cookieStore()
            print(f"✅ WikiRace: Got WebEngine profile and cookie store")
            
            # Set the mwclientpreferences cookie for dark theme
            # Format: skin-theme-clientpref-night (dark mode)
            cookie_val = b"skin-theme-clientpref-night"
            cookie = QNetworkCookie(b"mwclientpreferences", cookie_val)
            cookie.setDomain(".wikipedia.org")
            cookie.setPath("/")
            cookie.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
            
            print(f"🍪 WikiRace: Created cookie - Name: mwclientpreferences, Value: {cookie_val.decode()}")
            print(f"🍪 WikiRace: Cookie domain: {cookie.domain()}, path: {cookie.path()}")
            
            # Set SameSite policy if supported
            try:
                cookie.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
                print("🍪 WikiRace: Set SameSite=Lax policy")
            except Exception as e:
                print(f"⚠️ WikiRace: Could not set SameSite policy: {e}")
            
            # Set the cookie for all Wikipedia domains
            domains = [
                "https://en.wikipedia.org/",
                "https://de.wikipedia.org/",
                "https://fr.wikipedia.org/",
                "https://es.wikipedia.org/",
                "https://it.wikipedia.org/",
                "https://pt.wikipedia.org/",
                "https://ru.wikipedia.org/",
                "https://ja.wikipedia.org/",
                "https://zh.wikipedia.org/",
                "https://ar.wikipedia.org/"
            ]
        
            print(f"🌐 WikiRace: Setting cookies for {len(domains)} Wikipedia domains...")
            for domain in domains:
                store.setCookie(cookie, QUrl(domain))
                print(f"🍪 WikiRace: Set cookie for {domain}")
            
            # Also try setting the cookie with a more specific path and domain
            print("🍪 WikiRace: Setting additional cookies with specific paths...")
            for domain in domains:
                # Try with root domain
                cookie_root = QNetworkCookie(b"mwclientpreferences", cookie_val)
                cookie_root.setDomain(domain.replace("https://", "").replace("/", ""))
                cookie_root.setPath("/")
                cookie_root.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
                try:
                    cookie_root.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
                except Exception:
                    pass
                store.setCookie(cookie_root, QUrl(domain))
                print(f"🍪 WikiRace: Set root domain cookie for {domain}")
                
                # Try with www subdomain
                www_domain = domain.replace("://", "://www.")
                cookie_www = QNetworkCookie(b"mwclientpreferences", cookie_val)
                cookie_www.setDomain(domain.replace("https://", "").replace("/", ""))
                cookie_www.setPath("/")
                cookie_www.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
                try:
                    cookie_www.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
                except Exception:
                    pass
                store.setCookie(cookie_www, QUrl(www_domain))
                print(f"🍪 WikiRace: Set www domain cookie for {www_domain}")
            
            # Add document-creation micro-fallback to prevent any residual flash
            print("📜 WikiRace: Adding document creation fallback script...")
            WikipediaDarkTheme._addDocumentCreationScript(profile)
            
            # Configure WebEngine settings for optimal dark mode
            print("⚙️ WikiRace: Configuring WebEngine settings...")
            settings = webView.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            print("✅ WikiRace: WebEngine settings configured")
            
            # Set user agent to indicate dark mode support
            user_agent = "WikiRace/1.0 (Dark Mode Optimized)"
            profile.setHttpUserAgent(user_agent)
            print(f"🌐 WikiRace: Set user agent: {user_agent}")
            
            print("✅ WikiRace: Wikipedia dark theme setup completed successfully")
            
        except Exception as e:
            print(f"❌ WikiRace: Error setting up dark theme: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def setMultiplePreferences(webView: QWebEngineView, preferences: list):
        """
        Set multiple Wikipedia client preferences
        Example: setMultiplePreferences(webView, ['skin-theme-clientpref-night', 'limited-width-clientpref-1'])
        """
        if not webView or not preferences:
            return
            
        profile = webView.page().profile()
        store = profile.cookieStore()
        
        # Join multiple preferences with commas
        cookie_val = b",".join([pref.encode('utf-8') for pref in preferences])
        cookie = QNetworkCookie(b"mwclientpreferences", cookie_val)
        cookie.setDomain(".wikipedia.org")
        cookie.setPath("/")
        cookie.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
        
        try:
            cookie.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
        except Exception:
            pass
        
        # Set the cookie for all Wikipedia domains
        store.setCookie(cookie, QUrl("https://en.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://de.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://fr.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://es.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://it.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://pt.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ru.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ja.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://zh.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ar.wikipedia.org/"))
        
        # Add document-creation micro-fallback to prevent any residual flash
        WikipediaDarkTheme._addDocumentCreationScript(profile)
        
        # Configure WebEngine settings for optimal dark mode
        settings = webView.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        # Set user agent to indicate dark mode support
        profile.setHttpUserAgent("WikiRace/1.0 (Dark Mode Optimized)")
    
    @staticmethod
    def _addDocumentCreationScript(profile: QWebEngineProfile):
        """
        Add a document-creation script to prevent any residual flash
        This runs before the page paints and sets a dark backdrop instantly
        """
        print("📜 WikiRace: Creating document creation fallback script...")
        
        script = QWebEngineScript()
        script.setName("prepaint-dark-fallback")
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
        script.setRunsOnSubFrames(True)
        script.setSourceCode("""
        try {
            console.log('WikiRace: Document creation script executing...');
            
            // Set the mwclientpreferences cookie immediately via JavaScript
            document.cookie = 'mwclientpreferences=skin-theme-clientpref-night; domain=.wikipedia.org; path=/; max-age=157680000; SameSite=Lax';
            console.log('WikiRace: Set mwclientpreferences cookie via JavaScript');
            
            // Hint to UA and provide a dark background before styles land.
            var m = document.createElement('meta');
            m.name = 'color-scheme'; 
            m.content = 'dark';
            if (document.head) {
                document.head.appendChild(m);
            }
            document.documentElement.style.backgroundColor = '#101418';
            document.documentElement.style.color = '#ffffff';
            
            // Force dark theme classes immediately
            document.documentElement.classList.add('skin-theme-clientpref-night');
            document.documentElement.classList.remove('skin-theme-clientpref-day');
            
            console.log('WikiRace: Document creation script completed - dark background and classes set');
        } catch (e) {
            console.log('WikiRace: Document creation script error:', e);
        }
        """)
        
        try:
            profile.scripts().insert(script)
            print("✅ WikiRace: Document creation script added successfully")
        except Exception as e:
            print(f"❌ WikiRace: Error adding document creation script: {e}")
    
    @staticmethod
    def ensureVector2022Skin(url: str) -> str:
        """
        Ensure Wikipedia URLs use the Vector 2022 skin for dark mode support
        Appends ?useskin=vector-2022 or merges with existing query params
        """
        print(f"🔗 WikiRace: Ensuring Vector 2022 skin for URL: {url}")
        
        if not url or "wikipedia.org" not in url:
            print(f"⚠️ WikiRace: URL is not a Wikipedia URL, skipping skin modification")
            return url
            
        original_url = url
        
        # Parse URL to check for existing query parameters
        if "?" in url:
            # URL already has query parameters, check if useskin is already set
            if "useskin=" in url:
                # Replace existing useskin parameter
                import re
                url = re.sub(r'useskin=[^&]*', 'useskin=vector-2022', url)
                print(f"🔄 WikiRace: Replaced existing useskin parameter")
            else:
                # Add useskin parameter
                url += "&useskin=vector-2022"
                print(f"➕ WikiRace: Added useskin parameter to existing query string")
        else:
            # No query parameters, add useskin
            url += "?useskin=vector-2022"
            print(f"➕ WikiRace: Added useskin parameter as new query string")
            
        if url != original_url:
            print(f"✅ WikiRace: URL updated from {original_url} to {url}")
        else:
            print(f"ℹ️ WikiRace: URL unchanged (already has correct skin)")
            
        return url
    
    @staticmethod
    def verifyDarkModeApplied(webView: QWebEngineView, callback=None):
        """
        Verify that dark mode was properly applied by checking for the dark theme class
        This is for debugging purposes
        """
        print("🔍 WikiRace: Verifying dark mode application...")
        
        if not webView:
            print("❌ WikiRace: WebView is None, cannot verify dark mode")
            return
            
        verification_js = """
        (function() {
            try {
                console.log('WikiRace: Starting dark mode verification...');
                
                var className = document.documentElement.className;
                var hasDarkClass = className.includes('skin-theme-clientpref-night') || 
                                 className.includes('vector-theme-dark');
                var bodyBg = window.getComputedStyle(document.body).backgroundColor;
                var isDark = bodyBg.includes('rgb(27, 20, 32)') || bodyBg.includes('#101418') || 
                           bodyBg.includes('rgb(30, 30, 30)') || bodyBg.includes('#1e1e1e');
                
                // Check for mwclientpreferences cookie
                var cookies = document.cookie;
                var hasMwCookie = cookies.includes('mwclientpreferences');
                var mwCookieValue = '';
                if (hasMwCookie) {
                    var match = cookies.match(/mwclientpreferences=([^;]+)/);
                    if (match) {
                        mwCookieValue = match[1];
                    }
                }
                
                // Check for meta color-scheme
                var metaColorScheme = document.querySelector('meta[name="color-scheme"]');
                var colorSchemeValue = metaColorScheme ? metaColorScheme.content : 'not found';
                
                console.log('WikiRace: Dark mode verification results:');
                console.log('  - HTML classes:', className);
                console.log('  - Has dark class:', hasDarkClass);
                console.log('  - Body background:', bodyBg);
                console.log('  - Is dark background:', isDark);
                console.log('  - Has mwclientpreferences cookie:', hasMwCookie);
                console.log('  - Cookie value:', mwCookieValue);
                console.log('  - Meta color-scheme:', colorSchemeValue);
                
                return {
                    hasDarkClass: hasDarkClass,
                    isDarkBackground: isDark,
                    className: className,
                    bodyBackground: bodyBg,
                    hasMwCookie: hasMwCookie,
                    mwCookieValue: mwCookieValue,
                    colorSchemeValue: colorSchemeValue
                };
            } catch (e) {
                console.log('WikiRace: Dark mode verification error:', e);
                return { error: e.toString() };
            }
        })();
        """
        
        def handleResult(result):
            print("🔍 WikiRace: Dark mode verification completed")
            if result and 'error' not in result:
                print(f"✅ WikiRace: Dark mode verification results:")
                print(f"  - Has dark class: {result.get('hasDarkClass', False)}")
                print(f"  - Is dark background: {result.get('isDarkBackground', False)}")
                print(f"  - HTML classes: {result.get('className', 'N/A')}")
                print(f"  - Body background: {result.get('bodyBackground', 'N/A')}")
                print(f"  - Has mwclientpreferences cookie: {result.get('hasMwCookie', False)}")
                print(f"  - Cookie value: {result.get('mwCookieValue', 'N/A')}")
                print(f"  - Meta color-scheme: {result.get('colorSchemeValue', 'N/A')}")
            else:
                print(f"❌ WikiRace: Dark mode verification failed: {result}")
            
            if callback:
                callback(result)
        
        try:
            webView.page().runJavaScript(verification_js, handleResult)
        except Exception as e:
            print(f"❌ WikiRace: Error running verification JavaScript: {e}")
    
    @staticmethod
    def checkCookiesInBrowser(webView: QWebEngineView):
        """
        Check what cookies are actually stored in the browser
        This helps debug if cookies are being set correctly
        """
        print("🍪 WikiRace: Checking cookies in browser...")
        
        if not webView:
            print("❌ WikiRace: WebView is None, cannot check cookies")
            return
            
        cookie_check_js = """
        (function() {
            try {
                var cookies = document.cookie;
                console.log('WikiRace: All cookies:', cookies);
                
                var mwCookie = null;
                if (cookies.includes('mwclientpreferences')) {
                    var match = cookies.match(/mwclientpreferences=([^;]+)/);
                    if (match) {
                        mwCookie = match[1];
                    }
                }
                
                return {
                    allCookies: cookies,
                    mwclientpreferences: mwCookie,
                    hasMwCookie: mwCookie !== null
                };
            } catch (e) {
                console.log('WikiRace: Cookie check error:', e);
                return { error: e.toString() };
            }
        })();
        """
        
        def handleCookieResult(result):
            print("🍪 WikiRace: Cookie check completed")
            if result and 'error' not in result:
                print(f"🍪 WikiRace: All cookies: {result.get('allCookies', 'N/A')}")
                print(f"🍪 WikiRace: mwclientpreferences cookie: {result.get('mwclientpreferences', 'N/A')}")
                print(f"🍪 WikiRace: Has mwclientpreferences: {result.get('hasMwCookie', False)}")
            else:
                print(f"❌ WikiRace: Cookie check failed: {result}")
        
        try:
            webView.page().runJavaScript(cookie_check_js, handleCookieResult)
        except Exception as e:
            print(f"❌ WikiRace: Error checking cookies: {e}")
    
    @staticmethod
    def forceDarkTheme(webView: QWebEngineView):
        """
        Force dark theme using JavaScript if the cookie approach doesn't work
        This is a fallback method that directly manipulates the DOM
        """
        print("🔧 WikiRace: Forcing dark theme via JavaScript...")
        
        if not webView:
            print("❌ WikiRace: WebView is None, cannot force dark theme")
            return
            
        force_dark_js = """
        (function() {
            try {
                console.log('WikiRace: Forcing dark theme via JavaScript...');
                
                // Set the cookie again via JavaScript
                document.cookie = 'mwclientpreferences=skin-theme-clientpref-night; domain=.wikipedia.org; path=/; max-age=157680000; SameSite=Lax';
                console.log('WikiRace: Re-set mwclientpreferences cookie via JavaScript');
                
                // Force remove day theme class and add night theme class
                document.documentElement.classList.remove('skin-theme-clientpref-day');
                document.documentElement.classList.add('skin-theme-clientpref-night');
                
                // Also try the vector theme classes
                document.documentElement.classList.remove('vector-theme-light');
                document.documentElement.classList.add('vector-theme-dark');
                
                // Set meta color-scheme
                var metaTheme = document.querySelector('meta[name="color-scheme"]');
                if (metaTheme) {
                    metaTheme.setAttribute('content', 'dark');
                } else {
                    var meta = document.createElement('meta');
                    meta.name = 'color-scheme';
                    meta.content = 'dark';
                    if (document.head) {
                        document.head.appendChild(meta);
                    }
                }
                
                // Force dark background
                document.documentElement.style.backgroundColor = '#101418';
                document.documentElement.style.color = '#ffffff';
                document.body.style.backgroundColor = '#101418';
                document.body.style.color = '#ffffff';
                
                // Try to trigger Wikipedia's theme system
                if (typeof mw !== 'undefined' && mw.user && mw.user.clientPrefs) {
                    try {
                        mw.user.clientPrefs.set('skin-theme', 'night');
                        console.log('WikiRace: Set Wikipedia client preference via mw.user.clientPrefs');
                    } catch (e) {
                        console.log('WikiRace: Could not set mw.user.clientPrefs:', e);
                    }
                }
                
                console.log('WikiRace: Dark theme forced successfully');
                return {
                    success: true,
                    classes: document.documentElement.className,
                    cookie: document.cookie
                };
            } catch (e) {
                console.log('WikiRace: Error forcing dark theme:', e);
                return { error: e.toString() };
            }
        })();
        """
        
        def handleForceResult(result):
            print("🔧 WikiRace: Force dark theme completed")
            if result and 'error' not in result:
                print(f"✅ WikiRace: Dark theme forced successfully")
                print(f"✅ WikiRace: HTML classes: {result.get('classes', 'N/A')}")
                print(f"✅ WikiRace: Cookies: {result.get('cookie', 'N/A')}")
            else:
                print(f"❌ WikiRace: Force dark theme failed: {result}")
        
        try:
            webView.page().runJavaScript(force_dark_js, handleForceResult)
        except Exception as e:
            print(f"❌ WikiRace: Error forcing dark theme: {e}")
    
    @staticmethod
    def setAutoTheme(webView: QWebEngineView):
        """
        Set the theme to follow OS preference (auto mode)
        This sets skin-theme~os instead of skin-theme~night
        """
        if not webView:
            return
            
        profile = webView.page().profile()
        store = profile.cookieStore()
        
        # Set the mwclientpreferences cookie for auto theme
        cookie_val = b"skin-theme-clientpref-os"
        cookie = QNetworkCookie(b"mwclientpreferences", cookie_val)
        cookie.setDomain(".wikipedia.org")
        cookie.setPath("/")
        cookie.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
        
        try:
            cookie.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
        except Exception:
            pass
        
        # Set the cookie for all Wikipedia domains
        store.setCookie(cookie, QUrl("https://en.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://de.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://fr.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://es.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://it.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://pt.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ru.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ja.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://zh.wikipedia.org/"))
        store.setCookie(cookie, QUrl("https://ar.wikipedia.org/"))
    
    @staticmethod
    def hideNavigationElements(webView: QWebEngineView):
        """
        Hide Wikipedia header, footer, and navigation elements to show only main content
        This injects CSS to hide various Wikipedia UI elements
        """
        print("🔧 WikiRace: Hiding Wikipedia navigation elements...")
        
        if not webView:
            print("❌ WikiRace: WebView is None, cannot hide navigation elements")
            return
            
        hide_elements_js = """
        (function() {
            try {
                console.log('WikiRace: Hiding Wikipedia navigation elements...');
                
                // Debug: Log page structure
                console.log('WikiRace: Debugging page structure...');
                console.log('WikiRace: All h1 elements:', document.querySelectorAll('h1'));
                console.log('WikiRace: All h2 elements:', document.querySelectorAll('h2'));
                console.log('WikiRace: Page title element:', document.querySelector('h1.firstHeading, h1#firstHeading, h1.mw-page-title, .mw-page-title, h1, .vector-page-title, .mw-body h1, #content h1, .vector-body h1'));
                
                // Create and inject CSS to hide Wikipedia navigation elements
                var style = document.createElement('style');
                style.id = 'wikirace-hide-navigation';
                style.textContent = `
                    /* Hide main header and navigation */
                    #mw-head,
                    .vector-header,
                    .vector-header-container,
                    #mw-navigation,
                    #mw-panel,
                    .vector-menu-tabs,
                    .vector-menu-dropdown,
                    .vector-user-menu,
                    .vector-search-box,
                    #p-logo,
                    #left-navigation,
                    #right-navigation,
                    .vector-main-menu,
                    .vector-page-tools,
                    .vector-toc,
                    
                    /* Hide footer */
                    #footer,
                    .vector-footer,
                    .mw-footer,
                    #mw-footer,
                    
                    /* Hide sidebar elements */
                    #mw-panel,
                    .vector-sidebar,
                    .vector-main-menu-container,
                    
                    /* Hide edit links and tools */
                    .mw-editsection,
                    .vector-view-edit,
                    .vector-view-history,
                    .vector-view-view,
                    .vector-more-collapsible,
                    
                    /* Hide language switcher */
                    .vector-page-toolbar,
                    .vector-page-toolbar-container,
                    
                    /* Hide talk page tabs */
                    #ca-talk,
                    #ca-edit,
                    #ca-ve-edit,
                    #ca-history,
                    #ca-watch,
                    #ca-unwatch,
                    
                    /* Hide notification area */
                    .mw-notification-area,
                    
                    /* Hide categories at bottom */
                    #catlinks,
                    
                    /* Hide "From Wikipedia" notice */
                    .dablink,
                    .hatnote,
                    
                    /* Hide article footer sections */
                    #See_also,
                    #Notes,
                    #References,
                    #Citations,
                    #Bibliography,
                    #Works_cited,
                    #Further_reading,
                    #External_links,
                    #Primary_sources,
                    #Sources,
                    #Footnotes,
                    #Navigation_boxes,
                    #Categories,
                    #Interlanguage_links,
                    
                    /* Hide external link icons */
                    .external:after {
                        display: none !important;
                        visibility: hidden !important;
                    }
                    
                    /* Adjust main content area */
                    #content,
                    .vector-body,
                    .mw-body,
                    #mw-content-text {
                        margin-left: 0 !important;
                        margin-right: 0 !important;
                        padding-left: 20px !important;
                        padding-right: 20px !important;
                    }
                    
                    /* Make content full width */
                    .vector-body {
                        max-width: none !important;
                        width: 100% !important;
                    }
                    
                    /* Hide Wikipedia logo and title */
                    .vector-header-start,
                    .vector-logo {
                        display: none !important;
                    }
                    
                    /* Preserve article title (h1) - multiple selectors for different Wikipedia layouts */
                    h1.firstHeading,
                    h1#firstHeading,
                    h1.mw-page-title,
                    .mw-page-title,
                    h1,
                    .vector-page-title,
                    .mw-body h1,
                    #content h1,
                    .vector-body h1,
                    .mw-body-content h1,
                    #mw-content-text h1 {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        color: inherit !important;
                        font-size: 1.7em !important;
                        font-weight: bold !important;
                        margin: 0.67em 0 !important;
                        padding: 0 !important;
                        text-decoration: none !important;
                        line-height: 1.2 !important;
                    }
                    
                    /* Override any conflicting styles that might hide the title */
                    .vector-header-start h1,
                    .vector-header h1,
                    .mw-head h1,
                    .vector-page-titlebar h1,
                    .vector-page-titlebar .mw-page-title,
                    .vector-page-titlebar .firstHeading {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                    }
                    
                    /* Ensure titlebar content is visible but hide the titlebar container styling */
                    .vector-page-titlebar {
                        background: transparent !important;
                        border: none !important;
                        padding: 0 !important;
                        margin: 0 !important;
                    }
                    
                    .vector-page-titlebar h1,
                    .vector-page-titlebar .mw-page-title,
                    .vector-page-titlebar .firstHeading {
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        color: inherit !important;
                        font-size: 2.5em !important;
                        font-weight: bold !important;
                        margin: 0.67em 0 !important;
                        padding: 0 !important;
                        line-height: 1.2 !important;
                    }
                `;
                
                // Remove existing style if it exists
                var existingStyle = document.getElementById('wikirace-hide-navigation');
                if (existingStyle) {
                    existingStyle.remove();
                }
                
                // Add the new style - check if document.head exists
                if (document.head) {
                    document.head.appendChild(style);
                } else {
                    console.log('WikiRace: document.head is null, cannot append style');
                }
                
                // Hide footer sections by heading text - stop at first footer found
                var footerSections = [
                    'See also', 'Notes', 'References', 'Citations', 'Bibliography', 
                    'Works cited', 'Further reading', 'External links', 'Primary sources',
                    'Sources', 'Footnotes', 'Navigation boxes', 'Categories', 'Interlanguage links'
                ];
                
                // Find the first footer section and remove everything from that point
                var firstFooterFound = false;
                var headings = document.querySelectorAll('h2');
                
                for (var i = 0; i < headings.length && !firstFooterFound; i++) {
                    var heading = headings[i];
                    var headingText = heading.textContent.trim();
                    
                    if (footerSections.indexOf(headingText) !== -1) {
                        firstFooterFound = true;
                        
                        console.log('WikiRace: Found first footer section: ' + headingText);
                        
                        // Hide the footer heading
                        heading.style.display = 'none';
                        
                        // Find the parent container (usually #content or .mw-body)
                        var contentContainer = document.querySelector('#content, .mw-body, .vector-body, #mw-content-text');
                        if (!contentContainer) {
                            contentContainer = heading.closest('div');
                        }
                        
                        if (contentContainer) {
                            // Get all elements after the footer heading
                            var allElements = Array.from(contentContainer.querySelectorAll('*'));
                            var footerIndex = allElements.indexOf(heading);
                            
                            if (footerIndex !== -1) {
                                // Hide all elements after the footer heading
                                for (var j = footerIndex + 1; j < allElements.length; j++) {
                                    var element = allElements[j];
                                    if (element !== heading) {
                                        element.style.display = 'none';
                                        element.style.visibility = 'hidden';
                                    }
                                }
                                console.log('WikiRace: Hidden ' + (allElements.length - footerIndex - 1) + ' elements after footer');
                            }
                        }
                        
                        break;
                    }
                }
                
                // Ensure article title is visible - try multiple approaches
                var titleSelectors = [
                    'h1.firstHeading',
                    'h1#firstHeading', 
                    'h1.mw-page-title',
                    '.mw-page-title',
                    'h1',
                    '.vector-page-title',
                    '.mw-body h1',
                    '#content h1',
                    '.vector-body h1',
                    '.mw-body-content h1',
                    '#mw-content-text h1',
                    '.vector-page-titlebar h1',
                    '.vector-page-titlebar .mw-page-title',
                    '.vector-page-titlebar .firstHeading'
                ];
                
                var articleTitle = null;
                for (var k = 0; k < titleSelectors.length; k++) {
                    articleTitle = document.querySelector(titleSelectors[k]);
                    if (articleTitle && articleTitle.textContent.trim()) {
                        console.log('WikiRace: Found title with selector: ' + titleSelectors[k]);
                        break;
                    }
                }
                
                if (articleTitle) {
                    articleTitle.style.visibility = 'visible';
                    articleTitle.style.opacity = '1';
                    articleTitle.style.color = 'inherit';
                    articleTitle.style.fontSize = '2.5em';
                    articleTitle.style.fontWeight = 'bold';
                    articleTitle.style.lineHeight = '1.2';
                    articleTitle.style.margin = '0.67em 0';
                    articleTitle.style.padding = '0';
                    console.log('WikiRace: Article title made visible: ' + articleTitle.textContent.trim());
                } else {
                    console.log('WikiRace: No article title found with any selector');
                    
                    // Try to find title in titlebar specifically
                    var titlebar = document.querySelector('.vector-page-titlebar');
                    if (titlebar) {
                        console.log('WikiRace: Found titlebar, checking for title inside...');
                        var titleInTitlebar = titlebar.querySelector('h1, .mw-page-title, .firstHeading');
                        if (titleInTitlebar) {
                            titleInTitlebar.style.display = 'block';
                            titleInTitlebar.style.visibility = 'visible';
                            titleInTitlebar.style.opacity = '1';
                            titleInTitlebar.style.fontSize = '2.5em';
                            titleInTitlebar.style.fontWeight = 'bold';
                            titleInTitlebar.style.lineHeight = '1.2';
                            titleInTitlebar.style.margin = '0.67em 0';
                            titleInTitlebar.style.padding = '0';
                            console.log('WikiRace: Found title in titlebar: ' + titleInTitlebar.textContent.trim());
                        }
                    }
                    
                    // Debug: log all h1 elements
                    var allH1s = document.querySelectorAll('h1');
                    console.log('WikiRace: All h1 elements found:', allH1s);
                    for (var l = 0; l < allH1s.length; l++) {
                        console.log('WikiRace: H1 ' + l + ':', allH1s[l].textContent.trim(), allH1s[l].className, allH1s[l].id);
                    }
                }
                
                console.log('WikiRace: Navigation elements hidden successfully');
                return { success: true };
                
            } catch (e) {
                console.log('WikiRace: Error hiding navigation elements:', e);
                return { error: e.toString() };
            }
        })();
        """
        
        def handleHideResult(result):
            print("🔧 WikiRace: Hide navigation elements completed")
            if result and 'error' not in result:
                print("✅ WikiRace: Wikipedia navigation elements hidden successfully")
            else:
                print(f"❌ WikiRace: Failed to hide navigation elements: {result}")
        
        try:
            webView.page().runJavaScript(hide_elements_js, handleHideResult)
        except Exception as e:
            print(f"❌ WikiRace: Error running hide navigation JavaScript: {e}")