"""Privilege risk assessment tool.

Assesses attorney-client privilege risk before routing a document through an
AI inference provider. References ABA Model Rule 1.6 and US v. Heppner
(S.D.N.Y. 2026). Not legal advice — consult qualified counsel.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.document_tools import read_document_clauses
from utils import audit

PROVIDER_POSTURES: Dict[str, Dict[str, Any]] = {
    "ollama": {
        "zdr": True,
        "training_risk": False,
        "hipaa_baa": False,
        "description": "Fully local inference; data never leaves your machine.",
    },
    "azure_openai": {
        "zdr": "configurable",
        "training_risk": False,
        "hipaa_baa": True,
        "description": "Zero Data Retention configurable; HIPAA BAA available; no training on API data.",
    },
    "vertex_ai": {
        "zdr": "configurable",
        "training_risk": False,
        "hipaa_baa": True,
        "description": "Zero Data Retention configurable; HIPAA BAA available; no training on API data.",
    },
    "openrouter": {
        "zdr": "configurable",
        "training_risk": "upstream-dependent",
        "hipaa_baa": False,
        "description": "Routes to upstream providers; ZDR and training risk depend on selected upstream model.",
    },
    "openai": {
        "zdr": False,
        "training_risk": "API: no / consumer: yes",
        "hipaa_baa": False,
        "description": "API: no training by default, no ZDR. Consumer products (ChatGPT) may use data for training.",
    },
    "anthropic": {
        "zdr": False,
        "training_risk": "API: no / consumer: yes",
        "hipaa_baa": False,
        "description": "API: no training by default. Consumer products may use data. No ZDR option at this time.",
    },
    "unknown": {
        "zdr": False,
        "training_risk": True,
        "hipaa_baa": False,
        "description": "Unknown provider — assume worst-case posture for privilege analysis.",
    },
}

_AI_INDICATORS = [
    r"\bAs an AI(?: language model)?\b",
    r"\bI(?:'m| am) an AI\b",
    r"\bI do not have(?: the ability to| personal)?\b",
    r"\bI cannot provide legal advice\b",
    r"\bAs a large language model\b",
    r"\bI(?:'m| am) unable to\b",
]

_PRIVILEGE_INDICATORS = [
    r"\battorney.client\b",
    r"\bwork product\b",
    r"\bprivilege(?:d)?\b",
    r"\blegal advice\b",
    r"\bcounsel\b",
    r"\battorney\b",
    r"\blegal opinion\b",
    r"\bconfidential communication\b",
]


def _detect_ai_generation(full_text: str) -> bool:
    """Return True if text shows signs of AI generation."""
    for pattern in _AI_INDICATORS:
        if re.search(pattern, full_text, re.IGNORECASE):
            return True
    return False


def _detect_privilege_indicators(full_text: str) -> List[str]:
    """Return privilege-related phrases found in text."""
    found = []
    for pattern in _PRIVILEGE_INDICATORS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            found.append(match.group(0))
    return found


def _compute_risk_level(
    privilege_indicators: List[str],
    posture: Dict[str, Any],
    counsel_directed: bool,
    ai_generated: bool,
) -> str:
    """Compute privilege risk level: LOW / MEDIUM / HIGH / CRITICAL."""

    score = 0

    if privilege_indicators:
        score += 2

    zdr = posture.get("zdr")
    training_risk = posture.get("training_risk")

    if zdr is False:
        score += 1
    if training_risk is True or training_risk == "upstream-dependent":
        score += 2
    elif isinstance(training_risk, str) and "consumer: yes" in training_risk:
        score += 1

    if ai_generated:
        score += 1

    if counsel_directed:
        score -= 2

    if score <= 0:
        return "LOW"
    if score <= 1:
        return "MEDIUM"
    if score <= 3:
        return "HIGH"
    return "CRITICAL"


def register_privilege_tools(mcp) -> None:
    """Register privilege risk tools with the MCP server."""

    @mcp.tool()
    def check_privilege_risk(
        file_path: str,
        inference_provider: str = "unknown",
        counsel_directed: bool = False,
    ) -> str:
        """Assess privilege risk before routing a document through an AI inference provider.

        Checks: privilege indicators in the text, provider data retention posture,
        and counsel-direction status. Returns a risk level and recommended posture.
        References ABA Model Rule 1.6 and US v. Heppner (S.D.N.Y. 2026).
        Not legal advice.
        """
        audit(
            "check_privilege_risk",
            file_path=file_path,
            inference_provider=inference_provider,
            counsel_directed=counsel_directed,
        )

        try:
            clauses = read_document_clauses(file_path)
        except FileNotFoundError:
            return json.dumps(
                {"file_path": file_path, "error": "File not found."},
                indent=2,
            )
        except ValueError as exc:
            return json.dumps(
                {"file_path": file_path, "error": str(exc)},
                indent=2,
            )

        full_text = " ".join(clauses.values())
        provider_key = inference_provider.strip().lower()
        posture = PROVIDER_POSTURES.get(provider_key, PROVIDER_POSTURES["unknown"])
        privilege_indicators = _detect_privilege_indicators(full_text)
        ai_generated = _detect_ai_generation(full_text)
        risk_level = _compute_risk_level(
            privilege_indicators, posture, counsel_directed, ai_generated
        )

        if risk_level == "LOW":
            recommended_posture = (
                "Routing this document through the selected provider appears low-risk. "
                "Confirm provider's current data retention terms before proceeding."
            )
        elif risk_level == "MEDIUM":
            recommended_posture = (
                "Exercise caution. Review the provider's data retention and training "
                "policies before routing potentially privileged content. Consider a "
                "local or zero-data-retention provider."
            )
        elif risk_level == "HIGH":
            recommended_posture = (
                "Do not route this document without explicit attorney authorization. "
                "The document may contain privileged content and the selected provider "
                "does not offer zero data retention. Use a local inference provider "
                "(e.g., Ollama) or obtain a BAA/ZDR agreement."
            )
        else:
            recommended_posture = (
                "CRITICAL: Do not route this document through an AI inference provider "
                "without direct attorney oversight and a signed BAA or ZDR agreement. "
                "Routing may constitute inadvertent waiver of attorney-client privilege."
            )

        result = {
            "file_path": file_path,
            "inference_provider": inference_provider,
            "provider_posture": posture,
            "counsel_directed": counsel_directed,
            "privilege_indicators_found": privilege_indicators,
            "ai_generation_detected": ai_generated,
            "privilege_risk": risk_level,
            "recommended_posture": recommended_posture,
            "heppner_note": (
                "United States v. Heppner (S.D.N.Y. 2026) held that routing "
                "attorney-client privileged communications through a third-party AI "
                "inference provider may constitute a waiver of privilege where the "
                "provider retains data and the disclosure was not narrowly necessary."
            ),
            "aba_rule": (
                "ABA Model Rule 1.6 requires lawyers to make reasonable efforts to "
                "prevent inadvertent disclosure of client confidential information. "
                "ABA Formal Opinion 512 (2023) addresses competence obligations when "
                "using generative AI tools in legal practice."
            ),
            "disclosure_obligation_note": (
                "If this document is routed through an AI provider that retains data, "
                "consult with supervising counsel about disclosure obligations to the "
                "client under applicable professional responsibility rules."
            ),
            "notice": "Not legal advice. Consult qualified counsel before making privilege determinations.",
        }
        return json.dumps(result, indent=2)
