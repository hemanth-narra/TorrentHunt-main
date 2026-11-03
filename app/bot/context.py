"""Shared application context.

One module-level singleton holds the app-lifetime dependencies and runtime
state shared across handlers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from localization import LanguageService
    from models.explicit_detector.explicit_detector import ExplicitDetector
    from services.search import SearchService
    from services.session_cache import SearchSessionCache
    from telethon.tl.types import User


class Context:
    # Assigned during startup, before any handler runs
    language_service: "LanguageService"
    explicit_detector: "ExplicitDetector"
    search: "SearchService"
    session_cache: "SearchSessionCache"
    me: "User"

    def __init__(self) -> None:
        self.sites: dict[str, dict[str, str]] = {}  # inline-searchable sources


ctx = Context()
