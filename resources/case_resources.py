"""Case law and precedent resources."""

from __future__ import annotations

import json

from demo_mode import demo_data_disabled_payload, demo_payload
from utils import audit, get_data_manager


def register_case_resources(mcp) -> None:
    """Register all case resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://case-database")
    def case_database() -> str:
        """Legal precedent index."""
        audit("resource_case_database")
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload("Local case database resource"), indent=2
            )
        index = [
            {
                "source": "demo_seed",
                "authoritative": False,
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
        return json.dumps(demo_payload(count=len(index), cases=index), indent=2)

    @mcp.resource("legal://case/{case_id}/analysis")
    def case_analysis(case_id: str) -> str:
        """Case analysis with holding, summary, and citation graph."""
        audit("resource_case_analysis", case_id=case_id)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload("Demo case analysis resource"), indent=2
            )
        case = data.get_case(case_id)
        if case is None:
            return json.dumps(
                demo_payload(case_id=case_id, error="Case not found."), indent=2
            )
        cited = [
            {"id": cid, "name": data.cases.get(cid, {}).get("name")}
            for cid in case.get("cites", [])
        ]
        return json.dumps(
            demo_payload(
                source="demo_seed",
                authoritative=False,
                **case,
                cited_authorities=cited,
            ),
            indent=2,
        )
