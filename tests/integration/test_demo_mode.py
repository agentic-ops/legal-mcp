"""Production-default and explicit demo-mode safety contracts."""

from __future__ import annotations

import logging

import pytest

from main import create_server
from tests.conftest import call_tool_json, read_resource_json
from utils import get_data_manager


GATED_TOOL_CALLS = [
    ("search_precedents", {"query": "contract breach"}),
    ("search_case_law", {"query": "contract breach"}),
    ("extract_statute", {"statute_id": "Cal.Civ.Code.1657"}),
    ("check_demo_database", {"citation": "2022 Cal.App.4th 1234"}),
    ("compare_contracts", {"contract_a": "NDA_v1", "contract_b": "NDA_v2"}),
    ("analyze_clauses", {"contract_id": "standard_nda_template"}),
    ("extract_clauses", {"contract_id": "standard_nda_template"}),
    (
        "generate_negotiation_guide",
        {"contract_id": "standard_nda_template", "party_role": "buyer"},
    ),
]

GATED_RESOURCES = [
    "legal://case-database",
    "legal://case/smith-v-abc-corp-2022/analysis",
    "legal://statute-library",
    "legal://statute/Cal.Civ.Code.1657/context",
    "legal://contract-templates",
    "legal://contract/standard_nda_template/differ",
]


class TestProductionMode:
    @pytest.mark.asyncio
    async def test_full_tool_catalog_remains_registered(self, production_mcp_server):
        names = {tool.name for tool in await production_mcp_server.list_tools()}
        assert "check_demo_database" in names
        assert "verify_citation_integrity" not in names
        assert {name for name, _ in GATED_TOOL_CALLS}.issubset(names)
        assert "analyze_document" in names
        assert "search_live_case_law" in names

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("tool_name", "arguments"), GATED_TOOL_CALLS)
    async def test_gated_tools_return_stable_unavailable_payload(
        self, production_mcp_server, tool_name, arguments
    ):
        payload = await call_tool_json(production_mcp_server, tool_name, arguments)
        assert payload["data_mode"] == "production"
        assert payload["available"] is False
        assert payload["error"] == "demo_data_disabled"
        serialized = str(payload)
        assert "Smith v. ABC Corp" not in serialized
        assert "standard_nda_template" not in serialized

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uri", GATED_RESOURCES)
    async def test_gated_resources_return_stable_unavailable_payload(
        self, production_mcp_server, uri
    ):
        payload = await read_resource_json(production_mcp_server, uri)
        assert payload["data_mode"] == "production"
        assert payload["available"] is False
        assert payload["error"] == "demo_data_disabled"

    @pytest.mark.asyncio
    async def test_aggregate_reports_no_source_when_live_is_disabled(
        self, production_mcp_server
    ):
        payload = await call_tool_json(
            production_mcp_server,
            "research_legal_issue",
            {"issue": "contract breach"},
        )
        assert payload["data_mode"] == "production"
        assert payload["available"] is False
        assert payload["error"] == "no_research_source_enabled"
        assert payload["cases"] == []
        assert payload["statutes"] == []
        assert payload["demo_data_included"] is False

    @pytest.mark.asyncio
    async def test_aggregate_uses_explicitly_enabled_live_source_without_demo_data(
        self, production_mcp_server, monkeypatch
    ):
        import httpx

        from integrations.config import CourtListenerSettings
        from integrations.courtlistener import CourtListenerClient

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "results": [
                        {"caseName": "Real Source Result", "citation": "1 F.4th 2"}
                    ],
                },
            )

        settings = CourtListenerSettings(enabled=True, api_token="test-token")
        monkeypatch.setenv("COURTLISTENER_ENABLED", "true")
        monkeypatch.setenv("COURTLISTENER_API_TOKEN", "test-token")
        client = CourtListenerClient(
            settings,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
        monkeypatch.setattr(
            "tools.research_tools.CourtListenerClient", lambda *_: client
        )

        payload = await call_tool_json(
            production_mcp_server,
            "research_legal_issue",
            {"issue": "contract breach"},
        )
        assert payload["data_mode"] == "production"
        assert payload["available"] is True
        assert payload["demo_data_included"] is False
        assert payload["cases"][0]["source"] == "courtlistener"
        assert payload["cases"][0]["verification_required"] is True

    @pytest.mark.asyncio
    async def test_server_config_reports_demo_default(self, production_mcp_server):
        payload = await read_resource_json(
            production_mcp_server, "legal://server-config"
        )
        assert payload["demo_mode"] is False
        assert payload["demo_mode_environment_variable"] == "LEGAL_MCP_DEMO_MODE"


class TestDemoMode:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool_name", "arguments"),
        GATED_TOOL_CALLS
        + [
            ("extract_statute", {"statute_id": "missing"}),
            ("check_demo_database", {"citation": "999 U.S. 999"}),
            ("analyze_clauses", {"contract_id": "missing"}),
        ],
    )
    async def test_demo_tool_payloads_start_with_warning(
        self, mcp_server, tool_name, arguments
    ):
        payload = await call_tool_json(mcp_server, tool_name, arguments)
        assert list(payload)[0] == "warning"
        assert payload["data_mode"] == "demo"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "uri",
        GATED_RESOURCES
        + [
            "legal://case/missing/analysis",
            "legal://statute/missing/context",
            "legal://contract/missing/differ",
        ],
    )
    async def test_demo_resource_payloads_start_with_warning(self, mcp_server, uri):
        payload = await read_resource_json(mcp_server, uri)
        assert list(payload)[0] == "warning"
        assert payload["data_mode"] == "demo"

    @pytest.mark.asyncio
    async def test_aggregate_marks_demo_results_non_authoritative(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {"issue": "contract breach", "include_statutes": True},
        )
        assert list(payload)[0] == "warning"
        assert payload["demo_data_included"] is True
        for result in payload["cases"] + payload["statutes"]:
            assert result["source"] == "demo_seed"
            assert result["authoritative"] is False


def test_data_manager_cache_is_keyed_by_mode(monkeypatch):
    monkeypatch.delenv("LEGAL_MCP_DEMO_MODE", raising=False)
    production = get_data_manager()
    monkeypatch.setenv("LEGAL_MCP_DEMO_MODE", "true")
    demo = get_data_manager()
    assert production is not demo
    assert production.cases == {}
    assert demo.cases


def test_startup_logs_production_mode(monkeypatch, caplog):
    monkeypatch.delenv("LEGAL_MCP_DEMO_MODE", raising=False)
    with caplog.at_level(logging.INFO, logger="legal_mcp"):
        create_server()
    assert "Production mode active" in caplog.text


def test_startup_logs_demo_warning(monkeypatch, caplog):
    monkeypatch.setenv("LEGAL_MCP_DEMO_MODE", "true")
    with caplog.at_level(logging.WARNING, logger="legal_mcp"):
        create_server()
    assert "DEMO MODE ENABLED" in caplog.text
