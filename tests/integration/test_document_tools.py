"""Integration tests for document ingestion and export tools."""

from __future__ import annotations

import json

import pytest
from docx import Document

from tests.conftest import call_tool_json


class TestAnalyzeDocument:
    @pytest.mark.asyncio
    async def test_analyze_docx_returns_risk_flags(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_docx)},
        )
        assert payload["overall_risk"] == "HIGH"
        assert payload["clause_count"] >= 1

    @pytest.mark.asyncio
    async def test_analyze_docx_detects_indemnification(
        self, mcp_server, risky_nda_docx
    ):
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_docx)},
        )
        flagged = any(
            "indemnif" in flag.get("trigger", "")
            for entry in payload["clause_analysis"].values()
            for flag in entry.get("flags", [])
        )
        assert flagged

    @pytest.mark.asyncio
    async def test_analyze_txt_file(self, mcp_server, risky_nda_txt):
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_txt)},
        )
        assert payload["overall_risk"] == "HIGH"

    @pytest.mark.asyncio
    async def test_analyze_document_not_found(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": "does/not/exist.docx"},
        )
        assert "error" in payload

    @pytest.mark.asyncio
    async def test_analyze_document_includes_missing_clauses(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_docx), "contract_type": "NDA"},
        )
        assert "missing_clauses" in payload
        assert isinstance(payload["missing_clauses"], list)

    @pytest.mark.asyncio
    async def test_analyze_document_contract_type_filters_missing_topics(
        self, mcp_server, tmp_path
    ):
        doc_path = tmp_path / "minimal_msa.txt"
        doc_path.write_text(
            "Scope of Services: Provider shall perform services.\n\n"
            "Governing Law: This Agreement shall be governed by the laws of Delaware.",
            encoding="utf-8",
        )
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(doc_path), "contract_type": "MSA"},
        )
        assert "term" in payload["missing_clauses"]
        assert "liab" in payload["missing_clauses"]

    @pytest.mark.asyncio
    async def test_analyze_document_unsupported_format(
        self, mcp_server, tmp_path
    ):
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        payload = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(pdf_path)},
        )
        assert "error" in payload
        assert "Unsupported" in payload["error"]


class TestCompareDocuments:
    @pytest.mark.asyncio
    async def test_compare_finds_differences(
        self, mcp_server, risky_nda_docx, clean_nda_docx
    ):
        payload = await call_tool_json(
            mcp_server,
            "compare_documents",
            {
                "file_path_a": str(risky_nda_docx),
                "file_path_b": str(clean_nda_docx),
            },
        )
        assert payload["difference_count"] >= 1

    @pytest.mark.asyncio
    async def test_compare_identical_files(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "compare_documents",
            {
                "file_path_a": str(risky_nda_docx),
                "file_path_b": str(risky_nda_docx),
            },
        )
        assert payload["difference_count"] == 0

    @pytest.mark.asyncio
    async def test_compare_missing_file(self, mcp_server, risky_nda_docx):
        payload = await call_tool_json(
            mcp_server,
            "compare_documents",
            {
                "file_path_a": str(risky_nda_docx),
                "file_path_b": "missing.docx",
            },
        )
        assert "error" in payload


class TestExportAnalysisReport:
    @pytest.mark.asyncio
    async def test_export_creates_docx_file(
        self, mcp_server, risky_nda_docx, tmp_path
    ):
        analysis = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_docx)},
        )
        output_path = tmp_path / "analysis_report.docx"
        payload = await call_tool_json(
            mcp_server,
            "export_analysis_report",
            {
                "analysis_json": json.dumps(analysis),
                "output_path": str(output_path),
            },
        )
        assert output_path.exists()
        assert payload["output_path"] == str(output_path)

    @pytest.mark.asyncio
    async def test_export_docx_contains_risk_summary(
        self, mcp_server, risky_nda_docx, tmp_path
    ):
        analysis = await call_tool_json(
            mcp_server,
            "analyze_document",
            {"file_path": str(risky_nda_docx)},
        )
        output_path = tmp_path / "analysis_report.docx"
        await call_tool_json(
            mcp_server,
            "export_analysis_report",
            {
                "analysis_json": json.dumps(analysis),
                "output_path": str(output_path),
            },
        )
        document = Document(str(output_path))
        headings = [paragraph.text for paragraph in document.paragraphs]
        assert "Risk Summary" in headings
        assert "Disclaimer" in headings

    @pytest.mark.asyncio
    async def test_export_nonexistent_analysis_json(self, mcp_server, tmp_path):
        payload = await call_tool_json(
            mcp_server,
            "export_analysis_report",
            {
                "analysis_json": "{not valid json",
                "output_path": str(tmp_path / "bad.docx"),
            },
        )
        assert "error" in payload


class TestExtractContractMetadata:
    @pytest.mark.asyncio
    async def test_extracts_governing_law_from_docx(self, mcp_server, tmp_path):
        doc_path = tmp_path / "test_gov_law.txt"
        doc_path.write_text(
            "This Agreement is entered into between Acme Inc. and Vendor Corp.\n\n"
            "Governing Law: This Agreement shall be governed by the laws of Delaware.",
            encoding="utf-8",
        )
        payload = await call_tool_json(
            mcp_server,
            "extract_contract_metadata",
            {"file_path": str(doc_path)},
        )
        assert payload.get("governing_law") is not None
        assert "Delaware" in payload["governing_law"]

    @pytest.mark.asyncio
    async def test_extracts_numeric_liability_cap(self, mcp_server, tmp_path):
        doc_path = tmp_path / "test_cap.txt"
        doc_path.write_text(
            "Limitation of Liability: Each party's aggregate liability shall not "
            "exceed $500,000 in any twelve-month period.",
            encoding="utf-8",
        )
        payload = await call_tool_json(
            mcp_server,
            "extract_contract_metadata",
            {"file_path": str(doc_path)},
        )
        assert payload.get("liability_cap_usd") == 500000

    @pytest.mark.asyncio
    async def test_missing_fields_return_null_not_error(self, mcp_server, tmp_path):
        doc_path = tmp_path / "test_minimal.txt"
        doc_path.write_text("This is a simple agreement with minimal content.", encoding="utf-8")
        payload = await call_tool_json(
            mcp_server,
            "extract_contract_metadata",
            {"file_path": str(doc_path)},
        )
        assert "error" not in payload
        # Missing fields should be null, not absent or erroring
        assert "governing_law" in payload
        assert "effective_date" in payload

    @pytest.mark.asyncio
    async def test_parties_extracted_from_nda(self, mcp_server, tmp_path):
        doc_path = tmp_path / "test_nda_meta.txt"
        doc_path.write_text(
            "This Non-Disclosure Agreement is entered into between Acme Inc. "
            "('Discloser') and Vendor Corp. ('Recipient') as of January 1, 2026.\n\n"
            "Confidentiality: Recipient shall hold all information in confidence.",
            encoding="utf-8",
        )
        payload = await call_tool_json(
            mcp_server,
            "extract_contract_metadata",
            {"file_path": str(doc_path)},
        )
        parties = payload.get("parties") or []
        all_names = " ".join(parties)
        assert "Acme" in all_names or "Vendor" in all_names

    @pytest.mark.asyncio
    async def test_missing_file_returns_error(self, mcp_server):
        payload = await call_tool_json(
            mcp_server,
            "extract_contract_metadata",
            {"file_path": "does/not/exist.docx"},
        )
        assert "error" in payload
