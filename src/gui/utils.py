"""Shared GUI utilities for WikiRace."""

from pathlib import Path
from PyQt6.QtGui import QIcon

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_ICON_PATH = _PROJECT_ROOT / 'src' / 'resources' / 'icons' / 'favicon.ico'


def set_window_icon(widget) -> None:
    """Apply the WikiRace favicon to a widget's window icon."""
    if _ICON_PATH.exists():
        widget.setWindowIcon(QIcon(str(_ICON_PATH)))


def configure_web_profile():
    """Apply standard persistent-cache settings to the default WebEngine profile.

    Returns the profile so callers that need to attach interceptors can do so
    without fetching it a second time.
    """
    from PyQt6.QtWebEngineCore import QWebEngineProfile
    profile = QWebEngineProfile.defaultProfile()
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
    )
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50 MB
    return profile
