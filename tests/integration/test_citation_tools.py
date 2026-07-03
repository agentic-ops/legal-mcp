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
    async def test_verify_citation_integrity_found(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "verify_citation_integrity",
            {"citation": "2022 Cal.App.4th 1234"},
        )
        assert payload["found_in_database"] is True
        assert payload["matched_case"]["name"] == "Smith v. ABC Corp"

    @pytest.mark.asyncio
    async def test_verify_citation_integrity_missing(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "verify_citation_integrity",
            {"citation": "999 U.S. 999"},
        )
        assert payload["found_in_database"] is False
