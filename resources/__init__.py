"""MCP resource modules for the Legal MCP Server."""

from __future__ import annotations

from resources.brief_resources import register_brief_resources
from resources.case_resources import register_case_resources
from resources.contract_resources import register_contract_resources
from resources.integration_resources import register_integration_resources
from resources.statute_resources import register_statute_resources


def register_all_resources(mcp) -> None:
    """Register every resource domain with the MCP server."""

    register_case_resources(mcp)
    register_statute_resources(mcp)
    register_contract_resources(mcp)
    register_brief_resources(mcp)
    register_integration_resources(mcp)
