"""Integration tests for MCP resources (static and dynamic)."""

from __future__ import annotations

import pytest

from tests.conftest import read_resource_json


class TestResources:
    """Integration tests for MCP resources."""

    @pytest.mark.asyncio
    async def test_static_case_database(self, mcp_server):
        payload = await read_resource_json(mcp_server, "legal://case-database")
        assert payload["count"] >= 1
        assert any(c["name"] == "Smith v. ABC Corp" for c in payload["cases"])

    @pytest.mark.asyncio
    async def test_static_contract_templates(self, mcp_server):
        payload = await read_resource_json(mcp_server, "legal://contract-templates")
        ids = [t["id"] for t in payload["templates"]]
        assert "standard_nda_template" in ids

    @pytest.mark.asyncio
    async def test_static_citation_standards(self, mcp_server):
        payload = await read_resource_json(mcp_server, "legal://citation-standards")
        assert payload["format"] == "bluebook"
        assert "Cal.App.4th" in payload["reporters"]

    @pytest.mark.asyncio
    async def test_dynamic_case_analysis(self, mcp_server):
        payload = await read_resource_json(
            mcp_server, "legal://case/smith-v-abc-corp-2022/analysis"
        )
        assert payload["name"] == "Smith v. ABC Corp"
        assert "cited_authorities" in payload

    @pytest.mark.asyncio
    async def test_dynamic_statute_context(self, mcp_server):
        payload = await read_resource_json(
            mcp_server, "legal://statute/Cal.Civ.Code.1657/context"
        )
        assert payload["title"] == "Reasonable Time"
