"""MCP resource modules for the Legal MCP Server."""

from __future__ import annotations

from feature_flags import is_category_enabled
from resources.brief_resources import register_brief_resources
from resources.case_resources import register_case_resources
from resources.config_resources import register_config_resources
from resources.contract_resources import register_contract_resources
from resources.integration_resources import register_integration_resources
from resources.statute_resources import register_statute_resources


def register_all_resources(mcp) -> None:
    """Register every enabled resource domain with the MCP server."""

    register_config_resources(mcp)
    if is_category_enabled("research"):
        register_case_resources(mcp)
        register_statute_resources(mcp)
    if is_category_enabled("contract"):
        register_contract_resources(mcp)
    if is_category_enabled("brief"):
        register_brief_resources(mcp)
    if is_category_enabled("integrations"):
        register_integration_resources(mcp)
