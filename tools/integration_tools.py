"""Tools for optional live legal-data integrations (CourtListener, PACER).

These tools expose the feature-flagged integrations to MCP clients. They
are safe to call even when integrations are disabled: in that case they
return a clear status payload and make no network requests.
"""

from __future__ import annotations

import json
from typing import Optional

from integrations import (
    CourtListenerClient,
    PacerClient,
    get_integration_settings,
)
from utils import audit


def register_integration_tools(mcp) -> None:
    """Register live-integration tools with the MCP server."""

    @mcp.tool()
    def integration_status() -> str:
        """Report which live integrations are enabled/configured.

        Reads the current feature flags and credential presence. Never
        returns secret values -- only booleans and non-sensitive metadata.
        """
        audit("integration_status")
        settings = get_integration_settings()
        report = {
            "courtlistener": CourtListenerClient(settings.courtlistener).status(),
            "pacer": PacerClient(settings.pacer).status(),
        }
        return json.dumps(report, indent=2)

    @mcp.tool()
    def search_live_case_law(
        query: str,
        source: str = "courtlistener",
        jurisdiction: Optional[str] = None,
    ) -> str:
        """Search a live legal database when the integration is enabled.

        ``source`` is either ``courtlistener`` (free, preferred) or
        ``pacer`` (paid; may incur fees). Disabled by default -- returns a
        status payload explaining how to enable the integration.
        """
        audit("search_live_case_law", query=query, source=source)
        settings = get_integration_settings()
        if source == "pacer":
            result = PacerClient(settings.pacer).search(query, jurisdiction)
        elif source == "courtlistener":
            result = CourtListenerClient(settings.courtlistener).search(query)
        else:
            result = {
                "error": f"Unknown source '{source}'.",
                "valid_sources": ["courtlistener", "pacer"],
            }
        return json.dumps(result, indent=2)
