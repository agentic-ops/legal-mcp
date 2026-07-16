---
name: legal-mcp-toolkit
description: >-
  Teaches an agent the methodology for chaining the Legal MCP Server's 27
  tools into complete legal workflows — contract risk triage, negotiation
  prep, privilege-safe AI review, legal research, brief drafting, citation
  cleanup, deep clause analysis, and batch document analysis. Use whenever the
  Legal MCP Server is connected and the user asks to review or compare a
  contract, negotiate terms, research case law or statutes, draft a brief or
  motion, validate citations, check whether a document is safe to send through
  an AI provider, run deep clause reasoning, or process a batch of documents.
compatibility: Requires the Legal MCP Server (this repository) connected as an MCP server.
---

# Legal MCP Toolkit

The Legal MCP Server gives an agent 27 tools (research, citation, contract,
document, privilege, brief, analysis-queue, integrations). Tools are the
**execution layer** — this skill is the **methodology layer**: which tools to
call, in what order, and what to surface to the user. It does not replace
attorney judgment; every workflow ends with a disclaimer, not a conclusion.

## Non-negotiable rules

1. **Never present tool output as legal advice.** Every contract/document/
   negotiation/privilege tool response includes a disclaimer field
   (`notice`, `disclaimer`, or similar) — always surface it to the user.
2. **Never treat demo content as authority.** Bundled cases, statutes, and
   contracts require `LEGAL_MCP_DEMO_MODE=true` and every response is labeled
   demo-only. Use them for demonstrations, never to verify a real citation.
3. **Prefer CourtListener over PACER** when a live source is genuinely
   needed — PACER bills per page/search and is disabled by default for a
   reason.
4. **Real files over seed IDs when a file exists.** If the user has an
   actual `.docx`/`.txt` contract, use `analyze_document` /
   `compare_documents` / `extract_contract_metadata`, not the seed-data
   `compare_contracts` (which only works on template IDs like
   `standard_nda_template`).
5. **Check privilege before routing to a non-local AI provider.** If a
   document looks privileged (attorney-client communication, work product,
   litigation strategy) and the user plans to paste it into a general AI
   chatbot, run `check_privilege_risk` first and surface the result before
   proceeding.
6. **Respect feature flags.** Categories can be disabled via `LEGAL_MCP_ENABLE_*`
   env vars. If a tool is missing, read `legal://server-config` before
   assuming the server is broken.

## Tool quick reference

| Category | Tools |
| --- | --- |
| Research | `search_precedents`, `search_case_law`, `extract_statute`, `research_legal_issue` |
| Citation | `validate_citation`, `normalize_citation`, `check_demo_database` |
| Contract | `compare_contracts`, `analyze_clauses`, `extract_clauses`, `suggest_clause_alternatives`, `generate_negotiation_guide`, `deep_analyze_clause` |
| Document | `analyze_document`, `compare_documents`, `export_analysis_report`, `extract_contract_metadata` |
| Privilege | `check_privilege_risk` |
| Brief | `generate_brief_outline`, `create_argument_structure`, `generate_issue_statement` |
| Analysis Queue | `queue_document_analysis`, `get_analysis_status`, `get_analysis_result`, `list_analysis_jobs` |
| Integrations | `integration_status`, `search_live_case_law` |

