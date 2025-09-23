"""
Wikipedia Theme Implementation
Implements Wikipedia theme switching using mwclientpreferences cookie
Supports both dark and light themes
"""

import time
from PyQt6.QtCore import QDateTime, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtNetwork import QNetworkCookie


class WikipediaTheme:
    """
    Handles Wikipedia theme implementation using the official mwclientpreferences cookie
    This prevents the white flash (FOUC) by setting the cookie before navigation
    Supports both dark and light themes
    OPTIMIZED: Now includes instant CSS injection for sub-second performance
    """
    
    # Pre-compiled CSS for hiding navigation elements (optimized for performance)
    _HIDE_NAVIGATION_CSS = """
        /* Hide main header and navigation */
        #mw-head, .vector-header, .vector-header-container, #mw-navigation, #mw-panel,
        .vector-menu-tabs, .vector-menu-dropdown, .vector-user-menu, .vector-search-box,
        #p-logo, #left-navigation, #right-navigation, .vector-main-menu, .vector-page-tools,
        .vector-toc, #footer, .vector-footer, .mw-footer, #mw-footer, .vector-sidebar,
        .vector-main-menu-container, .mw-editsection, .vector-view-edit, .vector-view-history,
        .vector-view-view, .vector-more-collapsible, .vector-page-toolbar,
        .vector-page-toolbar-container, #ca-talk, #ca-edit, #ca-ve-edit, #ca-history,
        #ca-watch, #ca-unwatch, .mw-notification-area, #catlinks, .dablink, .hatnote,
        #See_also, #Notes, #References, #Citations, #Bibliography, #Works_cited,
        #Further_reading, #External_links, #Primary_sources, #Sources, #Footnotes,
        #Navigation_boxes, #Categories, #Interlanguage_links, .vector-header-start,
        .vector-logo { display: none !important; }
        
        /* Hide external link icons */
        .external:after { display: none !important; visibility: hidden !important; }
        
        /* Adjust main content area for full width */
        #content, .vector-body, .mw-body, #mw-content-text {
            margin-left: 0 !important; margin-right: 0 !important;
            padding-left: 20px !important; padding-right: 20px !important;
        }
        .vector-body { max-width: none !important; width: 100% !important; }
        
        /* Preserve and style article title - reduced font size for better balance */
        h1.firstHeading, h1#firstHeading, h1.mw-page-title, .mw-page-title, .vector-page-title,
        .mw-body h1:first-of-type, #content h1:first-of-type, .vector-body h1:first-of-type,
        .mw-body-content h1:first-of-type, #mw-content-text h1:first-of-type,
        .vector-page-titlebar h1, .vector-page-titlebar .mw-page-title,
        .vector-page-titlebar .firstHeading {
            display: block !important; visibility: visible !important; opacity: 1 !important;
            color: inherit !important; font-size: 1.4em !important; font-weight: bold !important;
            margin: 0.67em 0 !important; padding: 0 !important; line-height: 1.2 !important;
            text-decoration: none !important;
        }
        
        /* Clean up titlebar styling */
        .vector-page-titlebar {
            background: transparent !important; border: none !important;
            padding: 0 !important; margin: 0 !important;
        }
        
        /* Hide footer sections using efficient selectors */
        h2[id*="eference"] ~ *, h2[id*="ote"] ~ *, h2[id*="ee_also"] ~ *,
        h2[id*="xternal"] ~ *, h2[id*="itation"] ~ *, h2[id*="ibliography"] ~ * {
            display: none !important;
        }
    """
    
    # Pre-compiled CSS specifically for Wikipedia main page customization
    _MAIN_PAGE_CUSTOMIZATION_CSS = """
        /* Note: Main page customization is now handled via JavaScript in applyMainPageCustomization() */
        /* CSS :contains() selectors are not supported in Chromium/QWebEngine */
        /* All main page styling is done via JavaScript for better compatibility */
    """
    
    @staticmethod
    def setupTheme(webView: QWebEngineView, theme: str = 'dark'):
        """
        Set up Wikipedia theme for a QWebEngineView
        This should be called before any Wikipedia navigation
        """
        print(f"🔧 WikiRace: Setting up Wikipedia {theme} theme...")
        
        if not webView:
            print(f"❌ WikiRace: WebView is None, cannot setup {theme} theme")
            return
            
        try:
            # Get the profile and cookie store
            profile = webView.page().profile()
            store = profile.cookieStore()
            print(f"✅ WikiRace: Got WebEngine profile and cookie store")
            
            # Set the mwclientpreferences cookie for the specified theme
            if theme == 'light':
                cookie_val = b"skin-theme-clientpref-day"
            else:
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
            WikipediaTheme._addDocumentCreationScript(profile, theme)
            
            # Configure WebEngine settings for optimal theme support
            print("⚙️ WikiRace: Configuring WebEngine settings...")
            settings = webView.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            print("✅ WikiRace: WebEngine settings configured")
            
            # Set user agent to indicate theme support
            user_agent = f"WikiRace/1.0 ({theme.title()} Mode Optimized)"
            profile.setHttpUserAgent(user_agent)
            print(f"🌐 WikiRace: Set user agent: {user_agent}")
            
            print(f"✅ WikiRace: Wikipedia {theme} theme setup completed successfully")
            
        except Exception as e:
            print(f"❌ WikiRace: Error setting up {theme} theme: {e}")
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
        WikipediaTheme._addDocumentCreationScript(profile)
        
        # Configure WebEngine settings for optimal dark mode
        settings = webView.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        # Set user agent to indicate dark mode support
        profile.setHttpUserAgent("WikiRace/1.0 (Dark Mode Optimized)")
    
    @staticmethod
    def _addDocumentCreationScript(profile: QWebEngineProfile, theme: str = 'dark'):
        """
        Add a document-creation script to prevent any residual flash
        This runs before the page paints and sets the appropriate backdrop instantly
        """
        print(f"📜 WikiRace: Creating document creation fallback script for {theme} theme...")
        
        script = QWebEngineScript()
        script.setName(f"prepaint-{theme}-fallback")
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
        script.setRunsOnSubFrames(True)
        
        # Set theme-specific values
        if theme == 'light':
            cookie_value = 'skin-theme-clientpref-day'
            color_scheme = 'light'
            bg_color = '#FFFFFF'
            text_color = '#1A1A1A'
            theme_class = 'skin-theme-clientpref-day'
            remove_class = 'skin-theme-clientpref-night'
        else:
            cookie_value = 'skin-theme-clientpref-night'
            color_scheme = 'dark'
            bg_color = '#101418'
            text_color = '#ffffff'
            theme_class = 'skin-theme-clientpref-night'
            remove_class = 'skin-theme-clientpref-day'
        
        script.setSourceCode(f"""
        try {{
            console.log('WikiRace: Document creation script executing for {theme} theme...');
            
            // Set the mwclientpreferences cookie immediately via JavaScript
            document.cookie = 'mwclientpreferences={cookie_value}; domain=.wikipedia.org; path=/; max-age=157680000; SameSite=Lax';
            console.log('WikiRace: Set mwclientpreferences cookie via JavaScript');
            
            // Hint to UA and provide the appropriate background before styles land.
            var m = document.createElement('meta');
            m.name = 'color-scheme'; 
            m.content = '{color_scheme}';
            if (document.head) {{
                document.head.appendChild(m);
            }}
            document.documentElement.style.backgroundColor = '{bg_color}';
            document.documentElement.style.color = '{text_color}';
            
            // Force {theme} theme classes immediately
            document.documentElement.classList.add('{theme_class}');
            document.documentElement.classList.remove('{remove_class}');
            
            console.log('WikiRace: Document creation script completed - {theme} background and classes set');
        }} catch (e) {{
            console.log('WikiRace: Document creation script error:', e);
        }}
        """)
        
        try:
            profile.scripts().insert(script)
            print("✅ WikiRace: Document creation script added successfully")
        except Exception as e:
            print(f"❌ WikiRace: Error adding document creation script: {e}")
    
    @staticmethod
    def setupDarkTheme(webView: QWebEngineView):
        """
        Backward compatibility method for dark theme setup
        """
        return WikipediaTheme.setupTheme(webView, 'dark')
    
    @staticmethod
    def ensureVector2022Skin(url: str) -> str:
        """
        Ensure Wikipedia URLs use the Vector 2022 skin for dark mode support
        Also adds performance optimizations to the URL
        """
        print(f"🔗 WikiRace: Ensuring Vector 2022 skin for URL: {url}")
        
        if not url or "wikipedia.org" not in url:
            print(f"⚠️ WikiRace: URL is not a Wikipedia URL, skipping skin modification")
            return url
            
        original_url = url
        
        # Parse URL to check for existing query parameters
        if "?" in url:
            # URL already has query parameters
            if "useskin=" in url:
                # Replace existing useskin parameter
                import re
                url = re.sub(r'useskin=[^&]*', 'useskin=vector-2022', url)
                print(f"🔄 WikiRace: Replaced existing useskin parameter")
            else:
                # Add useskin parameter
                url += "&useskin=vector-2022"
                print(f"➕ WikiRace: Added useskin parameter to existing query string")
            
            # Could add performance parameters here if needed
        else:
            # No query parameters, add useskin only
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
                
                var className = document.documentElement ? document.documentElement.className : '';
                var hasDarkClass = className.includes('skin-theme-clientpref-night') || 
                                 className.includes('vector-theme-dark');
                var bodyBg = document.body ? window.getComputedStyle(document.body).backgroundColor : 'unknown';
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
    def forceTheme(webView: QWebEngineView, theme: str = 'dark'):
        """
        Force theme using JavaScript if the cookie approach doesn't work
        This is a fallback method that directly manipulates the DOM
        """
        print(f"🔧 WikiRace: Forcing {theme} theme via JavaScript...")
        
        if not webView:
            print(f"❌ WikiRace: WebView is None, cannot force {theme} theme")
            return
            
        # Set theme-specific values
        if theme == 'light':
            cookie_value = 'skin-theme-clientpref-day'
            color_scheme = 'light'
            bg_color = '#FFFFFF'
            text_color = '#1A1A1A'
            theme_class = 'skin-theme-clientpref-day'
            remove_class = 'skin-theme-clientpref-night'
            vector_theme = 'vector-theme-light'
            vector_remove = 'vector-theme-dark'
            mw_pref = 'day'
        else:
            cookie_value = 'skin-theme-clientpref-night'
            color_scheme = 'dark'
            bg_color = '#101418'
            text_color = '#ffffff'
            theme_class = 'skin-theme-clientpref-night'
            remove_class = 'skin-theme-clientpref-day'
            vector_theme = 'vector-theme-dark'
            vector_remove = 'vector-theme-light'
            mw_pref = 'night'
        
        force_theme_js = f"""
        (function() {{
            try {{
                console.log('WikiRace: Forcing {theme} theme via JavaScript...');
                
                // Set the cookie again via JavaScript
                document.cookie = 'mwclientpreferences={cookie_value}; domain=.wikipedia.org; path=/; max-age=157680000; SameSite=Lax';
                console.log('WikiRace: Re-set mwclientpreferences cookie via JavaScript');
                
                // Force remove opposite theme class and add current theme class
                if (document.documentElement && document.documentElement.classList) {{
                document.documentElement.classList.remove('{remove_class}');
                document.documentElement.classList.add('{theme_class}');
                
                // Also try the vector theme classes
                document.documentElement.classList.remove('{vector_remove}');
                document.documentElement.classList.add('{vector_theme}');
                }}
                
                // Set meta color-scheme
                var metaTheme = document.querySelector('meta[name="color-scheme"]');
                if (metaTheme) {{
                    metaTheme.setAttribute('content', '{color_scheme}');
                }} else {{
                    var meta = document.createElement('meta');
                    meta.name = 'color-scheme';
                    meta.content = '{color_scheme}';
                    if (document.head) {{
                        document.head.appendChild(meta);
                    }}
                }}
                
                // Force {theme} background
                document.documentElement.style.backgroundColor = '{bg_color}';
                document.documentElement.style.color = '{text_color}';
                document.body.style.backgroundColor = '{bg_color}';
                document.body.style.color = '{text_color}';
                
                // Try to trigger Wikipedia's theme system
                if (typeof mw !== 'undefined' && mw.user && mw.user.clientPrefs) {{
                    try {{
                        mw.user.clientPrefs.set('skin-theme', '{mw_pref}');
                        console.log('WikiRace: Set Wikipedia client preference via mw.user.clientPrefs');
                    }} catch (e) {{
                        console.log('WikiRace: Could not set mw.user.clientPrefs:', e);
                    }}
                }}
                
                console.log('WikiRace: {theme.title()} theme forced successfully');
                return {{
                    success: true,
                    classes: document.documentElement.className,
                    cookie: document.cookie
                }};
            }} catch (e) {{
                console.log('WikiRace: Error forcing {theme} theme:', e);
                return {{ error: e.toString() }};
            }}
        }})();
        """
        
        def handleForceResult(result):
            print(f"🔧 WikiRace: Force {theme} theme completed")
            if result and 'error' not in result:
                print(f"✅ WikiRace: {theme.title()} theme forced successfully")
                print(f"✅ WikiRace: HTML classes: {result.get('classes', 'N/A')}")
                print(f"✅ WikiRace: Cookies: {result.get('cookie', 'N/A')}")
            else:
                print(f"❌ WikiRace: Force {theme} theme failed: {result}")
        
        try:
            webView.page().runJavaScript(force_theme_js, handleForceResult)
        except Exception as e:
            print(f"❌ WikiRace: Error forcing {theme} theme: {e}")
    
    @staticmethod
    def forceDarkTheme(webView: QWebEngineView):
        """
        Backward compatibility method for forcing dark theme
        """
        return WikipediaTheme.forceTheme(webView, 'dark')
    
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
    
    # Class variable to track last setup theme to prevent conflicts
    _last_setup_theme = None
    _setup_in_progress = False
    
    @staticmethod
    def setupThemeWithNavigation(webView: QWebEngineView, theme: str = 'dark'):
        """
        OPTIMIZED: Combined theme setup and navigation hiding in a single DocumentCreation script
        This eliminates the 3-4 second delay by applying everything before the page renders
        Also sets up scripts for subsequent page navigations
        
        CRITICAL: This method handles theme switching for existing WebViews
        DO NOT REMOVE: Essential for preventing theme switching regressions
        
        THREAD-SAFE: Prevents race conditions when multiple WebViews share the same profile
        """
        print(f"🔄 WikiRace: [{time.time():.3f}] setupThemeWithNavigation called with theme: {theme}")
        
        # THREAD-SAFE: Prevent race conditions when multiple pages try to setup theme simultaneously
        if WikipediaTheme._setup_in_progress:
            print(f"⏳ WikiRace: [{time.time():.3f}] Theme setup already in progress, waiting...")
            # Wait a bit and try again
            import time as time_module
            time_module.sleep(0.1)
            if WikipediaTheme._setup_in_progress:
                print(f"⏳ WikiRace: [{time.time():.3f}] Theme setup still in progress, skipping duplicate setup")
                return
        
        # Check if theme is already set up correctly
        if WikipediaTheme._last_setup_theme == theme:
            print(f"✅ WikiRace: [{time.time():.3f}] Theme {theme} already set up correctly, skipping setup")
            return
        
        try:
            WikipediaTheme._setup_in_progress = True
            
            # CRITICAL: Clear all existing theme state to prevent conflicts
            # DO NOT REMOVE: This prevents old theme cookies/scripts from interfering
            WikipediaTheme._clearThemeState(webView)
            
            # Setup new theme
            WikipediaTheme._setupInitialTheme(webView, theme)
            WikipediaTheme._setupNavigationScripts(webView, theme)
            
            # Mark this theme as successfully set up
            WikipediaTheme._last_setup_theme = theme
            print(f"✅ WikiRace: [{time.time():.3f}] Theme setup completed successfully for {theme}")
            
        finally:
            WikipediaTheme._setup_in_progress = False
    
    @staticmethod
    def _setupInitialTheme(webView: QWebEngineView, theme: str = 'dark'):
        """
        Set up initial theme and DocumentCreation script
        """
        start_time = time.time()
        print(f"🚀 WikiRace: [{start_time:.3f}] Setting up initial {theme} theme with navigation hiding...")
        
        if not webView:
            print(f"❌ WikiRace: [{time.time():.3f}] WebView is None, cannot setup {theme} theme")
            return
            
        try:
            # Get the profile and cookie store
            profile_start = time.time()
            profile = webView.page().profile()
            store = profile.cookieStore()
            # Reduced logging for performance
            
            # Set the mwclientpreferences cookie for the specified theme
            cookie_start = time.time()
            if theme == 'light':
                cookie_val = b"skin-theme-clientpref-day"
                color_scheme = 'light'
                bg_color = '#FFFFFF'
                text_color = '#1A1A1A'
                theme_class = 'skin-theme-clientpref-day'
                remove_class = 'skin-theme-clientpref-night'
            else:
                cookie_val = b"skin-theme-clientpref-night"
                color_scheme = 'dark'
                bg_color = '#101418'
                text_color = '#ffffff'
                theme_class = 'skin-theme-clientpref-night'
                remove_class = 'skin-theme-clientpref-day'
                
            cookie = QNetworkCookie(b"mwclientpreferences", cookie_val)
            cookie.setDomain(".wikipedia.org")
            cookie.setPath("/")
            cookie.setExpirationDate(QDateTime.currentDateTimeUtc().addYears(5))
            
            try:
                cookie.setSameSitePolicy(QNetworkCookie.SameSite.Lax)
            except Exception:
                pass
            
            # Set cookie only for English Wikipedia (most commonly used)
            store.setCookie(cookie, QUrl("https://en.wikipedia.org/"))
            # OPTIMIZED: Reduced logging for performance
            
            # Create single optimized DocumentCreation script
            script_start = time.time()
            script = QWebEngineScript()
            script.setName(f"optimized-{theme}-setup")
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
            script.setRunsOnSubFrames(False)  # Only main frame for better performance
            
            # Combined script that does everything at once
            script.setSourceCode(f"""
            try {{
                var startTime = performance.now();
                var pageLoadStart = performance.timeOrigin + performance.now();
                console.log('WikiRace: [' + startTime.toFixed(3) + '] DocumentCreation script starting for {theme} theme');
                console.log('WikiRace: [' + startTime.toFixed(3) + '] Page load started at: ' + pageLoadStart.toFixed(3));
                
                // CRITICAL: Force clear any existing theme cookies first
                document.cookie = 'mwclientpreferences=; domain=.wikipedia.org; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                
                // Set new theme cookie immediately
                var cookieStart = performance.now();
                document.cookie = 'mwclientpreferences={cookie_val.decode()}; domain=.wikipedia.org; path=/; max-age=157680000; SameSite=Lax';
                // OPTIMIZED: Minimal logging for performance
                console.log('WikiRace: Theme cookie reset for {theme}');
                
                // Set theme background and classes immediately
                document.documentElement.style.backgroundColor = '{bg_color}';
                document.documentElement.style.color = '{text_color}';
                
                // CRITICAL: Aggressively remove ALL theme classes and set new one
                if (document.documentElement) {{
                    document.documentElement.classList.remove('skin-theme-clientpref-night', 'skin-theme-clientpref-day');
                    document.documentElement.classList.remove('vector-theme-dark', 'vector-theme-light');
                    document.documentElement.classList.add('{theme_class}');
                }}
                
                // Set color scheme meta tag
                var metaStart = performance.now();
                var meta = document.createElement('meta');
                meta.name = 'color-scheme';
                meta.content = '{color_scheme}';
                (document.head || document.documentElement).appendChild(meta);
                
                // Add DNS prefetch hints for faster loading
                var dnsPrefetch = document.createElement('link');
                dnsPrefetch.rel = 'dns-prefetch';
                dnsPrefetch.href = '//en.wikipedia.org';
                (document.head || document.documentElement).appendChild(dnsPrefetch);
                
                console.log('WikiRace: [' + performance.now().toFixed(3) + '] Meta and DNS prefetch added (+' + (performance.now() - metaStart).toFixed(1) + 'ms)');
                
                // Inject navigation hiding CSS immediately
                var cssStart = performance.now();
                var style = document.createElement('style');
                style.id = 'wikirace-optimized-styles';
                style.textContent = `{WikipediaTheme._HIDE_NAVIGATION_CSS}`;
                (document.head || document.documentElement).appendChild(style);
                // OPTIMIZED: Minimal logging for performance
                console.log('WikiRace: Navigation CSS injected at DocumentCreation');
                
                // REMOVED: MutationObserver to reduce main-thread work
                // REMOVED: Excessive logging to reduce performance overhead
                
                // OPTIMIZED: Minimal completion logging
                console.log('WikiRace: DocumentCreation completed for {theme} theme');
                setTimeout(function() {{
                    var checkTime = performance.now();
                    var header = document.querySelector('#mw-head, .vector-header');
                    var isHidden = header && (header.style.display === 'none' || getComputedStyle(header).display === 'none');
                    console.log('WikiRace: [' + checkTime.toFixed(3) + '] CSS effect check - header hidden: ' + isHidden + ' (+' + (checkTime - startTime).toFixed(1) + 'ms)');
                }}, 10);
                
            }} catch (e) {{
                console.log('WikiRace: [' + performance.now().toFixed(3) + '] Error in DocumentCreation script:', e);
            }}
            """)
            # CRITICAL: Remove ALL existing theme scripts before adding new one
            # This prevents theme conflicts when switching between dark/light modes
            # DO NOT REMOVE: This cleanup is essential to prevent old theme scripts
            # from overriding new theme settings during theme switches
            existing_scripts = profile.scripts()
            scripts_to_remove = []
            for i in range(existing_scripts.count()):
                script_list = existing_scripts.toList()
                if i < len(script_list):
                    existing_script = script_list[i]
                    script_name = existing_script.name()
                    # Remove ANY theme-related scripts (all themes)
                    if (script_name.startswith('prepaint-') or 
                        script_name.startswith('optimized-') or
                        script_name.startswith('navigation-hider-')):
                        scripts_to_remove.append(existing_script)
            
            for script_to_remove in scripts_to_remove:
                existing_scripts.remove(script_to_remove)
            
            if scripts_to_remove:
                print(f"🧹 WikiRace: [{time.time():.3f}] Cleaned up {len(scripts_to_remove)} old theme scripts")
            
            # Insert the new optimized script
            profile.scripts().insert(script)
            
            # Configure WebEngine settings for optimal performance
            settings = webView.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            
            # Performance optimizations (keep images enabled for better UX)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)  # Keep images for better experience
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)  # Disable plugins
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)  # Disable WebGL
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)  # Disable 2D canvas acceleration
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)  # Security + performance
            
            # Cache settings for faster repeat visits
            profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50MB cache
            
            # Set up request interceptor to block unnecessary resources
            WikipediaTheme._setupRequestInterceptor(profile)
            
            profile.setHttpUserAgent(f"WikiRace/1.0 (Optimized {theme.title()} Mode)")
            
            total_time = (time.time() - start_time) * 1000
            print(f"✅ WikiRace: Optimized {theme} theme setup completed")
            
        except Exception as e:
            error_time = time.time()
            print(f"❌ WikiRace: [{error_time:.3f}] Error in initial theme setup: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _setupNavigationScripts(webView: QWebEngineView, theme: str = 'dark'):
        """
        Set up scripts that run on every page load to ensure navigation elements are hidden
        """
        print(f"📜 WikiRace: [{time.time():.3f}] Setting up navigation scripts for {theme} theme")
        if not webView:
            return
            
        try:
            profile = webView.page().profile()
            
            # Create a script that runs on every page - using DOMContentLoaded for reliability
            nav_script = QWebEngineScript()
            nav_script.setName(f"navigation-hider-{theme}")
            nav_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            nav_script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
            nav_script.setRunsOnSubFrames(False)
            
            # Set theme-specific values
            if theme == 'light':
                bg_color = '#FFFFFF'
                text_color = '#1A1A1A'
            else:
                bg_color = '#101418'
                text_color = '#ffffff'
            
            nav_script.setSourceCode(f"""
            (function() {{
                try {{
                    // OPTIMIZED: Minimal operations for maximum performance
                    // Only inject navigation CSS if DocumentCreation script missed it
                    var existingStyle = document.getElementById('wikirace-navigation-css') || 
                                      document.getElementById('wikirace-optimized-styles');
                    
                    if (!existingStyle) {{
                        // Fallback injection if DocumentCreation script failed
                        var style = document.createElement('style');
                        style.id = 'wikirace-navigation-css';
                        style.textContent = `{WikipediaTheme._HIDE_NAVIGATION_CSS}`;
                        (document.head || document.documentElement).appendChild(style);
                        console.log('WikiRace: DocumentReady fallback CSS injected');
                    }}
                    
                    // OPTIMIZED: Minimal theme background enforcement
                    if (document.documentElement) {{
                        document.documentElement.style.backgroundColor = '{bg_color}';
                        document.documentElement.style.color = '{text_color}';
                    }}
                    
                }} catch (e) {{
                    // Silent error handling for performance
                }}
            }})();
            """)
            
            # CRITICAL: Remove ALL existing navigation scripts before adding new one
            # This prevents theme conflicts when switching between dark/light modes
            # DO NOT REMOVE: This cleanup is essential to prevent old theme scripts
            # from overriding new theme settings during theme switches
            existing_scripts = profile.scripts()
            scripts_to_remove = []
            for i in range(existing_scripts.count()):
                script_list = existing_scripts.toList()
                if i < len(script_list):
                    existing_script = script_list[i]
                    script_name = existing_script.name()
                    # Remove ANY navigation-related scripts (all themes)
                    if (script_name.startswith('navigation-hider-') or 
                        script_name.startswith('optimized-') or
                        script_name.startswith('prepaint-')):
                        scripts_to_remove.append(existing_script)
                        print(f"🧹 WikiRace: [{time.time():.3f}] Removing old script: {script_name}")
            
            for script_to_remove in scripts_to_remove:
                existing_scripts.remove(script_to_remove)
            
            print(f"🧹 WikiRace: [{time.time():.3f}] Cleaned up {len(scripts_to_remove)} old navigation scripts")
            
            # Insert the navigation script
            profile.scripts().insert(nav_script)
            print(f"✅ WikiRace: [{time.time():.3f}] Navigation script inserted successfully for {theme} theme")
            
        except Exception as e:
            print(f"❌ WikiRace: [{time.time():.3f}] Error setting up navigation scripts: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _setupRequestInterceptor(profile):
        """
        Set up a request interceptor to block unnecessary resources for faster loading
        """
        try:
            from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
            
            class FastLoadingInterceptor(QWebEngineUrlRequestInterceptor):
                def interceptRequest(self, info):
                    url = info.requestUrl().toString()
                    
                    # Block unnecessary resources for faster loading (keep images)
                    blocked_patterns = [
                        'googletagmanager.com',
                        'google-analytics.com', 
                        'doubleclick.net',
                        'googlesyndication.com',
                        'facebook.com/tr',
                        '.mp4', '.webm', '.ogg',  # Videos (still block these)
                        'analytics',
                        'tracking',
                        'ads'
                    ]
                    
                    for pattern in blocked_patterns:
                        if pattern in url.lower():
                            info.block(True)
                            return
            
            # Create and set the interceptor
            interceptor = FastLoadingInterceptor()
            profile.setUrlRequestInterceptor(interceptor)
            print("🚫 WikiRace: Request interceptor set up to block unnecessary resources")
            
        except Exception as e:
            print(f"⚠️ WikiRace: Could not set up request interceptor: {e}")
            # Continue without interceptor - not critical
    
    @staticmethod
    def _clearThemeState(webView: QWebEngineView):
        """
        CRITICAL: Clear all existing theme state (cookies, scripts) to prevent conflicts
        
        This method is ESSENTIAL for theme switching functionality.
        DO NOT REMOVE OR MODIFY without understanding the consequences:
        
        1. Clears all mwclientpreferences cookies (both light and dark)
        2. Removes all existing theme-related scripts
        3. Resets WebEngine profile state
        4. Without this, old theme state persists and causes conflicts
        
        REGRESSION PREVENTION:
        - This MUST be called before setting up new theme
        - ALL mwclientpreferences cookies MUST be cleared
        - ALL theme scripts MUST be removed
        - Profile state MUST be reset for theme switching to work
        """
        if not webView:
            return
            
        try:
            print(f"🧹 WikiRace: [{time.time():.3f}] Clearing all existing theme state...")
            
            profile = webView.page().profile()
            store = profile.cookieStore()
            
            # CRITICAL: Clear ALL mwclientpreferences cookies
            # DO NOT REMOVE: Old cookies will override new theme settings
            
            # Create empty cookie to clear existing ones
            clear_cookie = QNetworkCookie(b"mwclientpreferences", b"")
            clear_cookie.setDomain(".wikipedia.org")
            clear_cookie.setPath("/")
            clear_cookie.setExpirationDate(QDateTime.currentDateTimeUtc().addDays(-1))  # Expired = deleted
            
            # Clear cookies for all Wikipedia domains
            domains = [
                "https://en.wikipedia.org/",
                "https://www.en.wikipedia.org/",
                "https://wikipedia.org/",
                "https://www.wikipedia.org/"
            ]
            
            for domain in domains:
                store.setCookie(clear_cookie, QUrl(domain))
            
            print(f"🍪 WikiRace: [{time.time():.3f}] Cleared mwclientpreferences cookies from all domains")
            
            # CRITICAL: Remove ALL existing theme scripts
            # DO NOT REMOVE: Old scripts will continue running and override new theme
            existing_scripts = profile.scripts()
            scripts_to_remove = []
            for i in range(existing_scripts.count()):
                script_list = existing_scripts.toList()
                if i < len(script_list):
                    existing_script = script_list[i]
                    script_name = existing_script.name()
                    # Remove ALL theme-related scripts
                    if (script_name.startswith('navigation-hider-') or 
                        script_name.startswith('optimized-') or
                        script_name.startswith('prepaint-')):
                        scripts_to_remove.append(existing_script)
            
            for script_to_remove in scripts_to_remove:
                existing_scripts.remove(script_to_remove)
            
            if scripts_to_remove:
                print(f"🧹 WikiRace: [{time.time():.3f}] Removed {len(scripts_to_remove)} old theme scripts")
            
            # CRITICAL: Force clear any cached theme state via JavaScript
            # DO NOT REMOVE: Browser may cache theme state that needs clearing
            clear_js = """
            try {
                // Clear any cached theme preferences
                document.cookie = 'mwclientpreferences=; domain=.wikipedia.org; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
                
                // Remove any existing theme classes
                if (document.documentElement) {
                    document.documentElement.classList.remove('skin-theme-clientpref-night', 'skin-theme-clientpref-day');
                    document.documentElement.classList.remove('vector-theme-dark', 'vector-theme-light');
                }
                
                console.log('WikiRace: Theme state cleared via JavaScript');
            } catch (e) {
                console.log('WikiRace: Error clearing theme state:', e);
            }
            """
            
            webView.page().runJavaScript(clear_js)
            
            # Reset tracking variables since we cleared everything
            WikipediaTheme._last_setup_theme = None
            
            print(f"✅ WikiRace: [{time.time():.3f}] Theme state cleared successfully")
            
        except Exception as e:
            print(f"❌ WikiRace: [{time.time():.3f}] Error clearing theme state: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def applyMainPageCustomization(webView: QWebEngineView):
        """
        Apply main page specific customization (hide Main Page title, style Welcome title)
        This should only be called for the Wikipedia main page, not for article pages
        """
        if not webView:
            return
            
        print("🏠 WikiRace: Applying main page customization...")
        
        # Use JavaScript to precisely target and modify elements
        inject_js = """
        try {
            console.log('WikiRace: Starting main page customization...');
            
            // Hide the Main Page title specifically - try multiple selectors
            var selectors = [
                'h1.firstHeading',
                'h1#firstHeading', 
                '.vector-page-titlebar .mw-page-title',
                '.vector-page-titlebar .firstHeading',
                '.mw-page-title'
            ];
            
            for (var i = 0; i < selectors.length; i++) {
                var element = document.querySelector(selectors[i]);
                if (element && element.textContent.trim() === 'Main Page') {
                    element.style.display = 'none';
                    element.style.visibility = 'hidden';
                    console.log('WikiRace: Hidden Main Page title using selector:', selectors[i]);
                    
                    // Also collapse the empty titlebar container
                    var bar = document.querySelector('.vector-page-titlebar');
                    if (bar) {
                        bar.style.display = 'none';
                        bar.style.margin = '0';
                        bar.style.padding = '0';
                        console.log('WikiRace: Collapsed empty titlebar container');
                    }
                }
            }
            
            // Find and style the Welcome to Wikipedia text with new specifications
            var allElements = document.querySelectorAll('*');
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var text = element.textContent.trim();
                
                // Look for "Welcome to Wikipedia" text - be more flexible
                if (text === 'Welcome to Wikipedia' || text.includes('Welcome to Wikipedia') || 
                    text.includes('Welcome') && text.includes('Wikipedia')) {
                    // Make sure it's a heading or important text element
                    if (element.tagName && (element.tagName.toLowerCase() === 'h2' || 
                        element.tagName.toLowerCase() === 'h3' || 
                        element.tagName.toLowerCase() === 'h4' ||
                        element.classList.contains('mw-headline'))) {
                        
                        // Apply new styling specifications with !important to override any CSS
                        element.style.setProperty('font-size', 'clamp(24px, 2.6vw, 34px)', 'important');
                        element.style.setProperty('line-height', '1.15', 'important');
                        element.style.setProperty('font-weight', '600', 'important');
                        element.style.setProperty('white-space', 'nowrap', 'important');
                        element.style.setProperty('word-break', 'normal', 'important');
                        element.style.setProperty('letter-spacing', '0.2px', 'important');
                        element.style.setProperty('display', 'inline-block', 'important');
                        element.style.setProperty('visibility', 'visible', 'important');
                        
                        // Force its children not to stack
                        element.querySelectorAll('*').forEach(s => { 
                            s.style.display = 'inline'; 
                            s.style.whiteSpace = 'nowrap'; 
                        });
                        
                        // If the comma is its own node, merge any split nodes
                        element.textContent = element.textContent.replace(/\s*,\s*/g, ', ');
                        
                        console.log('WikiRace: Styled Welcome to Wikipedia text with new specifications:', text);
                        break;
                    }
                }
            }
            
            // Fallback: look for any heading that might be the welcome text
            var headings = document.querySelectorAll('h2, h3, h4, .mw-headline');
            for (var i = 0; i < headings.length; i++) {
                var heading = headings[i];
                var text = heading.textContent.trim();
                
                if (text.includes('Welcome') && text.includes('Wikipedia')) {
                    // Apply new styling specifications with !important to override any CSS
                    heading.style.setProperty('font-size', 'clamp(24px, 2.6vw, 34px)', 'important');
                    heading.style.setProperty('line-height', '1.15', 'important');
                    heading.style.setProperty('font-weight', '600', 'important');
                    heading.style.setProperty('white-space', 'nowrap', 'important');
                    heading.style.setProperty('word-break', 'normal', 'important');
                    heading.style.setProperty('letter-spacing', '0.2px', 'important');
                    heading.style.setProperty('display', 'inline-block', 'important');
                    heading.style.setProperty('visibility', 'visible', 'important');
                    
                    // Force its children not to stack
                    heading.querySelectorAll('*').forEach(s => { 
                        s.style.display = 'inline'; 
                        s.style.whiteSpace = 'nowrap'; 
                    });
                    
                    // If the comma is its own node, merge any split nodes
                    heading.textContent = heading.textContent.replace(/\s*,\s*/g, ', ');
                    
                    console.log('WikiRace: Styled welcome heading as fallback with new specifications:', text);
                    break;
                }
            }
            
            // Additional fallback: Try to find any large heading that might be the welcome text
            var largeHeadings = document.querySelectorAll('h1, h2, h3');
            for (var i = 0; i < largeHeadings.length; i++) {
                var heading = largeHeadings[i];
                var text = heading.textContent.trim();
                var computedStyle = window.getComputedStyle(heading);
                var fontSize = parseFloat(computedStyle.fontSize);
                
                // If it's a large heading and contains welcome/wikipedia keywords
                if (fontSize > 24 && (text.includes('Welcome') || text.includes('Wikipedia'))) {
                    console.log('WikiRace: Found large heading that might be welcome text:', text, 'font-size:', fontSize);
                    
                    // Apply new styling specifications with !important
                    heading.style.setProperty('font-size', 'clamp(24px, 2.6vw, 34px)', 'important');
                    heading.style.setProperty('line-height', '1.15', 'important');
                    heading.style.setProperty('font-weight', '600', 'important');
                    heading.style.setProperty('white-space', 'nowrap', 'important');
                    heading.style.setProperty('word-break', 'normal', 'important');
                    heading.style.setProperty('letter-spacing', '0.2px', 'important');
                    heading.style.setProperty('display', 'inline-block', 'important');
                    
                    // Force its children not to stack
                    heading.querySelectorAll('*').forEach(s => { 
                        s.style.display = 'inline'; 
                        s.style.whiteSpace = 'nowrap'; 
                    });
                    
                    // If the comma is its own node, merge any split nodes
                    heading.textContent = heading.textContent.replace(/\s*,\s*/g, ', ');
                    
                    console.log('WikiRace: Applied styling to large heading:', text);
                    break;
                }
            }
            
            console.log('WikiRace: Main page customization completed');
        } catch (e) {
            console.log('WikiRace: Error in main page customization:', e);
        }
        """
        
        try:
            webView.page().runJavaScript(inject_js)
            print("✅ WikiRace: Main page customization applied successfully")
        except Exception as e:
            print(f"❌ WikiRace: Error applying main page customization: {e}")
    
    @staticmethod
    def hideNavigationElements(webView: QWebEngineView):
        """
        DEPRECATED: Use the optimized setupThemeWithNavigation method instead.
        This method is kept for backward compatibility but should not be used for new code.
        """
        print("⚠️ WikiRace: Using deprecated hideNavigationElements method - consider using setupThemeWithNavigation")
        WikipediaTheme._injectNavigationCSS(webView)
    
    @staticmethod
    def _injectNavigationCSS(webView: QWebEngineView):
        """
        Optimized method to inject navigation hiding CSS immediately without DOM traversal
        """
        if not webView:
            return
            
        # Simple, fast CSS injection - no DOM manipulation
        inject_css_js = f"""
        try {{
            var style = document.getElementById('wikirace-hide-navigation');
            if (style) style.remove();
            
            style = document.createElement('style');
            style.id = 'wikirace-hide-navigation';
            style.textContent = `{WikipediaTheme._HIDE_NAVIGATION_CSS}`;
            
            (document.head || document.documentElement).appendChild(style);
            console.log('WikiRace: Navigation CSS injected successfully');
        }} catch (e) {{
            console.log('WikiRace: Error injecting navigation CSS:', e);
        }}
        """
        
        try:
            webView.page().runJavaScript(inject_css_js)
        except Exception as e:
            print(f"❌ WikiRace: Error injecting navigation CSS: {e}")

    @staticmethod
    def _old_hideNavigationElements_DEPRECATED(webView: QWebEngineView):
        """
        OLD METHOD - DEPRECATED AND SLOW
        This is the old implementation that caused 3-4 second delays
        Kept for reference only - DO NOT USE
        """
        print("⚠️ WikiRace: This is the OLD SLOW method - kept for reference only")
        print("⚠️ WikiRace: Use setupThemeWithNavigation() instead for instant performance")