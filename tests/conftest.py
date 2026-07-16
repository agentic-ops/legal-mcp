"""Pytest configuration and shared fixtures for the Legal MCP Server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from main import create_server
from tests.fixtures import RISKY_NDA_TEXT, build_clean_nda_docx, build_risky_nda_docx
from utils import CitationParser, LegalDataManager


@pytest.fixture(scope="session")
def data_manager() -> LegalDataManager:
    """A LegalDataManager backed by the repository's seed data."""

    return LegalDataManager(demo_mode=True)


@pytest.fixture(scope="session")
def parser(data_manager: LegalDataManager) -> CitationParser:
    """A CitationParser using the seed citation standards."""

    return CitationParser(data_manager)


@pytest.fixture
def sample_legal_data(data_manager: LegalDataManager) -> Dict[str, Any]:
    """Sample legal data for testing."""

    return {
        "cases": data_manager.cases,
        "statutes": data_manager.statutes,
        "contracts": data_manager.contracts,
    }


@pytest.fixture
def mcp_server(monkeypatch):
    """A demo-enabled FastMCP server for legacy seed-data integration tests."""

    monkeypatch.setenv("LEGAL_MCP_DEMO_MODE", "true")
    return create_server()


@pytest.fixture
def production_mcp_server(monkeypatch):
    """A production-default FastMCP server with demo content disabled."""

    monkeypatch.delenv("LEGAL_MCP_DEMO_MODE", raising=False)
    return create_server()


async def call_tool_json(server, name: str, arguments: Dict[str, Any]) -> Any:
    """Call an MCP tool and decode its JSON string payload."""

    result = await server.call_tool(name, arguments)
    structured = result[1] if isinstance(result, tuple) else result
    return json.loads(structured["result"])


async def read_resource_json(server, uri: str) -> Any:
    """Read an MCP resource and decode its JSON string payload."""

    contents = await server.read_resource(uri)
    first = list(contents)[0]
    text = getattr(first, "content", None) or getattr(first, "text", first)
    return json.loads(text)


@pytest.fixture(scope="session")
def risky_nda_docx(tmp_path_factory) -> Path:
    """A .docx NDA containing known HIGH-risk clauses."""

    path = tmp_path_factory.mktemp("documents") / "risky_nda.docx"
    return build_risky_nda_docx(path)


@pytest.fixture(scope="session")
def clean_nda_docx(tmp_path_factory) -> Path:
    """A .docx NDA with lower-risk language for comparison testing."""

    path = tmp_path_factory.mktemp("documents") / "clean_nda.docx"
    return build_clean_nda_docx(path)


@pytest.fixture(scope="session")
def risky_nda_txt(tmp_path_factory) -> Path:
    """Same risky clause text saved as .txt for format-agnostic testing."""

    path = tmp_path_factory.mktemp("documents") / "risky_nda.txt"
    path.write_text(RISKY_NDA_TEXT, encoding="utf-8")
    return path
