"""MCP tool modules for the Legal MCP Server."""

from __future__ import annotations

from tools.brief_tools import register_brief_tools
from tools.citation_tools import register_citation_tools
from tools.contract_tools import register_contract_tools
from tools.document_tools import register_document_tools
from tools.integration_tools import register_integration_tools
from tools.research_tools import register_research_tools


def register_all_tools(mcp) -> None:
    """Register every tool category with the MCP server."""

    register_research_tools(mcp)
    register_citation_tools(mcp)
    register_contract_tools(mcp)
    register_document_tools(mcp)
    register_brief_tools(mcp)
    register_integration_tools(mcp)
