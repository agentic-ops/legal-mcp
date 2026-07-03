"""Integration tests for the research tools."""

from __future__ import annotations

import pytest

from tests.conftest import call_tool_json


class TestResearchTools:
    """Integration tests for research tools."""

    @pytest.mark.asyncio
    async def test_search_precedents(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "search_precedents",
            {"query": "contract breach delivery timing", "jurisdiction": "CA"},
        )
        assert payload["result_count"] >= 1
        names = [r["name"] for r in payload["results"]]
        assert "Smith v. ABC Corp" in names

    @pytest.mark.asyncio
    async def test_search_case_law_includes_summary(self, mcp_server):
        payload = await call_tool_json(
            mcp_server, "search_case_law", {"query": "material breach"}
        )
        assert payload["result_count"] >= 1
        assert "summary" in payload["results"][0]

    @pytest.mark.asyncio
    async def test_extract_statute(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "extract_statute",
            {"statute_id": "Cal.Civ.Code.1657", "context": True},
        )
        assert payload["citation"] == "Cal. Civ. Code \u00a7 1657"
        assert "reasonable time" in payload["text"].lower()
        assert payload["context"]["enacted"] == "1872"

    @pytest.mark.asyncio
    async def test_extract_statute_not_found(self, mcp_server):
        payload = await call_tool_json(
            mcp_server, "extract_statute", {"statute_id": "does.not.exist"}
        )
        assert "error" in payload
