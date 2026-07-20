"""Token lookup service for HRS."""

from __future__ import annotations

from typing import Any

from database import queries

Record = dict[str, Any]


class TokenService:
    """Provide read-only access to tokens created by VisitService."""

    @staticmethod
    def get_by_number(token_number: str) -> Record | None:
        """Return a token record by its visible token number."""
        return queries.get_token_by_number(token_number)
