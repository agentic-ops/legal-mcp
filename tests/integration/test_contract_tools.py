"""Integration tests for the contract tools."""

from __future__ import annotations

import pytest

from tests.conftest import call_tool_json


class TestContractTools:
    """Integration tests for contract tools."""

    @pytest.mark.asyncio
    async def test_compare_contracts(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "compare_contracts",
            {"contract_a": "NDA_v1", "contract_b": "NDA_v2"},
        )
        assert payload["difference_count"] >= 1
        clauses = {d["clause"]: d for d in payload["differences"]}
        assert "confidentiality_scope" in clauses
        assert clauses["confidentiality_scope"]["status"] == "modified"
        # The client NDA adds an uncapped indemnification clause (HIGH risk).
        assert clauses["indemnification"]["risk_level"] == "HIGH"

    @pytest.mark.asyncio
    async def test_compare_contracts_missing(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "compare_contracts",
            {"contract_a": "NDA_v1", "contract_b": "nope"},
        )
        assert "error" in payload
        assert "nope" in payload["missing"]

    @pytest.mark.asyncio
    async def test_analyze_clauses(self, mcp_server):
        payload = await call_tool_json(
            mcp_server, "analyze_clauses", {"contract_id": "client_proposed_nda"}
        )
        assert payload["overall_risk"] == "HIGH"
        assert "indemnification" in payload["clause_analysis"]

    @pytest.mark.asyncio
    async def test_extract_clauses(self, mcp_server):
        payload = await call_tool_json(
            mcp_server, "extract_clauses", {"contract_id": "standard_nda_template"}
        )
        assert payload["clause_count"] >= 1
        assert "confidentiality_scope" in payload["clauses"]
