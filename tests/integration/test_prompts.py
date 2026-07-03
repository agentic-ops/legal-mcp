"""Integration tests for MCP prompts."""

from __future__ import annotations

import pytest


async def _prompt_text(server, name, arguments):
    result = await server.get_prompt(name, arguments)
    return " ".join(
        m.content.text for m in result.messages if hasattr(m.content, "text")
    )


class TestPrompts:
    """Integration tests for MCP prompts."""

    @pytest.mark.asyncio
    async def test_prompts_are_registered(self, mcp_server):
        prompts = await mcp_server.list_prompts()
        names = {p.name for p in prompts}
        assert {
            "precedent_analysis",
            "statutory_interpretation",
            "brief_construction",
            "contract_review",
        }.issubset(names)

    @pytest.mark.asyncio
    async def test_research_prompt_interpolates_argument(self, mcp_server):
        text = await _prompt_text(
            mcp_server, "precedent_analysis", {"case_facts": "delivery timing"}
        )
        assert "delivery timing" in text

    @pytest.mark.asyncio
    async def test_drafting_prompt_generates_text(self, mcp_server):
        text = await _prompt_text(
            mcp_server, "brief_construction", {"case_type": "contract_breach"}
        )
        assert "contract_breach" in text
