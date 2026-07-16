# resources/

MCP resource implementations — static and queryable data endpoints exposed as `legal://` URIs.
Resources are read-only. Bundled case, statute, and contract resources require
explicit `LEGAL_MCP_DEMO_MODE=true`; otherwise they remain registered and
return `demo_data_disabled`. Citation standards and brief frameworks remain
available in production mode.
Every handler returns a `json.dumps(..., indent=2)` string and calls `audit(...)`.

## Modules and URI schemes

| Module | URIs exposed |
|--------|-------------|
| `config_resources.py` | `legal://server-config` — feature-flag status for every tool category (always registered, never gated) |
| `case_resources.py` | `legal://case-database` — full precedent index; `legal://case/{case_id}/analysis` — per-case detail and analysis |
| `statute_resources.py` | `legal://statute-library` — statutory materials index; `legal://statute/{statute_id}/context` — statute text with legislative context |
| `contract_resources.py` | `legal://contract-templates` — contract/template index; `legal://contract/{contract_id}/differ` — template detail |
| `brief_resources.py` | `legal://brief-frameworks` — brief outline templates index; `legal://brief/{brief_id}/outline` — framework detail |
| `integration_resources.py` | `legal://integrations` — live-integration status (booleans only; credentials never echoed) |
| `__init__.py` | `register_all_resources(mcp)` — wires every enabled resource module into the FastMCP instance |

## The `legal://server-config` resource

This resource is **always registered** regardless of feature flags.
It returns the enabled/disabled state of every tool category so clients can discover what is available without calling any tools.
Use it to audit the server configuration at runtime:

```
legal://server-config  →  { "demo_mode": false, "enabled_categories": { ... } }
```

The response also reports the `LEGAL_MCP_DEMO_MODE` environment-variable name.

## Registration

`register_all_resources(mcp)` in `__init__.py` is called from `main.py`.
`config_resources` is registered unconditionally; all others are gated by the same `is_category_enabled()` flags that gate their matching tools.

## Adding a new resource

1. Create `resources/my_resources.py` with a `register_my_resources(mcp)` function.
2. Decorate each resource with `@mcp.resource("legal://my-uri")` (static) or `@mcp.resource("legal://my-uri/{param}")` (template).
3. Return `json.dumps(..., indent=2)` and call `audit(...)`.
4. Import and call `register_my_resources(mcp)` from `resources/__init__.py` inside the appropriate feature-flag guard.

```python
# resources/my_resources.py
import json
from utils import audit, get_data_manager

def register_my_resources(mcp):
    data = get_data_manager()

    @mcp.resource("legal://my-index")
    def my_index() -> str:
        """My resource index."""
        audit("resource_my_index")
        return json.dumps({"items": list(data.my_data.keys())}, indent=2)
```
