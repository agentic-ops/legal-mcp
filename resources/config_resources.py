"""Server configuration resources (always registered)."""

from __future__ import annotations

import json

from feature_flags import TOOL_CATEGORIES, enabled_categories
from utils import audit


def register_config_resources(mcp) -> None:
    """Register always-on configuration resources."""

    @mcp.resource("legal://server-config")
    def server_config() -> str:
        """Report enabled tool categories and their environment variable names."""
        audit("resource_server_config")
        categories = enabled_categories()
        return json.dumps(
            {
                "enabled_categories": categories,
                "disabled_categories": [
                    name for name, enabled in categories.items() if not enabled
                ],
                "environment_variables": TOOL_CATEGORIES,
                "note": (
                    "All categories default to enabled. Set LEGAL_MCP_ENABLE_*=false "
                    "to disable a category before server startup."
                ),
            },
            indent=2,
        )
