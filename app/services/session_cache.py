"""In-memory cache for active search sessions.

Enables instant pagination and sorting without re-querying Jackett/Prowlarr,
and keeps callback data small enough to comfortably stay under Telegram's 64-byte limit.
"""

import time
from search_engine.models import SearchResults


class CachedSearch:
    __slots__ = ("query", "category", "results", "created_at")

    def __init__(self, query: str, category: str | None, results: SearchResults):
        self.query = query
        self.category = category
        self.results = results
        self.created_at = time.time()


class SearchSessionCache:
    def __init__(self, ttl: int = 1800, max_entries: int = 500):
        self._ttl = ttl
        self._max_entries = max_entries
        self._cache: dict[str, CachedSearch] = {}

    def get(self, session_id: str) -> CachedSearch | None:
        entry = self._cache.get(session_id)
        if not entry:
            return None
        if time.time() - entry.created_at > self._ttl:
            self._cache.pop(session_id, None)
            return None
        return entry

    def put(self, session_id: str, query: str, category: str | None, results: SearchResults) -> None:
        if len(self._cache) >= self._max_entries:
            # Prune oldest 20%
            oldest = sorted(self._cache.items(), key=lambda item: item[1].created_at)
            for k, _ in oldest[: max(1, self._max_entries // 5)]:
                self._cache.pop(k, None)
        self._cache[session_id] = CachedSearch(query, category, results)