Full descriptions: [README.md § Capabilities](../../../README.md#-capabilities).
Full worked examples for every workflow below: [WORKFLOW_EXAMPLES.md](../../../WORKFLOW_EXAMPLES.md).

## Workflow patterns

Pick the pattern that matches the user's request, then follow its tool
sequence. Patterns can be combined (e.g., negotiation prep often follows
contract risk triage).

### 1. Contract risk triage
**Trigger:** "review this contract", "what's risky here", "compare these two NDAs"

1. Real file → `analyze_document(file_path)`. Seed template → `analyze_clauses(contract_id)`.
2. Two versions to diff → `compare_documents` (files) or `compare_contracts` (template IDs).
3. Risky clause needs rewording → `suggest_clause_alternatives(clause_text, clause_type)`.
4. Deeper reasoning needed → `deep_analyze_clause(clause_text, clause_type)` (uses MCP sampling when the client supports it; otherwise returns heuristics only).
5. Deliverable needed → `export_analysis_report(analysis_json, output_path)`.

### 2. Negotiation prep
**Trigger:** "we're the buyer/seller, what should we push back on", "negotiation guide"

1. `generate_negotiation_guide(contract_id, party_role, focus_areas?)` — `party_role`
   must be `buyer`, `seller`, or `mutual`; it flips the recommended position on the
   same clause.
2. Surface `recommended_position` (accept/negotiate/reject) with `rationale` and
   `fallback_text` per clause. Lead with HIGH-risk clauses.
3. If the contract is a real file rather than a seed ID, run `analyze_document`
   first and paraphrase the negotiation logic manually — `generate_negotiation_guide`
   only accepts contract IDs from the template library.

### 3. Contract metadata lookup
**Trigger:** "what's the governing law/term/liability cap in this contract"

1. `extract_contract_metadata(file_path)` — pure regex extraction, not legal judgment.
2. Fields not found return `null`; don't guess on the agent's behalf — tell the
   user which fields need manual confirmation (see `confidence_notes`).

### 4. Privilege-safe AI review
**Trigger:** "can I paste this into ChatGPT/Claude", "is this privileged", document
mentions attorney-client communications or litigation strategy

1. `check_privilege_risk(file_path, inference_provider, counsel_directed)`.
2. `inference_provider` options with known postures: `ollama`, `azure_openai`,
   `vertex_ai`, `openrouter`, `openai`, `anthropic` (default `unknown` = worst case).
3. On `HIGH`/`CRITICAL`, tell the user not to proceed without attorney
   authorization; suggest `ollama` (local, zero data retention) as the lower-risk
   alternative rather than silently downgrading the risk yourself.

### 5. Legal research
**Trigger:** "find precedents for...", "what does this statute say", "research this issue"

1. Read `legal://server-config` to determine whether demo content is active;
   never present demo results as real authority.
2. Use `research_legal_issue` or `search_live_case_law` for real case-law
   research after confirming live integrations are enabled (`integration_status`).
3. Use `validate_citation` only for structure/reporter-format checks. Confirm
   existence and good-law status through an authoritative live source and
   attorney review.

### 6. Brief / motion drafting
**Trigger:** "draft a motion", "outline this brief", "argument structure"

1. `generate_brief_outline(case_type, motion_type, jurisdiction)` for the skeleton.
2. `create_argument_structure` for IRAC-style argument scaffolding per section.
3. `generate_issue_statement` to frame the question presented from facts + law.
4. Fill in authorities using the research pattern above before finalizing.

### 7. Citation cleanup
**Trigger:** "check these citations", "format to Bluebook"

1. `validate_citation` to catch structural issues.
2. `normalize_citation` to apply Bluebook-style spacing/abbreviations.
3. If demo mode is intentionally active, `check_demo_database` can show whether
   a citation appears in the sample dataset. A match is not verification that
   the case exists or remains good law.

### 8. Batch / async document analysis
**Trigger:** "queue these contracts for review", "analyze this batch overnight"

1. `queue_document_analysis(file_path, analysis_notes)` per file — returns a `job_id`
   immediately (analysis runs inline; status is `complete` or `error` right away
   in the current implementation, but always poll rather than assume).
2. `get_analysis_status(job_id)` / `get_analysis_result(job_id)` to check and retrieve.
3. `list_analysis_jobs()` to give the user a full batch summary.
4. This queue is a **local AI job store**, not a submission to human reviewers —
   don't imply a human will review queued jobs unless the user has a separate
   attorney-review process.

## Response shape

For every workflow, close with:
- The disclaimer text verbatim from the tool response (don't paraphrase it away).
- Concrete next steps (route to counsel, re-run with different parameters, file
  the export, etc.) — mirror the "Next Steps" pattern used in
  [WORKFLOW_EXAMPLES.md](../../../WORKFLOW_EXAMPLES.md).
