"""Callback-data protocol for the search flow.

Every search control (pagination, sort, category, pickers) round-trips search state
through Telegram callback data. Uses a short session id to safely guarantee
the payload stays well under Telegram's 64-byte callback-data limit in all languages.
"""

from dataclasses import dataclass

# One-char category codes; None (no category filter) is encoded as "0"
CATEGORY_CODES: dict[str | None, str] = {
    None: "0",
    "movies": "m",
    "tv": "t",
    "games": "g",
    "music": "u",
    "apps": "a",
    "anime": "n",
    "documentaries": "d",
    "others": "x",
}
CODE_TO_CATEGORY: dict[str, str | None] = {
    code: category for category, code in CATEGORY_CODES.items()
}


@dataclass(frozen=True)
class SearchState:
    query: str = ""
    session_id: str = ""
    category: str | None = None
    sort: str = "s"
    page: int = 1

    def pack(self, action: str) -> bytes:
        cat_code = CATEGORY_CODES.get(self.category, "0")
        if self.session_id:
            return f"{action}_{self.session_id}_{cat_code}{self.sort}{self.page}".encode()

        # Fallback to query if session_id is not set
        safe_query = self.query[:25]
        return f"{action}_{cat_code}{self.sort}{self.page}_{safe_query}".encode()

    @classmethod
    def unpack(cls, data: bytes) -> "SearchState":
        decoded = data.decode()
        parts = decoded.split("_")

        if len(parts) >= 3:
            # Session-based format: action_sessionid_state
            if len(parts[1]) == 8:
                session_id = parts[1]
                state_code = parts[2]
                cat = CODE_TO_CATEGORY.get(state_code[0])
                sort = state_code[1] if len(state_code) > 1 else "s"
                page = int(state_code[2:]) if len(state_code) > 2 and state_code[2:].isdigit() else 1
                return cls(
                    query="",
                    session_id=session_id,
                    category=cat,
                    sort=sort,
                    page=page,
                )

            # Legacy format: action_state_query
            _, state, query = decoded.split("_", 2)
            return cls(
                query=query,
                session_id="",
                category=CODE_TO_CATEGORY.get(state[0]),
                sort=state[1] if len(state) > 1 else "s",
                page=int(state[2:]) if len(state) > 2 and state[2:].isdigit() else 1,
            )

        return cls(query="")
