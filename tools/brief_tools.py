"""Brief scaffolding and argument-outline tools.

These tools produce deterministic structural scaffolds for legal briefs.
They generate outlines from the brief frameworks in the local data,
construct IRAC-style argument structures, and draft issue statements. They
do not generate legal advice -- the output is a scaffold for attorney
review.
"""

from __future__ import annotations

import json
from typing import List, Optional

from utils import audit, get_data_manager


def register_brief_tools(mcp) -> None:
    """Register all brief tools with the MCP server."""

    data = get_data_manager()

    @mcp.tool()
    def generate_brief_outline(
        case_type: str, jurisdiction: Optional[str] = None
    ) -> str:
        """Generate a guided brief outline based on case type."""
        audit("generate_brief_outline", case_type=case_type, jurisdiction=jurisdiction)
        framework = data.get_brief_framework(case_type)
        if framework is None:
            available = list(data.brief_frameworks.keys())
            return json.dumps(
                {
                    "case_type": case_type,
                    "error": "No matching brief framework.",
                    "available_frameworks": available,
                },
                indent=2,
            )
        result = {
            "case_type": case_type,
            "jurisdiction": jurisdiction,
            "framework_id": framework["id"],
            "title": framework["title"],
            "outline": framework["sections"],
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def create_argument_structure(
        issue: str, authorities: Optional[List[str]] = None
    ) -> str:
        """Create an IRAC-style argument structure with authority integration."""
        audit("create_argument_structure", issue=issue, authorities=authorities)
        authorities = authorities or []
        result = {
            "issue": issue,
            "structure": {
                "issue": f"Whether {issue}",
                "rule": "State the governing legal rule and elements.",
                "application": "Apply the rule to the facts of this matter.",
                "conclusion": "State the conclusion that follows from the rule.",
            },
            "authorities": authorities,
            "note": "IRAC scaffold for attorney review; not legal advice.",
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def generate_issue_statement(facts: str, law: str) -> str:
        """Generate an issue-statement framework from facts and governing law."""
        audit("generate_issue_statement", facts=facts, law=law)
        statement = (
            f"Whether, under {law}, {facts.rstrip('.')}"
            f", the applicable legal standard is satisfied."
        )
        result = {
            "facts": facts,
            "law": law,
            "issue_statement": statement,
            "components": {
                "legal_question": "Whether the standard is satisfied",
                "governing_law": law,
                "material_facts": facts,
            },
        }
        return json.dumps(result, indent=2)
