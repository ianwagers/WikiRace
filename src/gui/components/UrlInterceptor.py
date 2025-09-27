"""
URL Request Interceptor for Wikipedia Navigation
Handles automatic addition of useskin=vector-2022 parameter, external link blocking, and resource filtering
"""

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class WikipediaUrlInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts navigation requests to add useskin=vector-2022, block external links, and filter resources"""
    
    def __init__(self, webview=None):
        super().__init__()
        self.webview = webview
    
    def interceptRequest(self, info):
        url = info.requestUrl()
        url_str = url.toString()
        nav_type = info.navigationType()
        
        # Debug: Log all requests to understand what's happening
        print(f"🔍 WikiRace: Interceptor called - URL: {url_str}, NavType: {nav_type}")
        
        # Handle resource blocking for performance (from WikipediaTheme)
        if nav_type != info.NavigationType.NavigationTypeLink:
            # Block unnecessary resources for faster loading (keep images)
            blocked_patterns = [
                'googletagmanager.com',
                'google-analytics.com', 
                'doubleclick.net',
                'googlesyndication.com',
                'facebook.com/tr',
                '.mp4', '.webm', '.ogg',  # Videos
                'tracking',
                'ads'
            ]
            
            # Allow Wikipedia's own modules even if they contain "analytics"
            if 'wikipedia.org' in url_str.lower():
                return  # Don't block Wikipedia's own resources
            
            # Block external analytics/tracking services
            for pattern in blocked_patterns:
                if pattern in url_str.lower():
                    print(f"🚫 WikiRace: Blocking external resource: {url_str}")
                    info.block(True)
                    return
            
            print(f"🔍 WikiRace: Non-link navigation: {url_str} (type: {nav_type})")
            return
        
        # Handle link navigation
        print(f"🔗 WikiRace: Link navigation detected: {url_str}")
        
        # Handle external links (non-Wikipedia domains)
        if not self._is_wikipedia_url(url_str):
            print(f"🚫 WikiRace: External link detected, blocking: {url_str}")
            info.block(True)
            
            # Navigate back to previous page if WebView is available
            if self.webview and hasattr(self.webview, 'back'):
                print(f"⬅️ WikiRace: Navigating back from external link")
                self.webview.back()
            
            return
        
        # Handle Wikipedia URLs that don't already have the skin parameter
        if ("wikipedia.org" in url_str and 
            "useskin=vector-2022" not in url_str):
            
            # Add useskin=vector-2022 to the URL
            if "?" in url_str:
                new_url_str = url_str + "&useskin=vector-2022"
            else:
                new_url_str = url_str + "?useskin=vector-2022"
            
            # Redirect to the new URL with the skin parameter
            new_url = QUrl(new_url_str)
            info.redirect(new_url)
            print(f"🔄 WikiRace: URL interceptor redirecting to: {new_url_str}")
    
    def _is_wikipedia_url(self, url_str):
        """Check if the URL is a Wikipedia domain"""
        wikipedia_domains = [
            'wikipedia.org',
            'wikimedia.org',
            'wikidata.org',
            'commons.wikimedia.org',
            'meta.wikimedia.org'
        ]
        
        return any(domain in url_str.lower() for domain in wikipedia_domains)
