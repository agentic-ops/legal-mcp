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

    @pytest.mark.asyncio
    async def test_analyze_clauses_includes_missing_clauses(self, mcp_server):
        payload = await call_tool_json(
            mcp_server, "analyze_clauses", {"contract_id": "standard_nda_template"}
        )
        assert "missing_clauses" in payload
        assert isinstance(payload["missing_clauses"], list)

    @pytest.mark.asyncio
    async def test_analyze_clauses_filtered_clause_omits_missing_clauses(
        self, mcp_server
    ):
        payload = await call_tool_json(
            mcp_server,
            "analyze_clauses",
            {
                "contract_id": "standard_nda_template",
                "clause_type": "governing_law",
            },
        )
        assert "missing_clauses" not in payload


class TestSuggestClauseAlternatives:
    @pytest.mark.asyncio
    async def test_indemnification_returns_alternatives(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "suggest_clause_alternatives",
            {
                "clause_text": (
                    "Recipient shall indemnify without limitation of liability."
                ),
                "clause_type": "indemnification",
            },
        )
        assert len(payload["alternatives"]) >= 2

    @pytest.mark.asyncio
    async def test_each_alternative_has_required_keys(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "suggest_clause_alternatives",
            {
                "clause_text": "Uncapped liability clause.",
                "clause_type": "limitation_of_liability",
            },
        )
        for alternative in payload["alternatives"]:
            assert "text" in alternative
            assert "risk_level" in alternative
            assert "rationale" in alternative

    @pytest.mark.asyncio
    async def test_limitation_of_liability_alternatives(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "suggest_clause_alternatives",
            {
                "clause_text": "Liability is unlimited.",
                "clause_type": "limitation_of_liability",
            },
        )
        assert payload["alternatives"]
        assert payload["clause_type"] == "limitation_of_liability"

    @pytest.mark.asyncio
    async def test_unknown_clause_type_returns_fallback(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "suggest_clause_alternatives",
            {
                "clause_text": "Some unusual clause.",
                "clause_type": "unknown",
            },
        )
        assert payload["alternatives"]
        assert len(payload["alternatives"]) >= 1

    @pytest.mark.asyncio
    async def test_disclaimer_present_in_all_responses(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "suggest_clause_alternatives",
            {
                "clause_text": "Indemnify forever.",
                "clause_type": "indemnification",
            },
        )
        assert "not legal advice" in payload["notice"].lower()
        assert "not legal advice" in payload["disclaimer"].lower()


class TestGenerateNegotiationGuide:
    @pytest.mark.asyncio
    async def test_buyer_rejects_high_risk_clause(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "client_proposed_nda", "party_role": "buyer"},
        )
        guide = payload["guide"]
        # The client_proposed_nda has an uncapped indemnification clause (HIGH)
        indemnification_entries = [e for e in guide if e["clause"] == "indemnification"]
        assert indemnification_entries, "indemnification clause should appear in guide"
        assert indemnification_entries[0]["recommended_position"] == "reject"

    @pytest.mark.asyncio
    async def test_seller_negotiates_high_risk_clause(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "client_proposed_nda", "party_role": "seller"},
        )
        guide = payload["guide"]
        indemnification_entries = [e for e in guide if e["clause"] == "indemnification"]
        assert indemnification_entries
        assert indemnification_entries[0]["recommended_position"] == "negotiate"

    @pytest.mark.asyncio
    async def test_each_clause_has_required_keys(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "standard_nda_template", "party_role": "buyer"},
        )
        required_keys = {
            "clause",
            "risk_level",
            "recommended_position",
            "rationale",
            "fallback_text",
        }
        for entry in payload["guide"]:
            assert required_keys.issubset(entry.keys()), f"Missing keys in: {entry}"

    @pytest.mark.asyncio
    async def test_focus_areas_filter_output(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {
                "contract_id": "standard_nda_template",
                "party_role": "buyer",
                "focus_areas": ["governing_law"],
            },
        )
        assert payload["clause_count"] == 1
        assert payload["guide"][0]["clause"] == "governing_law"

    @pytest.mark.asyncio
    async def test_disclaimer_present(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "standard_nda_template", "party_role": "mutual"},
        )
        assert "not legal advice" in payload["notice"].lower()
        assert payload["disclaimer"]

    @pytest.mark.asyncio
    async def test_invalid_contract_returns_error(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "nonexistent_contract", "party_role": "buyer"},
        )
        assert "error" in payload

    @pytest.mark.asyncio
    async def test_invalid_party_role_returns_error(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "standard_nda_template", "party_role": "alien"},
        )
        assert "error" in payload

    @pytest.mark.asyncio
    async def test_includes_missing_clauses(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "generate_negotiation_guide",
            {"contract_id": "standard_nda_template", "party_role": "buyer"},
        )
        assert "missing_clauses" in payload
        assert isinstance(payload["missing_clauses"], list)
