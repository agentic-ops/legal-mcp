"""Brief templates, frameworks, and citation-standard resources."""

from __future__ import annotations

import json

from utils import audit, get_data_manager


def register_brief_resources(mcp) -> None:
    """Register all brief resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://brief-frameworks")
    def brief_frameworks() -> str:
        """Brief outline templates index."""
        audit("resource_brief_frameworks")
        index = [
            {
                "id": f["id"],
                "title": f["title"],
                "applicable_case_types": f.get("applicable_case_types", []),
                "section_count": len(f.get("sections", [])),
            }
            for f in data.brief_frameworks.values()
        ]
        return json.dumps({"count": len(index), "frameworks": index}, indent=2)

    @mcp.resource("legal://brief/{brief_id}/outline")
    def brief_outline(brief_id: str) -> str:
        """Brief structure and argument sections for a framework."""
        audit("resource_brief_outline", brief_id=brief_id)
        framework = data.get_brief_framework(brief_id)
        if framework is None:
            return json.dumps(
                {"brief_id": brief_id, "error": "Framework not found."},
                indent=2,
            )
        return json.dumps(framework, indent=2)

    @mcp.resource("legal://citation-standards")
    def citation_standards() -> str:
        """Citation formatting rules and reporter reference data."""
        audit("resource_citation_standards")
        return json.dumps(data.citation_standards, indent=2)
