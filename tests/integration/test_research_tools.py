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


class TestResearchLegalIssue:
    @pytest.mark.asyncio
    async def test_returns_local_results_when_cl_disabled(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {
                "issue": "contract breach delivery timing",
                "jurisdiction": "CA",
            },
        )
        assert payload["case_result_count"] >= 1
        assert payload["cases"][0]["source"] == "demo_seed"
        assert payload["courtlistener_status"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_includes_statutes_when_flag_true(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {
                "issue": "reasonable time contract performance",
                "jurisdiction": "CA",
                "include_statutes": True,
            },
        )
        assert payload["statutes"] is not None
        assert len(payload["statutes"]) >= 1

    @pytest.mark.asyncio
    async def test_excludes_statutes_when_flag_false(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {
                "issue": "reasonable time contract performance",
                "include_statutes": False,
            },
        )
        assert payload["statutes"] is None

    @pytest.mark.asyncio
    async def test_cl_results_merged_when_mock_enabled(self, mcp_server, monkeypatch):
        import httpx

        from integrations.config import CourtListenerSettings
        from integrations.courtlistener import CourtListenerClient

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "results": [
                        {
                            "caseName": "Mock v. Example",
                            "citation": "999 F.3d 111",
                        }
                    ],
                },
            )

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        settings = CourtListenerSettings(enabled=True, api_token="secret-token")

        def mock_client(*args, **kwargs):
            return CourtListenerClient(settings, http_client=http_client)

        monkeypatch.setattr(
            "tools.research_tools.CourtListenerClient",
            mock_client,
        )
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {"issue": "contract breach"},
        )
        sources = {case["source"] for case in payload["cases"]}
        assert "courtlistener" in sources

    @pytest.mark.asyncio
    async def test_results_annotated_with_source(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {"issue": "material breach"},
        )
        assert all(case["source"] == "demo_seed" for case in payload["cases"])
        assert all(case["authoritative"] is False for case in payload["cases"])

    @pytest.mark.asyncio
    async def test_no_duplicates_across_sources(self, mcp_server, monkeypatch):
        import httpx

        from integrations.config import CourtListenerSettings
        from integrations.courtlistener import CourtListenerClient

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "results": [
                        {
                            "caseName": "Smith v. ABC Corp",
                            "citation": "2022 Cal.App.4th 1234",
                        }
                    ],
                },
            )

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        settings = CourtListenerSettings(enabled=True, api_token="secret-token")

        def mock_client(*args, **kwargs):
            return CourtListenerClient(settings, http_client=http_client)

        monkeypatch.setattr(
            "tools.research_tools.CourtListenerClient",
            mock_client,
        )
        payload = await call_tool_json(
            mcp_server,
            "research_legal_issue",
            {
                "issue": "contract breach delivery timing",
                "jurisdiction": "CA",
            },
        )
        citations = [
            case.get("citation")
            for case in payload["cases"]
            if case.get("citation") == "2022 Cal.App.4th 1234"
        ]
        assert len(citations) == 1
