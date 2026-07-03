"""Shared clause risk heuristics for contract and document analysis."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

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


def assess_clause_risk(text: str) -> Dict[str, Any]:
    """Return risk level and flags for a clause or paragraph."""

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
