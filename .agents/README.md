# .agents/

Vendor-agnostic agent skills — reusable workflow definitions compatible with Cursor, Claude Code, Codex CLI, Gemini CLI, and other compliant LLM tools.

Skills complement MCP tools by providing **methodology**: which tools to chain, in what order, and what to surface to the user. The MCP server is the **execution layer** (27 tools); a skill is the **playbook layer**. Connecting the server alone gives an agent tools without a playbook; the skill is the playbook.

## Skills

### [`skills/legal-mcp-toolkit/SKILL.md`](skills/legal-mcp-toolkit/SKILL.md)

Teaches an agent the methodology for chaining the Legal MCP Server's 27 tools into eight complete legal workflows:

- **Contract risk triage** — `analyze_clauses` → `generate_negotiation_guide` → surface risk summary
- **Negotiation prep** — clause analysis → `suggest_clause_alternatives` → redline guide
- **Privilege-safe AI review** — `check_privilege_risk` before routing any document to a cloud inference provider
- **Legal research** — `search_precedents` / `search_case_law` / `extract_statute` → synthesize findings
- **Brief drafting** — `generate_brief_outline` → `create_argument_structure` → `generate_issue_statement`
- **Citation cleanup** — `validate_citation` → `normalize_citation` → `verify_citation_integrity`
- **Deep clause analysis** — `deep_analyze_clause` with MCP sampling fallback
- **Batch document analysis** — `queue_document_analysis` → poll `get_analysis_status` → `get_analysis_result`

The skill also encodes non-negotiable rules (never present tool output as legal advice; always surface disclaimers; prefer local tools over live integrations) and agent-readable tool selection logic.

## Standard and compatibility

Skills follow the [Agent Skills open specification](https://agentskills.io/specification.md).
The same `SKILL.md` works unchanged across Claude Code, Cursor, Codex CLI, and Gemini CLI.
Cursor and Codex CLI discover skills under `.agents/skills/` automatically when you open the repository.
For Claude Code, symlink or copy the `legal-mcp-toolkit/` directory into `.claude/skills/`.

## Adding a new skill

1. Create a directory under `.agents/skills/my-skill-name/`.
2. Add a `SKILL.md` with a YAML front matter block (`name`, `description`, `compatibility`) and the workflow methodology in the body.
3. Skills should reference tool names by their exact MCP identifiers (e.g., `search_precedents`) so agents can resolve them at runtime.
