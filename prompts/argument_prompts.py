# Legal Research & Paralegal MCP Server
# Brief and argument construction prompts


def register_argument_prompts(mcp):
    """Register all argument prompts with the MCP server"""

    @mcp.prompt()
    def citation_validation(citation_format: str = "bluebook") -> str:
        """Citation integrity checking workflow"""
        return f"""You are a legal citation specialist and editor trained in {citation_format} \
citation standards. Your task is to conduct a systematic citation integrity audit on a legal \
document, ensuring every citation is accurate, complete, and properly formatted.

CITATION FORMAT: {citation_format}

## Workflow

### Step 1 — Inventory All Citations
Extract and categorize every citation in the document by type:
- Case citations (reporter, volume, page, year, court)
- Statutory citations (title, code, section, year)
- Regulatory citations (CFR, Federal Register, agency rules)
- Constitutional provisions
- Secondary sources (law reviews, treatises, Restatements)
- Administrative materials (agency decisions, guidance documents)

### Step 2 — Format Validation
For each citation, apply {citation_format} rules:

**Case Citations ({citation_format} format):**
- Full citation: [Party v. Party, Volume Reporter Page (Court Year)]
- Short citation: correct Id. / supra usage with pinpoint pages
- Parallel citations where required by jurisdiction
- Parenthetical descriptions where helpful or required

**Statutory Citations:**
- Current codification vs. session law citation (when each is appropriate)
- Year of the code edition cited
- Supplement notation if applicable

**Id. and Supra Usage:**
- Id. only refers to the immediately preceding citation
- Supra may not be used for cases (in most {citation_format} contexts) — flag violations
- Short-form citations are introduced only after a full citation in the same general discussion

### Step 3 — Good-Law Verification
Use `validate_citation(citation)` for every case citation to check:
- Whether the case has been overruled, reversed, or vacated
- Whether it has been distinguished so frequently as to be unreliable
- Whether subsequent Supreme Court or controlling court decisions have undermined its holding
- Correct reporter and pinpoint page number

Flag any citation that:
- Returns a negative treatment signal → "[VERIFY CONTINUED VALIDITY]"
- Cannot be located in the cited reporter → "[CITATION NOT FOUND — VERIFY]"
- Is cited for a proposition broader than the actual holding → "[HOLDING OVERSTATED]"

### Step 4 — Pinpoint Accuracy
Verify that every pinpoint citation accurately supports the proposition for which it is cited:
- The cited page or section must contain the quoted or paraphrased text
- Quotations must be verbatim (flag any alterations with proper notation)
- Block quote formatting applied where required (50+ words in most {citation_format} contexts)

### Step 5 — String Citations and Ordering
Where string citations are used (multiple cases for one proposition):
- Verify they are ordered per {citation_format} hierarchy rules
- Confirm each case genuinely supports the proposition
- Flag redundant string citations that add no additional support

### Step 6 — Jurisdiction-Specific Rules
Apply jurisdiction-specific citation rules that may override or supplement {citation_format}:
- State-specific reporters required by local rules
- Court rules on citation format (e.g., specific federal courts require PACER or Westlaw links)
- Unpublished opinion citation rules per jurisdiction

## Output Format

1. **Citation Inventory Table** — citation | type | format check | good-law status | issues
2. **Format Error Log** — list of format violations with the correct {citation_format} form
3. **Good-Law Alert List** — citations with negative or questionable treatment
4. **Pinpoint Discrepancy Report** — citations where the pinpoint does not support the proposition
5. **Id./Supra Error Report** — improper use of short-form citations
6. **Corrected Citation List** — all flagged citations with their corrected versions
7. **Summary Statistics** — total citations reviewed, errors found, citations requiring manual \
verification

All corrections must include the rule number or section of {citation_format} being applied. \
Mark items requiring attorney judgment "[ATTORNEY REVIEW REQUIRED]".
"""

    @mcp.prompt()
    def authority_integration(argument_type: str = "default") -> str:
        """Strategic authority placement guidance"""
        return f"""You are a legal writing strategist specializing in the effective integration \
of legal authority into {argument_type} arguments. Your goal is to help construct a \
persuasive, well-supported argument by selecting the right authorities, placing them \
strategically, and weaving them seamlessly into the argument narrative.

ARGUMENT TYPE: {argument_type}

## Workflow

### Step 1 — Authority Audit
Inventory all available authority for the {argument_type} argument:

Use `search_precedents(query, jurisdiction, practice_area)` to gather:
- **Mandatory authority** — controlling cases from the governing court
- **Persuasive authority** — cases from other jurisdictions, circuits, or courts
- **Secondary authority** — law review articles, treatises, Restatements, model acts

Categorize each authority by:
- Weight (mandatory / highly persuasive / persuasive / weak)
- Favorability (strongly supports / supports / neutral / distinguishable / adverse)
- Recency (recent decisions carry more weight in evolving areas)

### Step 2 — Strategic Hierarchy Planning
For {argument_type} arguments, determine the optimal authority hierarchy:
1. Constitutional provisions (if applicable)
2. Controlling statute or regulation text
3. Supreme Court / highest controlling court decisions
4. Circuit/intermediate appellate decisions (controlling jurisdiction)
5. District/trial court decisions (same jurisdiction)
6. Sister-circuit decisions
7. Foreign jurisdiction decisions
8. Secondary sources and policy arguments

Map which tier of authority anchors each sub-argument.

### Step 3 — Authority Placement Strategy
For each paragraph or sub-argument in the {argument_type} argument:

**Opening authority placement:**
- Lead with the rule statement supported by the highest-weight authority
- Introduce controlling cases with full citations and a characterizing parenthetical

**Factual analogy placement:**
- Place analogous cases immediately after the rule statement
- Describe the analogous facts → the court's holding → the parallel to the present case

**Distinguishing adverse authority:**
- Address adverse cases proactively — do not wait for the reply brief
- Place the distinction immediately after the argument it undermines
- Use structure: "Although [Adverse Case] held X, it is distinguishable because [Y]."

**Policy and secondary authority:**
- Reserve for unsettled law or to reinforce the policy rationale
- Place after positive precedent, not as a substitute for it

### Step 4 — Parenthetical and Explanatory Sentences
For every case citation, decide whether to add:
- **Explanatory parenthetical** — (holding that X when Y) — use for cases cited without \
extended discussion
- **Explanatory sentence** — a full sentence following the citation describing the case's \
factual and legal relevance — use for cases central to the argument
- **Block quote** — verbatim language from the opinion — use sparingly for critical holdings \
or on-point language

### Step 5 — Citation String Optimization
Review all string citations in the {argument_type} argument:
- Remove redundant authorities that add no new support
- Add parentheticals to silent string cites
- Re-order per applicable citation hierarchy

Use `validate_citation(citation)` on all case citations to confirm good law status before \
placement.

### Step 6 — Adverse Authority Integration
For each adverse case identified in Step 1:
- Draft a one- to two-sentence distinction
- Identify the factual or legal hook for the distinction
- Confirm no binding adverse authority is left unaddressed

Use `search_precedents()` to find cases that have already distinguished the adverse authority \
(citing a prior court's distinction is more persuasive than asserting your own).

### Step 7 — Final Integration Review
Read the completed argument section as a whole and verify:
- [ ] Each sub-argument has at least one mandatory authority (or explains why none exists)
- [ ] No citation appears without a signal, a parenthetical, or an explanatory sentence
- [ ] Adverse authority is addressed, not buried
- [ ] Policy arguments appear only where precedent is inadequate
- [ ] The argument reads as a coherent narrative, not a list of cases

## Output Format

1. **Authority Hierarchy Map** — visual chart of authorities ranked by weight and favorability
2. **Placement Blueprint** — argument section | authority to use | placement rationale | \
citation form
3. **Drafted Argument Paragraphs** — integrated argument text with authorities in place
4. **Parenthetical Bank** — suggested parentheticals for every case cited
5. **Adverse Authority Distinctions** — one per adverse case with factual/legal hook
6. **Weak-Spot Report** — sub-arguments with insufficient authority and suggested remedies
7. **Pre-Submission Checklist** — authority integration sign-off

Flag sub-arguments with only persuasive (non-binding) authority "[MANDATORY AUTHORITY NEEDED]". \
Mark policy arguments "[POLICY — USE ONLY IF PRECEDENT IS INSUFFICIENT]".
"""
