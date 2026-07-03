"""Statutory materials resources."""

from __future__ import annotations

import json

from utils import audit, get_data_manager


def register_statute_resources(mcp) -> None:
    """Register all statute resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://statute-library")
    def statute_library() -> str:
        """Statutory materials index."""
        audit("resource_statute_library")
        index = [
            {
                "id": s["id"],
                "title": s["title"],
                "citation": s["citation"],
                "jurisdiction": s["jurisdiction"],
                "topics": s.get("topics", []),
            }
            for s in data.statutes.values()
        ]
        return json.dumps({"count": len(index), "statutes": index}, indent=2)

    @mcp.resource("legal://statute/{statute_id}/context")
    def statute_context(statute_id: str) -> str:
        """Statutory context and legislative history."""
        audit("resource_statute_context", statute_id=statute_id)
        statute = data.get_statute(statute_id)
        if statute is None:
            return json.dumps(
                {"statute_id": statute_id, "error": "Statute not found."},
                indent=2,
            )
        return json.dumps(statute, indent=2)
