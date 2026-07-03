"""Citation validation and normalization tools.

Backed by :class:`utils.CitationParser`, these tools validate citation
structure, normalize spacing and Bluebook-style abbreviations, and verify
whether a citation cross-references a known case in the local database.
"""

from __future__ import annotations

import json
from typing import Optional

from utils import CitationParser, audit, get_data_manager


def register_citation_tools(mcp) -> None:
    """Register all citation tools with the MCP server."""

    data = get_data_manager()
    parser = CitationParser(data)

    @mcp.tool()
    def validate_citation(citation: str, format_standard: str = "bluebook") -> str:
        """Validate and normalize citation format."""
        audit("validate_citation", citation=citation, standard=format_standard)
        report = parser.validate(citation, format_standard)
        return json.dumps(report, indent=2)

    @mcp.tool()
    def normalize_citation(citation: str, jurisdiction: Optional[str] = None) -> str:
        """Normalize citation to standard format."""
        audit("normalize_citation", citation=citation, jurisdiction=jurisdiction)
        result = {
            "input": citation,
            "normalized": parser.normalize(citation, jurisdiction),
            "components": parser.parse(citation),
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def verify_citation_integrity(citation: str) -> str:
        """Verify citation integrity against the local case database."""
        audit("verify_citation_integrity", citation=citation)
        parsed = parser.parse(citation)
        normalized_core = None
        if parsed:
            normalized_core = (
                f"{parsed['volume']} {parsed['reporter']} {parsed['page']}"
            )
        match = None
        for case in data.cases.values():
            case_core = case.get("citation")
            if normalized_core and case_core == normalized_core:
                match = case
                break
        result = {
            "input": citation,
            "parsed": parsed,
            "found_in_database": match is not None,
            "matched_case": (
                {
                    "id": match["id"],
                    "name": match["name"],
                    "citation": match["citation"],
                }
                if match
                else None
            ),
        }
        return json.dumps(result, indent=2)
