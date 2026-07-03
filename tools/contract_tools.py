"""Contract analysis and clause-differ tools.

These tools operate on the local contract templates. They provide a
clause-level differ, rule-based risk flagging, and template-based clause
extraction. Risk heuristics are intentionally transparent and deterministic
so their output can be audited and reviewed by an attorney.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from tools.risk_helpers import assess_clause_risk
from utils import audit, get_data_manager

CLAUSE_ALTERNATIVES: Dict[str, List[Dict[str, str]]] = {
    "indemnification": [
        {
            "text": (
                "Each party shall indemnify the other only for third-party claims "
                "arising from its own negligence or willful misconduct, subject to "
                "a mutual cap equal to the fees paid under this Agreement in the "
                "twelve (12) months preceding the claim."
            ),
            "risk_level": "MEDIUM",
            "rationale": "Mutual, capped indemnity with a negligence carve-out.",
        },
        {
            "text": (
                "Indemnifying party's liability shall exclude indirect, incidental, "
                "or consequential damages and shall not exceed the greater of fees "
                "paid in the prior twelve months or $100,000."
            ),
            "risk_level": "MEDIUM",
            "rationale": "Caps exposure and excludes consequential damages.",
        },
        {
            "text": (
                "Each party shall defend and indemnify the other at its own expense "
                "for claims directly caused by that party's breach of confidentiality "
                "obligations, with reasonable cooperation requirements."
            ),
            "risk_level": "LOW",
            "rationale": "Narrow indemnity limited to confidentiality breaches.",
        },
    ],
    "limitation_of_liability": [
        {
            "text": (
                "Except for breaches of confidentiality or indemnification "
                "obligations, each party's aggregate liability shall not exceed "
                "the fees paid in the twelve (12) months preceding the claim."
            ),
            "risk_level": "LOW",
            "rationale": "Mutual cap with explicit carve-outs for key obligations.",
        },
        {
            "text": (
                "Neither party shall be liable for indirect, incidental, special, "
                "or consequential damages. Direct damages are capped at twice the "
                "fees paid in the prior twelve months."
            ),
            "risk_level": "LOW",
            "rationale": "Tiered liability with consequential damages excluded.",
        },
    ],
    "ip_assignment": [
        {
            "text": (
                "Work product created under this Agreement shall be deemed work "
                "made for hire; to the extent it is not, Provider assigns all "
                "right, title, and interest to Client, while retaining a "
                "non-exclusive license to use generalized know-how."
            ),
            "risk_level": "MEDIUM",
            "rationale": "Assigns IP while preserving a limited license-back.",
        },
        {
            "text": (
                "Provider grants Client an exclusive license to deliverables within "
                "the defined field of use; Provider retains ownership of pre-existing "
                "materials and background IP."
            ),
            "risk_level": "LOW",
            "rationale": "Field-of-use license instead of broad assignment.",
        },
    ],
    "non_compete": [
        {
            "text": (
                "During the term and for twelve (12) months thereafter, Recipient "
                "shall not solicit Client's employees within the geographic markets "
                "where services were performed."
            ),
            "risk_level": "MEDIUM",
            "rationale": "Temporal and geographic narrowing of restriction.",
        },
        {
            "text": (
                "Non-compete obligations apply only to direct competition with "
                "Client's core product line and only in jurisdictions where "
                "Recipient performed services."
            ),
            "risk_level": "LOW",
            "rationale": "Scope limited to direct competition and service regions.",
        },
    ],
    "governing_law": [
        {
            "text": (
                "This Agreement shall be governed by the laws of the State of "
                "Delaware, without regard to conflict-of-law principles."
            ),
            "risk_level": "LOW",
            "rationale": "Neutral, widely used commercial jurisdiction.",
        },
        {
            "text": (
                "This Agreement shall be governed by the laws of the State where "
                "the principal place of business of the performing party is located."
            ),
            "risk_level": "LOW",
            "rationale": "Ties governing law to the performing party's home state.",
        },
    ],
}

FALLBACK_ALTERNATIVES: List[Dict[str, str]] = [
    {
        "text": (
            "Revise the clause to include mutual obligations, explicit caps, and "
            "carve-outs for gross negligence or willful misconduct."
        ),
        "risk_level": "MEDIUM",
        "rationale": "Generic balancing language when clause type is unknown.",
    },
    {
        "text": (
            "Add a reasonableness standard and require written notice before "
            "enforcement of discretionary rights."
        ),
        "risk_level": "LOW",
        "rationale": "Reduces one-sided discretionary control.",
    },
]

DISCLAIMER = (
    "AI-generated suggestions for attorney review only. Not legal advice."
)

POSITION_MATRIX: Dict[tuple, tuple] = {
    ("HIGH", "buyer"):   ("reject",    "High-risk clause favors seller; seek mutual cap or deletion."),
    ("HIGH", "seller"):  ("negotiate", "High-risk clause; confirm scope is intentional."),
    ("HIGH", "mutual"):  ("negotiate", "High-risk; seek cap and carve-outs."),
    ("MEDIUM", "buyer"): ("negotiate", "Review and narrow scope before accepting."),
    ("MEDIUM", "seller"):("negotiate", "Confirm terms align with your risk tolerance."),
    ("MEDIUM", "mutual"):("negotiate", "Standard negotiation point."),
    ("LOW", "buyer"):    ("accept",    "Standard market language."),
    ("LOW", "seller"):   ("accept",    "Standard market language."),
    ("LOW", "mutual"):   ("accept",    "Standard market language."),
}


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
                risk = assess_clause_risk(text_b or "")["risk_level"]
            elif text_b is None:
                status = "only_in_a"
                risk = assess_clause_risk(text_a or "")["risk_level"]
            else:
                status = "modified"
                risk_a = assess_clause_risk(text_a)["risk_level"]
                risk_b = assess_clause_risk(text_b)["risk_level"]
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
            name: {"text": text, **assess_clause_risk(text)}
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

    @mcp.tool()
    def suggest_clause_alternatives(clause_text: str, clause_type: str) -> str:
        """Given risky clause text, return alternative phrasings with risk rationale.

        AI-generated suggestions for attorney review only. Not legal advice.
        """
        audit("suggest_clause_alternatives", clause_type=clause_type)
        normalized = clause_type.strip().lower().replace("-", "_").replace(" ", "_")
        alternatives = CLAUSE_ALTERNATIVES.get(normalized, FALLBACK_ALTERNATIVES)
        current_risk = assess_clause_risk(clause_text)
        result = {
            "clause_type": clause_type,
            "input_clause": clause_text,
            "current_risk": current_risk,
            "alternatives": alternatives,
            "disclaimer": DISCLAIMER,
            "notice": "not legal advice",
        }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def generate_negotiation_guide(
        contract_id: str,
        party_role: str = "buyer",
        focus_areas: Optional[List[str]] = None,
    ) -> str:
        """Generate a structured negotiation guide for a contract.

        Returns per-clause recommended positions (accept / negotiate / reject),
        rationale, and fallback language. AI-generated scaffold for attorney review.
        Not legal advice.
        """
        audit(
            "generate_negotiation_guide",
            contract_id=contract_id,
            party_role=party_role,
        )
        role = party_role.strip().lower()
        if role not in ("buyer", "seller", "mutual"):
            return json.dumps(
                {
                    "error": (
                        "party_role must be one of: 'buyer', 'seller', 'mutual'."
                    )
                },
                indent=2,
            )

        contract = data.get_contract(contract_id)
        if contract is None:
            return json.dumps(
                {"contract_id": contract_id, "error": "Contract not found."},
                indent=2,
            )

        clauses: Dict[str, str] = contract.get("clauses", {})
        if focus_areas:
            normalized_focus = [
                f.strip().lower().replace("-", "_").replace(" ", "_")
                for f in focus_areas
            ]
            clauses = {k: v for k, v in clauses.items() if k in normalized_focus}

        guide_entries: List[Dict[str, Any]] = []
        for clause_name, clause_text in clauses.items():
            risk_result = assess_clause_risk(clause_text)
            risk_level = risk_result["risk_level"]
            position, rationale = POSITION_MATRIX.get(
                (risk_level, role),
                ("negotiate", "Standard negotiation point."),
            )
            normalized_name = (
                clause_name.strip().lower().replace("-", "_").replace(" ", "_")
            )
            fallback_list = CLAUSE_ALTERNATIVES.get(normalized_name, FALLBACK_ALTERNATIVES)
            fallback_text = fallback_list[0]["text"] if fallback_list else ""
            guide_entries.append(
                {
                    "clause": clause_name,
                    "risk_level": risk_level,
                    "recommended_position": position,
                    "rationale": rationale,
                    "fallback_text": fallback_text,
                    "flags": risk_result.get("flags", []),
                }
            )

        result = {
            "contract_id": contract["id"],
            "title": contract.get("title"),
            "party_role": role,
            "clause_count": len(guide_entries),
            "guide": guide_entries,
            "disclaimer": DISCLAIMER,
            "notice": "not legal advice",
        }
        return json.dumps(result, indent=2)
