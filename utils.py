"""Core legal data management utilities for the Legal MCP Server.

This module provides two primary components:

* :class:`LegalDataManager` -- loads and caches the structured legal seed
  data (cases, statutes, contracts, brief frameworks, citation standards)
  from the ``data/`` directory and exposes typed accessors.
* :class:`CitationParser` -- deterministic, offline citation extraction,
  normalization, and validation utilities.

Everything here is deterministic and performs no network calls, in keeping
with the server's audit-friendly design.
"""

from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("legal_mcp.utils")

DATA_DIR = Path(__file__).resolve().parent / "data"


def audit(event: str, **details: Any) -> None:
    """Emit a structured audit log entry.

    Legal workflows require a traceable record of every operation. This
    helper centralises audit logging so tools and resources can record
    provenance without duplicating formatting logic.
    """

    payload = " ".join(f"{key}={value!r}" for key, value in details.items())
    logger.info("audit event=%s %s", event, payload)


class LegalDataManager:
    """Central data-access class for legal materials.

    Loads JSON seed data lazily and caches it in memory. Data files live in
    ``data/`` and can be refreshed at runtime via :meth:`reload`.
    """

    def __init__(self, data_dir: Optional[os.PathLike[str] | str] = None) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else DATA_DIR
        self._cache: Dict[str, Any] = {}

    # -- internal helpers -------------------------------------------------
    def _load(self, key: str, relative_path: str) -> Any:
        if key not in self._cache:
            path = self.data_dir / relative_path
            try:
                with path.open("r", encoding="utf-8") as handle:
                    self._cache[key] = json.load(handle)
            except FileNotFoundError:
                logger.warning("data file missing: %s", path)
                self._cache[key] = {}
        return self._cache[key]

    def reload(self) -> None:
        """Clear the in-memory cache so the next access re-reads from disk."""

        self._cache.clear()
        audit("data_reload", data_dir=str(self.data_dir))

    # -- raw collections --------------------------------------------------
    @property
    def cases(self) -> Dict[str, Any]:
        return self._load("cases", "cases/cases.json")

    @property
    def statutes(self) -> Dict[str, Any]:
        return self._load("statutes", "statutes/statutes.json")

    @property
    def contracts(self) -> Dict[str, Any]:
        return self._load("contracts", "contracts/contracts.json")

    @property
    def brief_frameworks(self) -> Dict[str, Any]:
        return self._load("brief_frameworks", "templates/brief_frameworks.json")

    @property
    def citation_standards(self) -> Dict[str, Any]:
        return self._load("citation_standards", "citation_standards.json")

    # -- case accessors ---------------------------------------------------
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.cases.get(case_id)

    def search_cases(
        self, query: str, jurisdiction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return cases ranked by keyword relevance to ``query``.

        Ranking is a deterministic keyword-overlap score across the case
        name, topics, holding, and summary.
        """

        terms = [t for t in re.split(r"\W+", query.lower()) if t]
        results: List[Dict[str, Any]] = []
        for case in self.cases.values():
            if jurisdiction and case.get("jurisdiction") != jurisdiction:
                continue
            haystack = " ".join(
                [
                    case.get("name", ""),
                    " ".join(case.get("topics", [])),
                    case.get("holding", ""),
                    case.get("summary", ""),
                ]
            ).lower()
            score = sum(haystack.count(term) for term in terms)
            if score > 0 or not terms:
                enriched = dict(case)
                enriched["relevance_score"] = score
                results.append(enriched)
        results.sort(key=lambda c: c["relevance_score"], reverse=True)
        return results

    # -- statute accessors ------------------------------------------------
    def get_statute(self, statute_id: str) -> Optional[Dict[str, Any]]:
        return self.statutes.get(statute_id)

    # -- contract accessors -----------------------------------------------
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        contract = self.contracts.get(contract_id)
        if contract is not None:
            return contract
        # Resolve aliases (e.g. NDA_v1 -> standard_nda_template).
        for candidate in self.contracts.values():
            if contract_id in candidate.get("aliases", []):
                return candidate
        return None

    def list_contracts(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": c["id"],
                "title": c.get("title"),
                "type": c.get("type"),
                "aliases": c.get("aliases", []),
                "clause_count": len(c.get("clauses", {})),
            }
            for c in self.contracts.values()
        ]

    # -- brief accessors --------------------------------------------------
    def get_brief_framework(self, framework_id: str) -> Optional[Dict[str, Any]]:
        framework = self.brief_frameworks.get(framework_id)
        if framework is not None:
            return framework
        # Fall back to matching by applicable case type.
        for candidate in self.brief_frameworks.values():
            if framework_id in candidate.get("applicable_case_types", []):
                return candidate
        return None

    # -- diagnostics ------------------------------------------------------
    def stats(self) -> Dict[str, int]:
        return {
            "cases": len(self.cases),
            "statutes": len(self.statutes),
            "contracts": len(self.contracts),
            "brief_frameworks": len(self.brief_frameworks),
            "reporters": len(self.citation_standards.get("reporters", {})),
        }


class CitationParser:
    """Citation extraction, normalization, and validation utilities.

    The parser is intentionally offline and rule-based. It recognises legal
    citations of the common ``<volume> <reporter> <page>`` form, optionally
    prefixed with a case name and suffixed with a pincite.
    """

    # <case name>, <volume> <reporter> <page>[, <pincite>]
    CITATION_RE = re.compile(
        r"^(?:(?P<case>.+?),\s*)?"
        r"(?P<volume>\d+)\s+"
        r"(?P<reporter>[A-Za-z][A-Za-z0-9.\s]*?[A-Za-z0-9.])\s+"
        r"(?P<page>\d+)"
        r"(?:,\s*(?P<pincite>\d+))?$"
    )

    # Inline finder for extracting citations from free text.
    INLINE_RE = re.compile(
        r"\b(?P<volume>\d+)\s+"
        r"(?P<reporter>(?:[A-Z][A-Za-z.]*\.?\s?)+?\d*[a-z]{0,2})\s+"
        r"(?P<page>\d+)\b"
    )

    def __init__(self, data_manager: Optional[LegalDataManager] = None) -> None:
        self.data = data_manager or get_data_manager()

    # -- helpers ----------------------------------------------------------
    @property
    def _reporters(self) -> Dict[str, Any]:
        return self.data.citation_standards.get("reporters", {})

    @property
    def _name_abbreviations(self) -> Dict[str, str]:
        return self.data.citation_standards.get("case_name_abbreviations", {})

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _match_reporter(self, reporter: str) -> Optional[str]:
        """Return the canonical reporter key matching ``reporter`` (loosely)."""

        normalized = self._collapse_whitespace(reporter)
        # Exact match first.
        if normalized in self._reporters:
            return normalized
        # Compare ignoring spaces (e.g. "Cal. App. 4th" vs "Cal.App.4th").
        squashed = normalized.replace(" ", "")
        for key in self._reporters:
            if key.replace(" ", "") == squashed:
                return key
        return None

    # -- public API -------------------------------------------------------
    def parse(self, citation: str) -> Optional[Dict[str, Any]]:
        """Parse a single citation string into structured components."""

        match = self.CITATION_RE.match(self._collapse_whitespace(citation))
        if not match:
            return None
        parts = match.groupdict()
        return {
            "case_name": (parts["case"] or "").strip() or None,
            "volume": int(parts["volume"]),
            "reporter": self._collapse_whitespace(parts["reporter"]),
            "page": int(parts["page"]),
            "pincite": int(parts["pincite"]) if parts["pincite"] else None,
        }

    def extract_citations(self, text: str) -> List[str]:
        """Extract citation-like substrings from free-form text."""

        found: List[str] = []
        for match in self.INLINE_RE.finditer(text):
            reporter = self._collapse_whitespace(match.group("reporter"))
            if self._match_reporter(reporter) is None:
                continue
            citation = f"{match.group('volume')} {reporter} {match.group('page')}"
            if citation not in found:
                found.append(citation)
        return found

    def abbreviate_case_name(self, name: str) -> str:
        """Apply Bluebook-style word abbreviations to a case name."""

        def replace(token: str) -> str:
            stripped = token.strip(".,")
            abbrev = self._name_abbreviations.get(stripped)
            return abbrev if abbrev else token

        return " ".join(replace(token) for token in name.split())

    def normalize(self, citation: str, jurisdiction: Optional[str] = None) -> str:
        """Normalize spacing and case-name abbreviations for a citation."""

        parsed = self.parse(citation)
        if not parsed:
            return self._collapse_whitespace(citation)
        pieces = []
        if parsed["case_name"]:
            pieces.append(self.abbreviate_case_name(parsed["case_name"]) + ",")
        core = f"{parsed['volume']} {parsed['reporter']} {parsed['page']}"
        pieces.append(core)
        result = " ".join(pieces)
        if parsed["pincite"] is not None:
            result += f", {parsed['pincite']}"
        return result

    def validate(
        self, citation: str, format_standard: str = "bluebook"
    ) -> Dict[str, Any]:
        """Validate a citation and return a structured report."""

        issues: List[str] = []
        parsed = self.parse(citation)
        if not parsed:
            return {
                "input": citation,
                "valid": False,
                "issues": ["Could not parse citation structure."],
                "components": None,
                "normalized": None,
                "format_standard": format_standard,
            }

        reporter_key = self._match_reporter(parsed["reporter"])
        if reporter_key is None:
            issues.append(f"Unrecognized reporter '{parsed['reporter']}'.")
        if not parsed["case_name"]:
            issues.append("Missing case name (citation lacks a party line).")

        reporter_info = self._reporters.get(reporter_key) if reporter_key else None
        return {
            "input": citation,
            "valid": not issues,
            "issues": issues,
            "components": parsed,
            "reporter": reporter_info,
            "normalized": self.normalize(citation),
            "format_standard": format_standard,
        }


@lru_cache(maxsize=1)
def get_data_manager() -> LegalDataManager:
    """Return the process-wide :class:`LegalDataManager` singleton."""

    return LegalDataManager()
