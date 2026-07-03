"""Pytest configuration and shared fixtures for the Legal MCP Server."""

from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from main import create_server
from utils import CitationParser, LegalDataManager


@pytest.fixture(scope="session")
def data_manager() -> LegalDataManager:
    """A LegalDataManager backed by the repository's seed data."""

    return LegalDataManager()


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


@pytest.fixture(scope="session")
def mcp_server():
    """A fully-registered FastMCP server instance for integration tests."""

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
