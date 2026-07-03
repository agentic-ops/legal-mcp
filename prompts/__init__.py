"""Central prompt registration for the Legal MCP Server."""

from __future__ import annotations

from prompts.analysis_prompts import register_analysis_prompts
from prompts.argument_prompts import register_argument_prompts
from prompts.drafting_prompts import register_drafting_prompts
from prompts.research_prompts import register_research_prompts


def register_all_prompts(mcp) -> None:
    """Register all prompt categories with the MCP server."""

    register_research_prompts(mcp)
    register_drafting_prompts(mcp)
    register_analysis_prompts(mcp)
    register_argument_prompts(mcp)
