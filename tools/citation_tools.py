"""Citation validation and normalization tools.

Backed by :class:`utils.CitationParser`, these tools validate citation
structure, normalize spacing and Bluebook-style abbreviations, and verify
whether a citation cross-references a known case in the local database.
"""

from __future__ import annotations

import json
from typing import Optional

from demo_mode import demo_data_disabled_payload, demo_payload
from utils import CitationParser, audit, get_data_manager


def register_citation_tools(mcp) -> None:
    """Register all citation tools with the MCP server."""

    data = get_data_manager()
    parser = CitationParser(data)

    @mcp.tool()
    def validate_citation(citation: str, format_standard: str = "bluebook") -> str:
        """Validate citation structure and reporter format only.

        This does not establish that a case exists or remains good law.
        """
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
    def check_demo_database(citation: str) -> str:
        """Check whether a citation appears in the bundled demo case data.

        A match is not verification that a case exists or remains good law.
        """
        audit("check_demo_database", citation=citation)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload(
                    "Demo citation lookup",
                    [
                        "Use validate_citation for structure and reporter formatting.",
                        "Enable and configure CourtListener for live case-law research.",
                        "Set LEGAL_MCP_DEMO_MODE=true only for demonstrations or testing.",
                    ],
                ),
                indent=2,
            )
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
        result = demo_payload(
            input=citation,
            parsed=parsed,
            found_in_demo_database=match is not None,
            matched_demo_case=(
                {
                    "id": match["id"],
                    "name": match["name"],
                    "citation": match["citation"],
                }
                if match
                else None
            ),
        )
        return json.dumps(result, indent=2)
