"""Tests for the optional live integrations (CourtListener, PACER).

These cover the feature-flag gating (disabled / misconfigured / enabled)
without making real network calls. The enabled path uses an httpx
MockTransport so no external requests occur.
"""

from __future__ import annotations

import httpx
import pytest

from integrations import CourtListenerClient, PacerClient
from integrations.config import CourtListenerSettings, PacerSettings
from tests.conftest import call_tool_json, read_resource_json


class TestCourtListenerAdapter:
    def test_disabled_by_default(self):
        client = CourtListenerClient(CourtListenerSettings())
        result = client.search("contract breach")
        assert result["enabled"] is False
        assert result["results"] == []
        assert "disabled" in result["message"].lower()

    def test_enabled_but_missing_token(self):
        client = CourtListenerClient(CourtListenerSettings(enabled=True))
        result = client.search("contract breach")
        assert result["enabled"] is True
        assert result["configured"] is False
        assert "COURTLISTENER_API_TOKEN" in result["missing_settings"]

    def test_enabled_and_configured_uses_token(self):
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["auth"] = request.headers.get("Authorization")
            captured["q"] = request.url.params.get("q")
            return httpx.Response(
                200, json={"count": 1, "results": [{"caseName": "Foo v. Bar"}]}
            )

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        settings = CourtListenerSettings(enabled=True, api_token="secret-token")
        client = CourtListenerClient(settings, http_client=http_client)

        result = client.search("qualified immunity", result_type="o")
        assert captured["auth"] == "Token secret-token"
        assert captured["q"] == "qualified immunity"
        assert result["result_count"] == 1
        assert result["results"][0]["caseName"] == "Foo v. Bar"


class TestPacerAdapter:
    def test_disabled_by_default(self):
        client = PacerClient(PacerSettings())
        result = client.search("acme corp")
        assert result["enabled"] is False
        assert result["environment"] == "qa"
        assert result["results"] == []

    def test_enabled_but_missing_credentials(self):
        client = PacerClient(PacerSettings(enabled=True))
        result = client.search("acme corp")
        assert result["enabled"] is True
        assert "PACER_LOGIN_ID" in result["missing_settings"]

    def test_enabled_authenticates_then_searches(self):
        calls = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(str(request.url))
            if request.url.path.endswith("/cso-auth"):
                return httpx.Response(
                    200, json={"loginResult": "0", "nextGenCSO": "T" * 128}
                )
            return httpx.Response(
                200, json={"content": [{"caseTitle": "United States v. Acme"}]}
            )

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        settings = PacerSettings(
            enabled=True, login_id="user", password="pass", environment="qa"
        )
        client = PacerClient(settings, http_client=http_client)

        result = client.search("Acme")
        assert any("cso-auth" in url for url in calls)
        assert any("cases/find" in url for url in calls)
        assert result["result_count"] == 1
        assert result["results"][0]["caseTitle"] == "United States v. Acme"


class TestIntegrationToolsAndResources:
    @pytest.mark.asyncio
    async def test_integration_status_tool(self, mcp_server):
        payload = await call_tool_json(mcp_server, "integration_status", {})
        assert payload["courtlistener"]["enabled"] is False
        assert payload["pacer"]["enabled"] is False
        # Status must never leak secret values.
        assert "api_token" not in payload["courtlistener"]
        assert "password" not in payload["pacer"]

    @pytest.mark.asyncio
    async def test_search_live_case_law_disabled(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "search_live_case_law",
            {"query": "breach", "source": "courtlistener"},
        )
        assert payload["enabled"] is False

    @pytest.mark.asyncio
    async def test_integrations_resource(self, mcp_server):
        payload = await read_resource_json(mcp_server, "legal://integrations")
        assert "courtlistener" in payload
        assert "pacer" in payload
