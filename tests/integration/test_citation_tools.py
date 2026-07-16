"""Integration tests for the citation tools."""

from __future__ import annotations

import pytest

from tests.conftest import call_tool_json


class TestCitationTools:
    """Integration tests for citation tools."""

    @pytest.mark.asyncio
    async def test_validate_citation(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "validate_citation",
            {"citation": "Smith v. ABC Corp, 2022 Cal.App.4th 1234"},
        )
        assert payload["valid"] is True
        assert payload["components"]["volume"] == 2022

    @pytest.mark.asyncio
    async def test_normalize_citation(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "normalize_citation",
            {"citation": "Johnson v. XYZ Industries, 2020 Cal.4th 567"},
        )
        assert "Indus." in payload["normalized"]

    @pytest.mark.asyncio
    async def test_check_demo_database_found(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "check_demo_database",
            {"citation": "2022 Cal.App.4th 1234"},
        )
        assert list(payload)[0] == "warning"
        assert payload["found_in_demo_database"] is True
        assert payload["matched_demo_case"]["name"] == "Smith v. ABC Corp"
        assert "found_in_database" not in payload

    @pytest.mark.asyncio
    async def test_check_demo_database_missing(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "check_demo_database",
            {"citation": "999 U.S. 999"},
        )
        assert list(payload)[0] == "warning"
        assert payload["found_in_demo_database"] is False
