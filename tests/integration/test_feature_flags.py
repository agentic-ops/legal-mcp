"""Integration tests for category-level feature flags."""

from __future__ import annotations

import pytest

from main import create_server
from tests.conftest import read_resource_json


class TestFeatureFlagRegistration:
    @pytest.mark.asyncio
    async def test_default_server_registers_analysis_queue_tools(self):
        server = create_server()
        tools = await server.list_tools()
        names = {tool.name for tool in tools}
        assert "queue_document_analysis" in names
        assert "deep_analyze_clause" in names

    @pytest.mark.asyncio
    async def test_disabled_category_excludes_tools(self, monkeypatch):
        monkeypatch.setenv("LEGAL_MCP_ENABLE_ANALYSIS_QUEUE", "false")
        monkeypatch.setenv("LEGAL_MCP_ENABLE_CONTRACT", "false")
        server = create_server()
        tools = await server.list_tools()
        names = {tool.name for tool in tools}
        assert "queue_document_analysis" not in names
        assert "deep_analyze_clause" not in names
        assert "analyze_document" in names

    @pytest.mark.asyncio
    async def test_server_config_reports_disabled_categories(self, monkeypatch):
        monkeypatch.setenv("LEGAL_MCP_ENABLE_PRIVILEGE", "false")
        server = create_server()
        payload = await read_resource_json(server, "legal://server-config")
        assert payload["enabled_categories"]["privilege"] is False
        assert "privilege" in payload["disabled_categories"]
        assert (
            payload["environment_variables"]["privilege"]
            == "LEGAL_MCP_ENABLE_PRIVILEGE"
        )
