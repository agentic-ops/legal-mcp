"""Precedent retrieval and statute extraction tools.

These tools query explicitly enabled demo content and optional live sources.
Bundled sample legal content is disabled in production mode. Any paid-database
integration must respect the cost warnings documented in the README.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from demo_mode import demo_data_disabled_payload, demo_payload
from integrations import CourtListenerClient, get_integration_settings
from utils import audit, get_data_manager

FEE_NOTICE = (
    "Results are from explicitly enabled demo seed data, not verified legal "
    "authority. Live sources (CourtListener/RECAP, "
    "PACER) are optional and disabled by default; enable them via feature "
    "flags and query them with the 'search_live_case_law' tool. Check "
    "'integration_status' first. PACER usage may incur fees."
)


def _case_result_key(result: Dict[str, Any]) -> Optional[str]:
    for key in ("citation", "caseName", "name", "id"):
        value = result.get(key)
        if value:
            return str(value).strip().lower()
    return None


def _merge_case_results(
    local_results: List[Dict[str, Any]],
    live_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for result in local_results + live_results:
        dedupe_key = _case_result_key(result)
        if dedupe_key and dedupe_key in seen:
            continue
        if dedupe_key:
            seen.add(dedupe_key)
        merged.append(result)
    return merged


def register_research_tools(mcp) -> None:
    """Register all research tools with the MCP server."""

    data = get_data_manager()

    @mcp.tool()
    def search_precedents(query: str, jurisdiction: Optional[str] = None) -> str:
        """Search for legal precedents based on query and jurisdiction.

        May incur third-party database fees (e.g., PACER) when live adapters
        are enabled; see README.
        """
        audit("search_precedents", query=query, jurisdiction=jurisdiction)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload("Local precedent search"), indent=2
            )
        matches = data.search_cases(query, jurisdiction)
        result = demo_payload(
            query=query,
            jurisdiction=jurisdiction,
            result_count=len(matches),
            results=[
                {
                    "source": "demo_seed",
                    "authoritative": False,
                    "id": c["id"],
                    "name": c["name"],
                    "citation": c["citation"],
                    "court": c["court"],
                    "year": c["year"],
                    "holding": c["holding"],
                    "relevance_score": c["relevance_score"],
                }
                for c in matches
            ],
            notice=FEE_NOTICE,
        )
        return json.dumps(result, indent=2)

    @mcp.tool()
    def extract_statute(statute_id: str, context: bool = True) -> str:
        """Extract statute text with optional contextual analysis."""
        audit("extract_statute", statute_id=statute_id, context=context)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload(
                    "Bundled statute lookup",
                    [
                        "Use a verified statute source or user-supplied document.",
                        "Set LEGAL_MCP_DEMO_MODE=true only for demonstrations or testing.",
                    ],
                ),
                indent=2,
            )
        statute = data.get_statute(statute_id)
        if statute is None:
            return json.dumps(
                demo_payload(statute_id=statute_id, error="Statute not found."),
                indent=2,
            )
        result = demo_payload(
            source="demo_seed",
            authoritative=False,
            id=statute["id"],
            title=statute["title"],
            citation=statute["citation"],
            jurisdiction=statute["jurisdiction"],
            text=statute["text"],
        )
        if context:
            result["context"] = {
                "enacted": statute.get("enacted"),
                "last_amended": statute.get("last_amended"),
                "history": statute.get("history"),
                "topics": statute.get("topics", []),
            }
        return json.dumps(result, indent=2)

    @mcp.tool()
    def search_case_law(query: str, jurisdiction: Optional[str] = None) -> str:
        """Search case law with relevance ranking.

        May incur third-party database fees (e.g., PACER) when live adapters
        are enabled; see README.
        """
        audit("search_case_law", query=query, jurisdiction=jurisdiction)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload("Local case-law search"), indent=2
            )
        matches = data.search_cases(query, jurisdiction)
        result = demo_payload(
            query=query,
            jurisdiction=jurisdiction,
            result_count=len(matches),
            results=[
                {
                    "source": "demo_seed",
                    "authoritative": False,
                    "id": c["id"],
                    "name": c["name"],
                    "citation": c["citation"],
                    "court": c["court"],
                    "year": c["year"],
                    "topics": c.get("topics", []),
                    "holding": c["holding"],
                    "summary": c.get("summary"),
                    "relevance_score": c["relevance_score"],
                }
                for c in matches
            ],
            notice=FEE_NOTICE,
        )
        return json.dumps(result, indent=2)

    @mcp.tool()
    def research_legal_issue(
        issue: str,
        jurisdiction: Optional[str] = None,
        include_statutes: bool = True,
    ) -> str:
        """Aggregate local case search, CourtListener (if enabled), and statutes.

        Returns a single research response with source attribution and
        deduplicated case results.
        """
        audit(
            "research_legal_issue",
            issue=issue,
            jurisdiction=jurisdiction,
            include_statutes=include_statutes,
        )

        local_cases = data.search_cases(issue, jurisdiction) if data.demo_mode else []
        local_case_results = [
            {
                "source": "demo_seed",
                "authoritative": False,
                "id": case["id"],
                "name": case["name"],
                "citation": case["citation"],
                "court": case["court"],
                "year": case["year"],
                "holding": case["holding"],
                "summary": case.get("summary"),
                "relevance_score": case["relevance_score"],
            }
            for case in local_cases
        ]

        live_case_results: List[Dict[str, Any]] = []
        live_status: Optional[Dict[str, Any]] = None
        settings = get_integration_settings()
        courtlistener = CourtListenerClient(settings.courtlistener)
        live_payload = courtlistener.search(issue)
        live_status = {
            "enabled": live_payload.get("enabled"),
            "configured": settings.courtlistener.configured,
            "message": live_payload.get("message"),
            "error": live_payload.get("error"),
        }
        for item in live_payload.get("results", []):
            live_case_results.append(
                {
                    "source": "courtlistener",
                    "authoritative": False,
                    "verification_required": True,
                    "name": item.get("caseName") or item.get("case_name"),
                    "citation": item.get("citation") or item.get("citeCount"),
                    "court": item.get("court"),
                    "year": item.get("dateFiled") or item.get("year"),
                    "holding": item.get("snippet") or item.get("text"),
                    "summary": item.get("snippet"),
                    "relevance_score": item.get("score"),
                }
            )

        merged_cases = _merge_case_results(local_case_results, live_case_results)

        statutes: List[Dict[str, Any]] = []
        if include_statutes and data.demo_mode:
            statutes = [
                {
                    "source": "demo_seed",
                    "authoritative": False,
                    "id": statute["id"],
                    "title": statute["title"],
                    "citation": statute["citation"],
                    "jurisdiction": statute["jurisdiction"],
                    "text": statute["text"],
                    "relevance_score": statute["relevance_score"],
                }
                for statute in data.search_statutes(issue, jurisdiction)
            ]

        source_available = bool(
            data.demo_mode
            or (
                settings.courtlistener.enabled
                and settings.courtlistener.configured
                and not live_payload.get("error")
            )
        )
        fields: Dict[str, Any] = {
            "issue": issue,
            "jurisdiction": jurisdiction,
            "available": source_available,
            "case_result_count": len(merged_cases),
            "cases": merged_cases,
            "statutes": statutes if include_statutes else None,
            "demo_data_included": data.demo_mode,
            "courtlistener_status": live_status,
            "notice": (
                "Aggregated research scaffold for attorney review only. "
                "Not legal advice."
            ),
        }
        if not source_available:
            fields["error"] = "no_research_source_enabled"
            fields["message"] = (
                "No research source is available. Demo data is disabled and "
                "CourtListener is not enabled and configured."
            )
            fields["next_steps"] = [
                "Enable and configure CourtListener for live case-law research.",
                "Set LEGAL_MCP_DEMO_MODE=true only for demonstrations or testing.",
            ]
        result = (
            demo_payload(**fields)
            if data.demo_mode
            else {
                "data_mode": "production",
                **fields,
            }
        )
        return json.dumps(result, indent=2)
