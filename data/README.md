# data/

JSON seed data that powers the server offline — no network calls needed.
All data is loaded at startup by `LegalDataManager` in `utils.py` via `get_data_manager()` (a process-wide singleton).
Adding or editing entries here requires **no code changes** — the manager loads everything dynamically.

For live court records and filings, see [`integrations/`](../integrations/).

## Files and directories

| Path | Contents |
|------|----------|
| `cases/cases.json` | Precedent index — each entry has `id`, `name`, `citation`, `court`, `jurisdiction`, `year`, `topics`, `holding`, `summary`, `disposition`, and `cites` (cross-references to other case IDs). Used by `search_precedents`, `search_case_law`, and the `legal://case-database` resource. |
| `statutes/statutes.json` | Statutory materials — each entry has `id`, `title`, `citation`, `jurisdiction`, `topics`, and full text. Used by `extract_statute` and the `legal://statute-library` resource. |
| `contracts/contracts.json` | Contract templates and clause library — 13 templates covering NDAs, MSAs, DPAs, HIPAA BAA, Terms of Use, Privacy Policy, Advisor Agreement, California Offer Letter, Post-Money SAFE, and Cookie Notice. Used by `compare_contracts`, `analyze_clauses`, `extract_clauses`, and the `legal://contract-templates` resource. |
| `citation_standards.json` | Reporter abbreviations and Bluebook citation rules. Used by `CitationParser` in `utils.py` to validate and normalize citations. |
| `templates/brief_frameworks.json` | Brief outline frameworks indexed by case type (e.g., `motion_to_dismiss`, `appellate_brief`). Used by `generate_brief_outline` and the `legal://brief-frameworks` resource. |

## Data schema conventions

- Every top-level object uses a stable string `id` as the dictionary key (e.g., `"smith-v-abc-corp-2022"`).
- Arrays of string tags (e.g., `topics`) are used for keyword search; keep them lowercase.
- Cross-references between entries use `id` strings (e.g., `cites` in cases).

## Extending the data

1. **Add a case:** insert a new entry into `data/cases/cases.json` following the existing schema. The server picks it up on next restart.
2. **Add a statute:** insert into `data/statutes/statutes.json`.
3. **Add a contract template:** insert into `data/contracts/contracts.json`; follow the clause structure used by existing templates so `analyze_clauses` can score it.
4. **Add a brief framework:** insert into `data/templates/brief_frameworks.json` with a unique `id` matching the case type string your tools will pass.

No migrations, no schema files — just well-formed JSON objects following the existing structure.
