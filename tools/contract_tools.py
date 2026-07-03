"""Contract analysis and clause-differ tools.

These tools operate on the local contract templates. They provide a
clause-level differ, rule-based risk flagging, and template-based clause
extraction. Risk heuristics are intentionally transparent and deterministic
so their output can be audited and reviewed by an attorney.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from utils import audit, get_data_manager

# Transparent, keyword-based risk heuristics. Each entry maps a lowercase
# trigger phrase to a (risk_level, human-readable rationale) pair.
RISK_RULES: List[Tuple[str, str, str]] = [
    ("without limitation", "HIGH", "Potentially uncapped/unlimited liability."),
    ("indemnif", "MEDIUM", "Indemnification obligation present."),
    ("in perpetuity", "MEDIUM", "Perpetual obligation with no time limit."),
    ("perpetual", "MEDIUM", "Perpetual obligation with no time limit."),
    ("specifically marked", "MEDIUM", "Confidentiality narrowed to marked items."),
    ("sole discretion", "MEDIUM", "One-sided discretionary control."),
]


def _assess_clause_risk(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    flags: List[Dict[str, str]] = []
    highest = "LOW"
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    for trigger, level, rationale in RISK_RULES:
        if trigger in lowered:
            flags.append({"level": level, "rationale": rationale, "trigger": trigger})
            if order[level] > order[highest]:
                highest = level
    return {"risk_level": highest, "flags": flags}


def register_contract_tools(mcp) -> None:
    """Register all contract tools with the MCP server."""

    data = get_data_manager()

    @mcp.tool()
    def compare_contracts(contract_a: str, contract_b: str) -> str:
        """Compare two contracts and identify clause-level differences."""
        audit("compare_contracts", contract_a=contract_a, contract_b=contract_b)
        a = data.get_contract(contract_a)
        b = data.get_contract(contract_b)
        missing = [
            cid
            for cid, contract in ((contract_a, a), (contract_b, b))
            if contract is None
        ]
        if missing or a is None or b is None:
            return json.dumps(
                {"error": "Contract(s) not found.", "missing": missing},
                indent=2,
            )

        clauses_a: Dict[str, str] = a.get("clauses", {})
        clauses_b: Dict[str, str] = b.get("clauses", {})
        all_keys = sorted(set(clauses_a) | set(clauses_b))
        differences: List[Dict[str, Any]] = []
        for key in all_keys:
            text_a = clauses_a.get(key)
            text_b = clauses_b.get(key)
            if text_a == text_b:
                status = "identical"
                risk = "LOW"
            elif text_a is None:
                status = "only_in_b"
                risk = _assess_clause_risk(text_b or "")["risk_level"]
            elif text_b is None:
                status = "only_in_a"
                risk = _assess_clause_risk(text_a or "")["risk_level"]
            else:
                status = "modified"
                risk_a = _assess_clause_risk(text_a)["risk_level"]
                risk_b = _assess_clause_risk(text_b)["risk_level"]
                order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                risk = risk_a if order[risk_a] >= order[risk_b] else risk_b
                if risk == "LOW":
                    risk = "MEDIUM"
            if status != "identical":
                differences.append(
                    {
                        "clause": key,
                        "status": status,
                        "risk_level": risk,
                        "contract_a": text_a,
                        "contract_b": text_b,
                    }
                )

        result = {
            "contract_a": {"id": a["id"], "title": a.get("title")},
            "contract_b": {"id": b["id"], "title": b.get("title")},
            "identical_clause_count": len(all_keys) - len(differences),
            "difference_count": len(differences),
            "differences": differences,
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def analyze_clauses(contract_id: str, clause_type: Optional[str] = None) -> str:
        """Analyze contract clauses and identify risks."""
        audit("analyze_clauses", contract_id=contract_id, clause_type=clause_type)
        contract = data.get_contract(contract_id)
        if contract is None:
            return json.dumps(
                {"contract_id": contract_id, "error": "Contract not found."},
                indent=2,
            )
        clauses: Dict[str, str] = contract.get("clauses", {})
        selected = (
            {clause_type: clauses[clause_type]}
            if clause_type and clause_type in clauses
            else clauses
        )
        analysis = {
            name: {"text": text, **_assess_clause_risk(text)}
            for name, text in selected.items()
        }
        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        overall = "LOW"
        for entry in analysis.values():
            if order[entry["risk_level"]] > order[overall]:
                overall = entry["risk_level"]
        result = {
            "contract_id": contract["id"],
            "title": contract.get("title"),
            "overall_risk": overall,
            "clause_analysis": analysis,
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def extract_clauses(contract_id: str, template: Optional[str] = None) -> str:
        """Extract clauses from a contract, optionally filtered by template key."""
        audit("extract_clauses", contract_id=contract_id, template=template)
        contract = data.get_contract(contract_id)
        if contract is None:
            return json.dumps(
                {"contract_id": contract_id, "error": "Contract not found."},
                indent=2,
            )
        clauses: Dict[str, str] = contract.get("clauses", {})
        if template:
            clauses = {k: v for k, v in clauses.items() if template in k}
        result = {
            "contract_id": contract["id"],
            "title": contract.get("title"),
            "type": contract.get("type"),
            "clause_count": len(clauses),
            "clauses": clauses,
        }
        return json.dumps(result, indent=2)
