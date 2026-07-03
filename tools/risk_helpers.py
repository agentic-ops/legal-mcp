"""Shared clause risk heuristics for contract and document analysis."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

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

# Expected clause topics by contract type. Matching is substring-based on
# clause keys so naming variance (e.g. term_duration vs term_and_termination)
# still counts as present.
EXPECTED_CLAUSE_TOPICS_BY_TYPE: Dict[str, List[str]] = {
    "NDA": ["confidential", "term", "return", "governing_law", "remed"],
    "MSA": ["scope", "term", "liab", "governing_law"],
    "DPA": ["processing", "subject_rights", "security", "breach", "governing_law"],
    "BAA": ["permitted_use", "safeguard", "breach", "terminat", "governing_law"],
    "ToU": ["accept", "liab", "warrant", "governing_law", "arbitrat"],
    "PrivacyPolicy": [
        "data_collect",
        "data_use",
        "subject_rights",
        "retention",
        "contact",
    ],
    "AdvisorAgreement": [
        "service",
        "equity",
        "ip_assign",
        "confidential",
        "terminat",
        "governing_law",
    ],
    "OfferLetter": ["position", "compensation", "at_will", "start_date"],
    "SAFE": ["investment", "conversion", "valuation_cap", "governing_law"],
    "CookieNotice": ["types_of_cookies", "opt_out", "consent"],
}

GENERIC_ESSENTIAL_TOPICS = ["governing_law", "term", "liab", "terminat"]


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


def _topic_present(topic: str, clause_keys: Iterable[str]) -> bool:
    topic_lower = topic.lower()
    for key in clause_keys:
        key_lower = key.lower()
        if topic_lower in key_lower or key_lower in topic_lower:
            return True
    return False


def find_missing_clauses(
    clause_keys: Iterable[str],
    contract_type: Optional[str] = None,
) -> List[str]:
    """Return expected clause topics absent from the given clause keys."""

    keys = list(clause_keys)
    expected = EXPECTED_CLAUSE_TOPICS_BY_TYPE.get(
        contract_type or "",
        GENERIC_ESSENTIAL_TOPICS,
    )
    return [topic for topic in expected if not _topic_present(topic, keys)]
