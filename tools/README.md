# tools/

MCP tool implementations — the callable functions exposed to LLM clients.
Every tool accepts structured JSON arguments, returns a `json.dumps(..., indent=2)` string, and calls `audit(...)` for provenance.

## Modules

| Module | What it provides |
|--------|-----------------|
| `research_tools.py` | `search_precedents`, `search_case_law`, `extract_statute`, `research_legal_issue` — opt-in demo search plus explicitly enabled live research |
| `citation_tools.py` | `validate_citation`, `normalize_citation`, `check_demo_database` — citation formatting plus clearly labeled demo lookup |
| `contract_tools.py` | `compare_contracts`, `analyze_clauses`, `extract_clauses`, `suggest_clause_alternatives`, `generate_negotiation_guide` — real clause helpers plus opt-in sample-template workflows |
| `deep_analysis_tools.py` | `deep_analyze_clause` — keyword heuristics plus optional MCP LLM sampling for deeper clause reasoning; falls back gracefully when the client lacks sampling support |
| `document_tools.py` | `analyze_document`, `compare_documents`, `export_analysis_report`, `extract_contract_metadata` — risk analysis for real `.docx`/`.txt` files |
| `brief_tools.py` | `generate_brief_outline`, `create_argument_structure`, `generate_issue_statement` — IRAC-scaffolded brief drafting |
| `privilege_tools.py` | `check_privilege_risk` — assesses AI-routing risk for potentially privileged documents; references *Heppner* and ABA Rule 1.6 |
| `analysis_queue_tools.py` | `queue_document_analysis`, `get_analysis_status`, `get_analysis_result`, `list_analysis_jobs` — async local analysis job queue |
| `integration_tools.py` | `integration_status`, `search_live_case_law` — live CourtListener/RECAP and PACER search (feature-flag gated) |
| `risk_helpers.py` | Internal helpers `assess_clause_risk` and `find_missing_clauses` shared across contract and document tools; not exposed as MCP tools |
| `__init__.py` | `register_all_tools(mcp)` — wires every enabled category into the FastMCP instance |

## Registration

`register_all_tools(mcp)` in `__init__.py` is the single entry point called from `main.py`.
Each category is gated by a feature flag from `feature_flags.py`:

```python
if is_category_enabled("contract"):
    register_contract_tools(mcp)
    register_deep_analysis_tools(mcp)
```

All categories are **enabled by default**. Set `LEGAL_MCP_ENABLE_<CATEGORY>=false` to skip a category at startup.
See [`feature_flags.py`](../feature_flags.py) and the main [`README.md`](../README.md#feature-flags-tool-categories) for the full flag reference.

Bundled cases, statutes, and sample contracts are independently gated by
`LEGAL_MCP_DEMO_MODE`, which defaults to `false`. Seed-dependent tools remain
registered in production mode and return the stable `demo_data_disabled`
payload.

## Adding a new tool

1. Create `tools/my_tools.py` with a `register_my_tools(mcp)` function.
2. Decorate each tool with `@mcp.tool()` and return `json.dumps(..., indent=2)`.
3. Call `audit("my_tool", ...)` at the top of every tool for the provenance log.
4. Import and call `register_my_tools(mcp)` from `tools/__init__.py` (inside the appropriate feature-flag guard, or unconditionally if it needs no flag).
5. Add integration tests under `tests/integration/test_my_tools.py` using the `mcp_server` fixture from `tests/conftest.py`.

```python
# tools/my_tools.py
import json
from utils import audit, get_data_manager

def register_my_tools(mcp):
    data = get_data_manager()

    @mcp.tool()
    def my_tool(param: str) -> str:
        """Describe the legal intent clearly."""
        audit("my_tool", param=param)
        return json.dumps({"result": param}, indent=2)
```
