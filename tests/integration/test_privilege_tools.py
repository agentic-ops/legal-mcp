"""Integration tests for the privilege risk assessment tool."""

from __future__ import annotations

import pytest

from tests.conftest import call_tool_json


class TestCheckPrivilegeRisk:
    @pytest.mark.asyncio
    async def test_unknown_provider_returns_high_risk(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {
                "file_path": str(risky_nda_docx),
                "inference_provider": "unknown",
                "counsel_directed": False,
            },
        )
        assert payload["privilege_risk"] in ("HIGH", "CRITICAL")

    @pytest.mark.asyncio
    async def test_ollama_returns_low_risk(self, mcp_server, tmp_path):
        doc_path = tmp_path / "simple.txt"
        doc_path.write_text(
            "Scope of Services: Provider shall deliver software services.",
            encoding="utf-8",
        )
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {
                "file_path": str(doc_path),
                "inference_provider": "ollama",
                "counsel_directed": False,
            },
        )
        assert payload["privilege_risk"] in ("LOW", "MEDIUM")

    @pytest.mark.asyncio
    async def test_counsel_directed_lowers_risk_level(self, mcp_server, risky_nda_docx):
        without_counsel = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {
                "file_path": str(risky_nda_docx),
                "inference_provider": "unknown",
                "counsel_directed": False,
            },
        )
        with_counsel = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {
                "file_path": str(risky_nda_docx),
                "inference_provider": "unknown",
                "counsel_directed": True,
            },
        )
        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        assert order[with_counsel["privilege_risk"]] <= order[without_counsel["privilege_risk"]]

    @pytest.mark.asyncio
    async def test_result_includes_heppner_note(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {"file_path": str(risky_nda_docx), "inference_provider": "openai"},
        )
        assert "heppner_note" in payload
        assert "Heppner" in payload["heppner_note"]

    @pytest.mark.asyncio
    async def test_result_includes_aba_rule(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {"file_path": str(risky_nda_docx), "inference_provider": "anthropic"},
        )
        assert "aba_rule" in payload
        assert "1.6" in payload["aba_rule"]

    @pytest.mark.asyncio
    async def test_missing_file_returns_error(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {
                "file_path": "does/not/exist.docx",
                "inference_provider": "openai",
            },
        )
        assert "error" in payload

    @pytest.mark.asyncio
    async def test_provider_posture_included_in_result(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "check_privilege_risk",
            {"file_path": str(risky_nda_docx), "inference_provider": "azure_openai"},
        )
        assert "provider_posture" in payload
        assert payload["provider_posture"]["hipaa_baa"] is True
