"""Server configuration resources (always registered)."""

from __future__ import annotations

import json

from demo_mode import DEMO_MODE_ENV, is_demo_mode
from feature_flags import TOOL_CATEGORIES, enabled_categories
from utils import audit


def register_config_resources(mcp) -> None:
    """Register always-on configuration resources."""

    demo_mode = is_demo_mode()

    @mcp.resource("legal://server-config")
    def server_config() -> str:
        """Report enabled tool categories and their environment variable names."""
        audit("resource_server_config")
        categories = enabled_categories()
        return json.dumps(
            {
                "demo_mode": demo_mode,
                "demo_mode_environment_variable": DEMO_MODE_ENV,
                "enabled_categories": categories,
                "disabled_categories": [
                    name for name, enabled in categories.items() if not enabled
                ],
                "environment_variables": TOOL_CATEGORIES,
                "note": (
                    "All categories default to enabled. Set LEGAL_MCP_ENABLE_*=false "
                    "to disable a category before server startup. Bundled sample legal "
                    "content defaults to off and requires LEGAL_MCP_DEMO_MODE=true."
                ),
            },
            indent=2,
        )
