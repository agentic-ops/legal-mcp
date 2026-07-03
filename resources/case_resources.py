"""Case law and precedent resources."""

from __future__ import annotations

import json

from utils import audit, get_data_manager


def register_case_resources(mcp) -> None:
    """Register all case resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://case-database")
    def case_database() -> str:
        """Legal precedent index."""
        audit("resource_case_database")
        index = [
            {
                "id": c["id"],
                "name": c["name"],
                "citation": c["citation"],
                "court": c["court"],
                "jurisdiction": c["jurisdiction"],
                "year": c["year"],
                "topics": c.get("topics", []),
            }
            for c in data.cases.values()
        ]
        return json.dumps({"count": len(index), "cases": index}, indent=2)

    @mcp.resource("legal://case/{case_id}/analysis")
    def case_analysis(case_id: str) -> str:
        """Case analysis with holding, summary, and citation graph."""
        audit("resource_case_analysis", case_id=case_id)
        case = data.get_case(case_id)
        if case is None:
            return json.dumps(
                {"case_id": case_id, "error": "Case not found."}, indent=2
            )
        cited = [
            {"id": cid, "name": data.cases.get(cid, {}).get("name")}
            for cid in case.get("cites", [])
        ]
        return json.dumps({**case, "cited_authorities": cited}, indent=2)
