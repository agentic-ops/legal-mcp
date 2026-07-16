# prompts/

MCP prompt implementations — structured workflow templates that guide LLM clients through multi-step legal tasks.

**Prompts vs. tools:** tools are executable actions that return data; prompts are guidance templates that tell an LLM *how* to approach a task and *which tools to chain*. They are returned to the client as message sequences, not executed server-side.

## Modules and prompts

| Module | Prompts |
|--------|---------|
| `research_prompts.py` | `precedent_analysis` — step-by-step guide for researching and applying case precedents; `statutory_interpretation` — framework for reading a statute's text, structure, and legislative history |
| `drafting_prompts.py` | `brief_construction` — scaffolded workflow for drafting a legal brief from issue to conclusion; `clause_comparison` — structured approach to comparing contract clause alternatives |
| `analysis_prompts.py` | `contract_review` — risk-triage workflow for full contract analysis using `analyze_clauses` and `generate_negotiation_guide`; `citation_validation` — formatting cleanup plus authoritative source-checking workflow |
| `argument_prompts.py` | `argument_development` — IRAC-based argument scaffold for motions and briefs; `authority_integration` — methodology for weaving case law and statutes into a coherent argument |
| `__init__.py` | `register_all_prompts(mcp)` — wires all four prompt modules into the FastMCP instance |

## The 8 prompts at a glance

| Prompt name | One-line description |
|-------------|---------------------|
| `precedent_analysis` | Research and apply relevant case precedents to a legal issue |
| `statutory_interpretation` | Interpret a statute using text, structure, and legislative history |
| `brief_construction` | Scaffold a complete legal brief from issue statement to conclusion |
| `clause_comparison` | Compare contract clause alternatives and select the lower-risk option |
| `contract_review` | Full contract risk triage with negotiation guidance |
| `citation_validation` | Format and normalize citations, then route existence and good-law checks to authoritative sources |
| `argument_development` | Build an IRAC-structured argument for a motion or brief |
| `authority_integration` | Integrate case law and statutes into a coherent legal argument |

## Registration

`register_all_prompts(mcp)` in `__init__.py` is called unconditionally from `main.py` — prompts are not gated by feature flags.

## Adding a new prompt

1. Create `prompts/my_prompts.py` with a `register_my_prompts(mcp)` function.
2. Decorate each prompt with `@mcp.prompt()` and return a list of `Message` objects (or a string that FastMCP wraps automatically).
3. Import and call `register_my_prompts(mcp)` from `prompts/__init__.py`.

```python
# prompts/my_prompts.py
def register_my_prompts(mcp):

    @mcp.prompt()
    def my_workflow(context: str) -> str:
        """Guide the LLM through a custom legal workflow."""
        return (
            f"You are analyzing: {context}\n"
            "Step 1: Call search_precedents to find relevant cases.\n"
            "Step 2: Call extract_statute for applicable statutes.\n"
            "Step 3: Synthesize findings and surface the disclaimer."
        )
```
