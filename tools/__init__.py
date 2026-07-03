"""MCP tool modules for the Legal MCP Server."""

from __future__ import annotations

from feature_flags import is_category_enabled
from tools.analysis_queue_tools import register_analysis_queue_tools
from tools.brief_tools import register_brief_tools
from tools.citation_tools import register_citation_tools
from tools.contract_tools import register_contract_tools
from tools.deep_analysis_tools import register_deep_analysis_tools
from tools.document_tools import register_document_tools
from tools.integration_tools import register_integration_tools
from tools.privilege_tools import register_privilege_tools
from tools.research_tools import register_research_tools


def register_all_tools(mcp) -> None:
    """Register every enabled tool category with the MCP server."""

    if is_category_enabled("research"):
        register_research_tools(mcp)
    if is_category_enabled("citation"):
        register_citation_tools(mcp)
    if is_category_enabled("contract"):
        register_contract_tools(mcp)
        register_deep_analysis_tools(mcp)
    if is_category_enabled("document"):
        register_document_tools(mcp)
    if is_category_enabled("brief"):
        register_brief_tools(mcp)
    if is_category_enabled("integrations"):
        register_integration_tools(mcp)
    if is_category_enabled("privilege"):
        register_privilege_tools(mcp)
    if is_category_enabled("analysis_queue"):
        register_analysis_queue_tools(mcp)
