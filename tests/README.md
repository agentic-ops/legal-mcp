# tests/

pytest test suite — unit tests for pure logic and integration tests that exercise tools, resources, and prompts through the in-memory FastMCP API.

## Running the tests

```bash
# Full suite (recommended)
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# A single file
python -m pytest tests/integration/test_contract_tools.py -v
```

> If `pytest` is not on your PATH after a `pip install --user`, use `python -m pytest` as shown above.

## Directory structure

```
tests/
├── conftest.py           # Shared fixtures and helpers (see below)
├── fixtures/             # Reusable test data builders (RISKY_NDA_TEXT, build_*_docx helpers)
├── unit/                 # Pure-logic tests — no server, no I/O
│   ├── test_utils.py     # LegalDataManager and CitationParser unit tests
│   ├── test_risk_helpers.py   # assess_clause_risk and find_missing_clauses
│   └── test_feature_flags.py  # Feature flag env-var parsing
└── integration/          # Full-stack tests using the in-memory FastMCP server
    ├── test_research_tools.py
    ├── test_citation_tools.py
    ├── test_contract_tools.py
    ├── test_document_tools.py
    ├── test_privilege_tools.py
    ├── test_analysis_queue_tools.py
    ├── test_deep_analysis_tools.py
    ├── test_prompts.py
    ├── test_resources.py
    ├── test_integrations.py    # Integration adapter tests (httpx mocked)
    └── test_feature_flags.py   # Feature flag gating end-to-end
```

## conftest.py helpers

`conftest.py` provides session-scoped fixtures and two async helper functions used throughout the integration suite:

| Name | Type | Description |
|------|------|-------------|
| `data_manager` | fixture | `LegalDataManager` backed by the repo's seed data |
| `parser` | fixture | `CitationParser` using the seed citation standards |
| `mcp_server` | fixture | Fully-registered `FastMCP` instance (calls `create_server()`) |
| `risky_nda_docx` | fixture | Temp `.docx` NDA with known HIGH-risk clauses |
| `clean_nda_docx` | fixture | Temp `.docx` NDA with lower-risk language |
| `risky_nda_txt` | fixture | Same risky text saved as `.txt` |
| `call_tool_json(server, name, arguments)` | async helper | Calls an MCP tool and decodes its JSON payload |
| `read_resource_json(server, uri)` | async helper | Reads an MCP resource and decodes its JSON payload |

Example integration test:

```python
import pytest
from tests.conftest import call_tool_json

@pytest.mark.asyncio
async def test_my_tool(mcp_server):
    result = await call_tool_json(mcp_server, "my_tool", {"param": "value"})
    assert result["result"] == "value"
```

## Live integrations are always mocked

`integrations/courtlistener.py` and `integrations/pacer.py` use `httpx.MockTransport` in tests.
**No real network calls are made.** Do not add tests that contact live PACER or CourtListener endpoints.
