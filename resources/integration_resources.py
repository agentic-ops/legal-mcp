"""Resource exposing the status of optional live integrations."""

from __future__ import annotations

import json

from integrations import (
    CourtListenerClient,
    PacerClient,
    get_integration_settings,
)
from utils import audit


def register_integration_resources(mcp) -> None:
    """Register integration-status resources with the MCP server."""

    @mcp.resource("legal://integrations")
    def integrations_status() -> str:
        """Feature-flag and configuration status for live integrations."""
        audit("resource_integrations_status")
        settings = get_integration_settings()
        return json.dumps(
            {
                "courtlistener": CourtListenerClient(settings.courtlistener).status(),
                "pacer": PacerClient(settings.pacer).status(),
            },
            indent=2,
        )
