"""Integration tests for deep clause analysis via MCP sampling."""

from __future__ import annotations

import json

import pytest
from mcp import types
from mcp.shared.memory import create_connected_server_and_client_session

from main import create_server
from tests.conftest import call_tool_json


async def _stub_sampling(_context, _params):
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Stub LLM analysis: consider adding a mutual liability cap.",
        ),
        model="stub-model",
    )


class TestDeepAnalyzeClause:
    @pytest.mark.asyncio
    async def test_fallback_when_sampling_unavailable(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "deep_analyze_clause",
            {
                "clause_text": (
                    "Recipient shall indemnify without limitation of liability."
                ),
                "clause_type": "indemnification",
            },
        )
        assert payload["llm_reasoning"] is None
        assert payload["heuristic_analysis"]["risk_level"] == "HIGH"
        assert "does not support LLM sampling" in payload["note"]
        assert "not legal advice" in payload["disclaimer"].lower()

    @pytest.mark.asyncio
    async def test_sampling_path_populates_llm_reasoning(self):
        server = create_server()
        async with create_connected_server_and_client_session(
            server,
            sampling_callback=_stub_sampling,
            client_info=types.Implementation(name="test-client", version="1.0"),
        ) as client:
            result = await client.call_tool(
                "deep_analyze_clause",
                {
                    "clause_text": (
                        "Liability shall be unlimited without limitation of liability."
                    ),
                    "clause_type": "limitation_of_liability",
                },
            )
            payload = json.loads(result.content[0].text)
        assert payload["llm_reasoning"] == (
            "Stub LLM analysis: consider adding a mutual liability cap."
        )
        assert payload["heuristic_analysis"]["risk_level"] == "HIGH"

    @pytest.mark.asyncio
    async def test_disabled_contract_category_hides_tool(self, monkeypatch):
        monkeypatch.setenv("LEGAL_MCP_ENABLE_CONTRACT", "false")
        server = create_server()
        tools = await server.list_tools()
        names = {tool.name for tool in tools}
        assert "deep_analyze_clause" not in names
