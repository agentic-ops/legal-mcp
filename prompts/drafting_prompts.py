# Legal Research & Paralegal MCP Server
# Document drafting prompts


def register_drafting_prompts(mcp):
    """Register all drafting prompts with the MCP server"""

    @mcp.prompt()
    def brief_construction(case_type: str = "default") -> str:
        """Structured brief writing framework"""
        return f"""You are an appellate and trial advocacy specialist helping to construct a \
well-structured, persuasive legal brief for a {case_type} matter. Your output must follow \
court formatting rules, lead with the strongest theory, and anticipate opposing arguments.

CASE TYPE: {case_type}

## Workflow

### Step 1 — Research and Authority Gathering
Use `search_briefs(query="{case_type}", court_level)` to:
- Find successful brief frameworks for similar {case_type} cases
- Identify the leading cases, key statutes, and secondary authorities
- Note the court's preference for style, citation format, and argument structure

Use `search_precedents(query, jurisdiction, practice_area)` to build your authority base:
- Locate controlling precedent (mandatory authority)
- Find persuasive authority from sister circuits or other jurisdictions
- Identify cases to distinguish or limit

### Step 2 — Theory of the Case
Before drafting, crystallize one overarching theory of the case for a {case_type} matter:
- State it in a single sentence (the "headline")
- Every argument, fact, and authority must reinforce this theory
- Test the theory against the strongest opposing arguments

### Step 3 — Issue Framing (Questions Presented)
Draft Questions Presented that:
- Assume a favorable answer without being argumentative
- Incorporate the most favorable facts
- Are specific enough to be answerable, broad enough to capture the full issue

### Step 4 — Statement of Facts
Draft a factual narrative that:
- Is scrupulously accurate (cite the record for every fact)
- Strategically emphasizes favorable facts and provides context for unfavorable ones
- Uses vivid, concrete language — tell the story, not just the facts
- Avoids legal conclusions in the facts section

### Step 5 — Argument Construction
For each argument in a {case_type} brief, follow the IRAC+ structure:
1. **Issue** — one-sentence topic sentence stating the legal conclusion
2. **Rule** — state the controlling legal standard precisely, with citation
3. **Application** — apply the rule to the specific facts; be concrete, not abstract
4. **Counter-argument** — acknowledge the strongest opposing argument
5. **Rebuttal** — explain why the opposing argument fails
6. **Conclusion** — restate the relief sought for this argument

Use `validate_citation(citation)` on every citation before finalizing.

### Step 6 — Summary of Argument
Draft a standalone Summary of Argument (typically 1–3 pages) that:
- Can be read independently and persuade a judge who reads nothing else
- Presents the argument roadmap in the order it will appear
- Uses topic sentences that state legal conclusions, not just legal issues

### Step 7 — Relief and Conclusion
State the precise relief requested with the legal basis for each form of relief.

## Output Format

Produce a complete brief outline with the following sections:

1. **Cover / Caption** — [court, parties, case number, brief title]
2. **Table of Contents** (with argument headings)
3. **Table of Authorities** (cases, statutes, secondary sources)
4. **Jurisdictional Statement**
5. **Questions Presented**
6. **Statement of Facts**
7. **Summary of Argument**
8. **Argument** (IRAC+ for each issue, with point headings)
9. **Conclusion / Prayer for Relief**

For each section, provide: (a) the drafted text and (b) a bracketed [DRAFTER NOTE] explaining \
key choices. All citations in Bluebook format. Flag weak arguments "[ASSESS STRENGTH BEFORE \
FILING]".
"""

    @mcp.prompt()
    def argument_development(legal_issue: str = "default") -> str:
        """Legal argument construction and refinement"""
        return f"""You are a legal argumentation specialist helping to develop, stress-test, and \
refine a legal argument on the following issue:

LEGAL ISSUE: {legal_issue}

## Workflow

### Step 1 — Issue Decomposition
Break the legal issue "{legal_issue}" into its component sub-issues:
- Identify threshold questions (jurisdiction, standing, procedural prerequisites)
- Separate legal questions (reviewed de novo) from factual questions (reviewed for clear error)
- Map the logical dependency chain: which sub-issues must be won first?

### Step 2 — Authority Research
For each sub-issue, use `search_precedents(query, jurisdiction, practice_area)`:
- Find the controlling standard of review and burden of proof
- Locate the strongest supporting cases with comparable facts
- Identify adverse authority and flag cases that must be distinguished

Use `get_statute(jurisdiction, statute_name)` for any statutory components of the {legal_issue}.

### Step 3 — Argument Architecture
Select the optimal argument structure:
- **Syllogistic** (Major premise → Minor premise → Conclusion): best for clear rule application
- **Analogical** (This case is like X because…): best when facts closely parallel precedent
- **Policy-based** (The rule should be X because…): use when law is unsettled
- **Structural/textual** (The statute/contract says…): use when text controls

For the {legal_issue}, draft the primary argument using the most appropriate structure, plus \
one alternative argument as a fallback.

### Step 4 — Stress Testing (Devil's Advocate Review)
For each argument:
1. State the best counter-argument an opposing brief would make
2. Identify the weakest factual or legal link in your chain
3. Find cases where courts rejected a similar argument — what distinguished them?
4. Test whether the argument proves too much (would it have unintended consequences?)

### Step 5 — Refinement
Revise arguments based on the stress test:
- Narrow overboard claims
- Add limiting principles to policy arguments
- Strengthen factual anchors for analogical arguments
- Add parenthetical explanations to distinguish adverse cases

### Step 6 — Citation Validation
Run `validate_citation(citation)` on all cited authorities for structure and reporter
formatting only. Separately use an authoritative citator or live legal-data source to
confirm that no overruled or negatively treated cases are cited as good law and that
pinpoint citations support the stated propositions.

### Step 7 — Argument Brief Checklist
Before finalizing, verify:
- [ ] Each argument has a controlling authority or compelling policy rationale
- [ ] The standard of review is correctly stated and applied
- [ ] Every factual assertion is record-supported
- [ ] Adverse authority is addressed, not ignored
- [ ] Relief requested is legally available and clearly stated

## Output Format

1. **Issue Map** — visual tree of issue → sub-issues → threshold questions
2. **Primary Argument** — full IRAC+ draft with citations
3. **Alternative Argument** — condensed fallback argument
4. **Stress-Test Report** — top 3 counter-arguments with rebuttals
5. **Authority Inventory** — supporting cases | adverse cases | statutes | secondary sources
6. **Argument Refinement Notes** — what was changed and why
7. **Checklist Sign-off** — completed pre-submission checklist

Mark arguments with uncertain legal support "[AUTHORITY NEEDED]". \
Mark policy arguments relying on non-binding authority "[PERSUASIVE ONLY]".
"""
