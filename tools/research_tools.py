"""Precedent retrieval and statute extraction tools.

These tools query the local legal seed data. They perform no external
network calls in this build; adapters for CourtListener/RECAP and PACER are
planned (see README). Any future paid-database integration must respect the
cost warnings documented in the README.
"""

from __future__ import annotations

import json
from typing import Optional

from utils import audit, get_data_manager

FEE_NOTICE = (
    "Local seed data only. Live precedent adapters (CourtListener/RECAP, "
    "PACER) are not enabled in this build; PACER usage may incur fees."
)


def register_research_tools(mcp) -> None:
    """Register all research tools with the MCP server."""

    data = get_data_manager()

    @mcp.tool()
    def search_precedents(query: str, jurisdiction: Optional[str] = None) -> str:
        """Search for legal precedents based on query and jurisdiction.

        May incur third-party database fees (e.g., PACER) when live adapters
        are enabled; see README.
        """
        audit("search_precedents", query=query, jurisdiction=jurisdiction)
        matches = data.search_cases(query, jurisdiction)
        result = {
            "query": query,
            "jurisdiction": jurisdiction,
            "result_count": len(matches),
            "results": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "citation": c["citation"],
                    "court": c["court"],
                    "year": c["year"],
                    "holding": c["holding"],
                    "relevance_score": c["relevance_score"],
                }
                for c in matches
            ],
            "notice": FEE_NOTICE,
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def extract_statute(statute_id: str, context: bool = True) -> str:
        """Extract statute text with optional contextual analysis."""
        audit("extract_statute", statute_id=statute_id, context=context)
        statute = data.get_statute(statute_id)
        if statute is None:
            return json.dumps(
                {"statute_id": statute_id, "error": "Statute not found."},
                indent=2,
            )
        result = {
            "id": statute["id"],
            "title": statute["title"],
            "citation": statute["citation"],
            "jurisdiction": statute["jurisdiction"],
            "text": statute["text"],
        }
        if context:
            result["context"] = {
                "enacted": statute.get("enacted"),
                "last_amended": statute.get("last_amended"),
                "history": statute.get("history"),
                "topics": statute.get("topics", []),
            }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def search_case_law(query: str, jurisdiction: Optional[str] = None) -> str:
        """Search case law with relevance ranking.

        May incur third-party database fees (e.g., PACER) when live adapters
        are enabled; see README.
        """
        audit("search_case_law", query=query, jurisdiction=jurisdiction)
        matches = data.search_cases(query, jurisdiction)
        result = {
            "query": query,
            "jurisdiction": jurisdiction,
            "result_count": len(matches),
            "results": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "citation": c["citation"],
                    "court": c["court"],
                    "year": c["year"],
                    "topics": c.get("topics", []),
                    "holding": c["holding"],
                    "summary": c.get("summary"),
                    "relevance_score": c["relevance_score"],
                }
                for c in matches
            ],
            "notice": FEE_NOTICE,
        }
        return json.dumps(result, indent=2)
