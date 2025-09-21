"""
URL Request Interceptor for Wikipedia Navigation
Handles automatic addition of useskin=vector-2022 parameter
"""

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class WikipediaUrlInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts navigation requests to add useskin=vector-2022 before loading"""
    
    def interceptRequest(self, info):
        url = info.requestUrl()
        url_str = url.toString()
        
        # Only intercept Wikipedia URLs that don't already have the skin parameter
        if ("wikipedia.org" in url_str and 
            "useskin=vector-2022" not in url_str and 
            info.navigationType() == info.NavigationType.NavigationTypeLink):
            
            # Add useskin=vector-2022 to the URL
            if "?" in url_str:
                new_url_str = url_str + "&useskin=vector-2022"
            else:
                new_url_str = url_str + "?useskin=vector-2022"
            
            # Redirect to the new URL with the skin parameter
            new_url = QUrl(new_url_str)
            info.redirect(new_url)
            print(f"🔄 WikiRace: URL interceptor redirecting to: {new_url_str}")
