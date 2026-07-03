# Legal MCP Server — Research, Paralegal & Workflow Automation

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for
structured legal workflows. This **legal MCP server** provides tools, resources,
and prompts for precedent retrieval, statute analysis, citation validation,
contract clause comparison, and guided brief scaffolding — all backed by
inspectable, deterministic local data and optional (opt‑in) live legal databases.

> **This server provides legal‑workflow augmentation, not legal advice.** It
> does not replace attorney review and judgment.

- **Status:** V1 — implemented and tested.
- **Transport:** stdio, SSE, and streamable‑HTTP (via FastMCP).
- **Runtime:** Python 3.10+ and the official `mcp` SDK.

---

## ⚠️ PACER and paid‑database fees (read first)

**If you connect this MCP (or an AI assistant using it) to PACER or other paid
legal databases, you are responsible for all charges incurred on your
account.** PACER bills per page, per document, or per search. AI agents can
issue many requests in minutes; in real‑world testing a short (~10 minute)
agent session nearly exhausted a standard PACER account's **$30 per quarter**
fee waiver.

To protect you from surprise fees, **every live integration in this server is
disabled by default** and must be explicitly enabled with a feature flag and
credentials (see [Live integrations](#-live-integrations-pacer--courtlistenerrecap)).
Prefer the free **CourtListener / RECAP** source over PACER wherever possible.

For official PACER billing rules, see [pacer.gov](https://pacer.gov).

---

## 🚀 Quick start

```bash
# 1. Install dependencies (uses your user site-packages; a venv also works)
pip install -r requirements.txt

# 2. Run the server (SSE transport on http://127.0.0.1:8000/sse by default)
python main.py

# 3. (Optional) Explore it in the MCP Inspector
npx @modelcontextprotocol/inspector
#    In the Inspector: Transport = SSE, URL = http://127.0.0.1:8000/sse, Connect.
```

Run over a different transport:

```bash
python main.py --transport stdio            # for Claude Desktop / CLI clients
python main.py --transport streamable-http  # modern HTTP transport
python main.py --transport sse --port 9000  # custom port
```

All flags also read from environment variables: `MCP_TRANSPORT`, `HOST`,
`PORT`, `LOG_LEVEL`.

### Use it with the MCP CLI / Inspector directly

The server exposes a module‑level `mcp` object, so you can load it with the
MCP CLI:

```bash
mcp dev main.py:mcp     # launches the Inspector wired to this server
mcp run main.py:mcp     # runs the server via the CLI
```

---

## 🧰 Capabilities

### Tools (14)

| Category | Tool | Purpose |
| --- | --- | --- |
| Research | `search_precedents` | Keyword‑ranked precedent search over local cases |
| Research | `search_case_law` | Case‑law search with relevance ranking and summaries |
| Research | `extract_statute` | Statute text with optional legislative context |
| Citation | `validate_citation` | Validate structure and reporter; return issues |
| Citation | `normalize_citation` | Normalize spacing + Bluebook‑style abbreviations |
| Citation | `verify_citation_integrity` | Cross‑check a citation against the case database |
| Contract | `compare_contracts` | Clause‑level differ with risk flags |
| Contract | `analyze_clauses` | Rule‑based clause risk analysis |
| Contract | `extract_clauses` | Template‑filtered clause extraction |
| Brief | `generate_brief_outline` | Outline from a brief framework by case type |
| Brief | `create_argument_structure` | IRAC‑style argument scaffold |
| Brief | `generate_issue_statement` | Issue‑statement framework from facts + law |
| Integrations | `integration_status` | Report which live sources are enabled/configured |
| Integrations | `search_live_case_law` | Query CourtListener/RECAP or PACER (when enabled) |

### Resources

Static:

- `legal://case-database` — precedent index
- `legal://statute-library` — statutory materials index
- `legal://contract-templates` — contract/template index
- `legal://brief-frameworks` — brief outline templates
- `legal://citation-standards` — reporter + Bluebook reference data
- `legal://integrations` — live‑integration status (feature flags/config)

Dynamic templates:

- `legal://case/{case_id}/analysis`
- `legal://statute/{statute_id}/context`
- `legal://contract/{contract_id}/differ`
- `legal://brief/{brief_id}/outline`

### Prompts (8)

`precedent_analysis`, `statutory_interpretation`, `brief_construction`,
`argument_development`, `contract_review`, `clause_comparison`,
`citation_validation`, `authority_integration`.

See [`WORKFLOW_EXAMPLES.md`](WORKFLOW_EXAMPLES.md) for end‑to‑end workflow
walkthroughs.

---

## 🔌 Live integrations (PACER & CourtListener/RECAP)

Live legal databases are **optional and disabled by default**. Each is
controlled by a **feature flag** plus **API credentials**, all supplied via
environment variables. Check the current state at any time:

```bash
# via the tool
search_live_case_law / integration_status
# or the resource
legal://integrations
```

`integration_status` and the `legal://integrations` resource return only
booleans and non‑sensitive metadata — **credentials are never echoed back**.

### CourtListener / RECAP (Free Law Project) — free, preferred

CourtListener exposes a free, rate‑limited [REST API
(v4)](https://www.courtlistener.com/help/api/rest/) that also serves the
[RECAP Archive](https://free.law/recap/) of PACER documents. Authentication is
an `Authorization: Token <token>` header.

| Variable | Default | Description |
| --- | --- | --- |
| `COURTLISTENER_ENABLED` | `false` | Feature flag to enable the integration |
| `COURTLISTENER_API_TOKEN` | _(unset)_ | Token from your CourtListener profile |
| `COURTLISTENER_BASE_URL` | `https://www.courtlistener.com/api/rest/v4` | Override for testing |

```bash
export COURTLISTENER_ENABLED=true
export COURTLISTENER_API_TOKEN="your-token-here"   # https://www.courtlistener.com/profile/api/
python main.py
```

### PACER (federal court records) — paid, off by default

PACER uses a two‑step flow described in the
[PACER Authentication API User Guide](https://pacer.uscourts.gov/help/pacer/pacer-authentication-api-user-guide):

1. **Authenticate** — `POST {auth}/services/cso-auth` with your `loginId` and
   `password` (and optional client code / TOTP passcode). Returns a
   `nextGenCSO` token.
2. **Search** — reuse the `nextGenCSO` token as a cookie against the PACER
   Case Locator (PCL) API.

Per PACER guidance the token is **reused** across requests (the client caches
it); it does not re‑authenticate on every call.

| Variable | Default | Description |
| --- | --- | --- |
| `PACER_ENABLED` | `false` | Feature flag to enable the integration |
| `PACER_ENVIRONMENT` | `qa` | `qa` (non‑billable test) or `production` (billable) |
| `PACER_LOGIN_ID` | _(unset)_ | PACER username |
| `PACER_PASSWORD` | _(unset)_ | PACER password |
| `PACER_CLIENT_CODE` | _(unset)_ | Optional client/billing code |
| `PACER_OTP_SECRET` | _(unset)_ | Optional base32 TOTP secret if 2FA is enabled |

```bash
export PACER_ENABLED=true
export PACER_ENVIRONMENT=qa          # start with the non-billable QA env
export PACER_LOGIN_ID="your-username"
export PACER_PASSWORD="your-password"
python main.py
```

> Register for a **non‑billable QA account** at
> [qa-pacer.uscourts.gov](https://qa-pacer.uscourts.gov) to test safely.
> Production accounts are billable. See the
> [developer resources](https://pacer.uscourts.gov/file-case/developer-resources).

Copy [`.env.example`](.env.example) to `.env` for a template of all settings.

---

## 🐳 Docker (optional)

```bash
# Build and run over SSE at http://localhost:8000/sse
docker compose up --build
```

Enable integrations by exporting variables (or using a `.env` file next to
`docker-compose.yml`) before `docker compose up`:

```bash
COURTLISTENER_ENABLED=true COURTLISTENER_API_TOKEN=... docker compose up --build
```

Or with plain Docker:

```bash
docker build -t legal-mcp .
docker run --rm -p 8000:8000 \
  -e COURTLISTENER_ENABLED=true -e COURTLISTENER_API_TOKEN=... \
  legal-mcp
```

---

## 🍴 Forking & building your own (LLM‑friendly)

This project is designed to be forked and extended, including by AI coding
assistants:

- **Predictable structure.** Tools live in `tools/`, resources in
  `resources/`, prompts in `prompts/`, integrations in `integrations/`, and
  all seed data in `data/`. Each module exposes a `register_*` function and is
  wired up centrally (`tools/__init__.py`, `resources/__init__.py`,
  `prompts/__init__.py`).
- **Deterministic + offline by default.** No hidden network calls; live
  sources are opt‑in.
- **[`AGENTS.md`](AGENTS.md)** documents how to run, test, and extend the
  server so an agent can navigate the repo quickly.

### Add a new tool

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

Then call `register_my_tools(mcp)` from `tools/__init__.py`. Resources and
prompts follow the same pattern with `@mcp.resource(uri)` and `@mcp.prompt()`.

---

## 🏗️ Architecture

```
legal-mcp/
├── main.py                 # FastMCP server entry point (exposes `mcp`)
├── utils.py                # LegalDataManager + CitationParser + audit log
├── tools/                  # MCP tools (research, citation, contract, brief, integrations)
├── resources/              # MCP resources (case, statute, contract, brief, integrations)
├── prompts/                # MCP prompts (research, drafting, analysis, argument)
├── integrations/           # Optional live sources (config, courtlistener, pacer)
├── data/                   # Seed data (cases, statutes, contracts, templates, citations)
├── tests/                  # Unit + integration tests
├── Dockerfile              # Optional container image
├── docker-compose.yml      # Optional compose setup
└── requirements.txt        # Dependencies
```

The server initializes a `FastMCP` instance, registers all tools, resources,
and prompts, logs an audit trail, and runs the selected transport.

---

## 🧪 Testing, linting & types

```bash
pip install -r requirements.txt

pytest                 # run the full unit + integration suite
pytest --cov=. --cov-report=term-missing

python -m black .      # format
python -m flake8 .     # lint
python -m mypy .       # type-check
```

Integration tests exercise tools, resources, and prompts through the
in‑memory FastMCP API. The live integrations are tested with an
`httpx.MockTransport` so **no real network calls** are made.

> If the `pytest`, `black`, etc. scripts are not on your `PATH` after a
> `pip install --user`, invoke them via `python -m <tool>` as shown above.

---

## 🔐 Legal & compliance notes

- **Audit trails.** Every tool/resource call emits a structured audit log
  entry (`utils.audit`).
- **Deterministic core.** Local data operations are reproducible and make no
  hidden network calls.
- **Opt‑in external data.** PACER and CourtListener are disabled until you
  enable them; PACER may incur fees.
- **Not legal advice.** Output is a scaffold for attorney review.

## 📖 Further reading

- [Model Context Protocol](https://modelcontextprotocol.io)
- [CourtListener API](https://www.courtlistener.com/help/api/rest/) ·
  [RECAP](https://free.law/recap/)
- [PACER developer resources](https://pacer.uscourts.gov/file-case/developer-resources)

## 💬 Integration & development support

Need help integrating this legal MCP server into your practice workflows,
enabling the PACER or CourtListener/RECAP adapters, or building custom law MCP
tools and extensions? Professional integration and development support is
available.

- **Email:** [edwin@genego.io](mailto:edwin@genego.io)
- **LinkedIn:** [Edwin Genego](https://www.linkedin.com/in/edwin-genego/)

We're happy to help with deployment, custom integrations, and tailored legal
workflow automation.

## 📝 License

[GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).

Free to use, fork, and self-host. If you run a modified version as a network
service, AGPL-3.0 requires you to publish your changes. Organizations that
need to keep modifications private can contact
[edwin@genego.io](mailto:edwin@genego.io) for a commercial license.
