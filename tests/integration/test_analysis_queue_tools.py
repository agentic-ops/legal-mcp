"""Integration tests for the async document analysis queue tools."""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.analysis_queue_tools as aq
from tests.conftest import call_tool_json


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Use a temporary SQLite DB for each test to avoid cross-test contamination."""
    db_path = tmp_path / "test_analysis.db"
    monkeypatch.setattr(aq, "_DB_PATH", db_path)
    yield db_path


class TestAnalysisQueueTools:
    @pytest.mark.asyncio
    async def test_queue_returns_job_id(self, mcp_server, risky_nda_txt):
        payload = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": str(risky_nda_txt)},
        )
        assert "job_id" in payload
        assert len(payload["job_id"]) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_status_is_complete_after_queue(self, mcp_server, risky_nda_txt):
        queued = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": str(risky_nda_txt)},
        )
        job_id = queued["job_id"]
        status_payload = await call_tool_json(
            mcp_server,
            "get_analysis_status",
            {"job_id": job_id},
        )
        assert status_payload["status"] == "complete"

    @pytest.mark.asyncio
    async def test_get_result_contains_analysis(self, mcp_server, risky_nda_txt):
        queued = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": str(risky_nda_txt)},
        )
        job_id = queued["job_id"]
        result = await call_tool_json(
            mcp_server,
            "get_analysis_result",
            {"job_id": job_id},
        )
        assert "overall_risk" in result
        assert result["overall_risk"] == "HIGH"

    @pytest.mark.asyncio
    async def test_list_jobs_includes_queued_job(self, mcp_server, risky_nda_txt):
        queued = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": str(risky_nda_txt), "analysis_notes": "batch run"},
        )
        job_id = queued["job_id"]
        listing = await call_tool_json(mcp_server, "list_analysis_jobs", {})
        job_ids = [j["job_id"] for j in listing["jobs"]]
        assert job_id in job_ids

    @pytest.mark.asyncio
    async def test_missing_job_id_returns_error(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "get_analysis_status",
            {"job_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert "error" in payload

    @pytest.mark.asyncio
    async def test_bad_file_path_sets_error_status(self, mcp_server):
        queued = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": "does/not/exist.docx"},
        )
        job_id = queued["job_id"]
        status_payload = await call_tool_json(
            mcp_server,
            "get_analysis_status",
            {"job_id": job_id},
        )
        assert status_payload["status"] == "error"

    @pytest.mark.asyncio
    async def test_analysis_notes_stored_with_job(self, mcp_server, risky_nda_txt):
        queued = await call_tool_json(
            mcp_server,
            "queue_document_analysis",
            {"file_path": str(risky_nda_txt), "analysis_notes": "priority review"},
        )
        job_id = queued["job_id"]
        status_payload = await call_tool_json(
            mcp_server,
            "get_analysis_status",
            {"job_id": job_id},
        )
        assert status_payload["analysis_notes"] == "priority review"
