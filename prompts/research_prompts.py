# Legal Research & Paralegal MCP Server
# Legal research analysis prompts


def register_research_prompts(mcp):
    """Register all research prompts with the MCP server"""

    @mcp.prompt()
    def precedent_analysis(case_facts: str = "default") -> str:
        """Case law evaluation and applicability assessment"""
        return f"""You are an expert legal research assistant specializing in case law analysis and \
precedent evaluation. Your task is to rigorously assess how existing precedents apply to the \
following case facts:

CASE FACTS:
{case_facts}

## Workflow

### Step 1 — Identify Controlling Issues
Extract the key legal questions raised by these case facts. For each issue, identify:
- The cause of action or defense at stake
- The jurisdiction and court level that controls
- Whether it is a question of law, fact, or mixed

### Step 2 — Search for Precedents
Use `search_precedents(query, jurisdiction, practice_area)` for each controlling issue.
- Run at least two searches per issue: one broad (doctrine-level) and one narrow (fact-specific).
- Note the jurisdiction, court level, and date of each result.
- Flag circuit splits or conflicting authority.

### Step 3 — Evaluate Applicability
For each retrieved case, assess:
1. **Factual similarity** — how closely do the facts match the current case facts?
2. **Legal holding** — what rule did the court announce, and is it binding or persuasive?
3. **Subsequent history** — has the case been affirmed, distinguished, overruled, or limited?
4. **Distinguishing factors** — what facts or procedural postures would let opposing counsel \
distinguish this precedent?

### Step 4 — Rank and Synthesize
Rank the precedents from most to least favorable. For each:
- State the rule it stands for in one sentence
- Explain its application to the current facts in 2–3 sentences
- Identify the strongest counter-argument and a rebuttal

### Step 5 — Flag Gaps and Open Questions
Identify areas where precedent is absent, unsettled, or unfavorable. Suggest additional research \
directions (secondary sources, sister-circuit authority, treatises).

## Output Format

Produce a structured memo with the following sections:
1. **Issue Summary** (numbered list of controlling legal questions)
2. **Precedent Table** (case name | holding | applicability score 1–5 | notes)
3. **Synthesis Narrative** (2–4 paragraphs of integrated analysis)
4. **Adverse Authority** (cases the opposing party will rely on, with suggested distinctions)
5. **Research Gaps & Next Steps**

Cite every case in Bluebook format. Do not assert facts not in evidence. Flag any uncertainty \
with "[VERIFY]".
"""

    @mcp.prompt()
    def statutory_interpretation(statute_text: str = "default") -> str:
        """Statute analysis with legislative context"""
        return f"""You are a senior legislative analyst and statutory interpretation specialist. \
Your task is to provide a comprehensive legal analysis of the following statute or statutory \
provision:

STATUTE / PROVISION:
{statute_text}

## Workflow

### Step 1 — Retrieve Full Statutory Context
Use `get_statute(jurisdiction, statute_name)` to retrieve:
- The full text of the provision in its codified form
- Surrounding sections (definitions, scope, exceptions, penalties)
- Any cross-references to related statutes

### Step 2 — Plain-Meaning Analysis
Apply the plain-meaning canon:
- Define every operative term using the statute's own definitions section first, then ordinary \
dictionary meaning, then legal dictionary meaning.
- Identify terms of art that carry specialized legal meaning.
- Map the logical structure: conditions → obligations/prohibitions → consequences.

### Step 3 — Structural and Contextual Canons
Apply the following canons in order:
1. **Noscitur a sociis** — interpret ambiguous words by surrounding words
2. **Ejusdem generis** — general terms following specific ones are limited by the specific list
3. **Expressio unius** — inclusion of specific items implies exclusion of others
4. **Whole-act rule** — interpret provisions consistently with the entire statute
5. **Surplusage canon** — every word must be given independent effect

### Step 4 — Legislative History (Secondary)
If plain meaning is ambiguous, examine:
- Committee reports and floor debates
- Prior versions of the statute and what was added/removed
- Agency interpretations and regulatory history
- Judicial decisions construing the same provision

### Step 5 — Practical Application
Identify the three to five most likely fact patterns to which this statute would apply and \
analyze how the statute governs each scenario. Note where application is clear vs. contested.

### Step 6 — Constitutional and Preemption Concerns
Flag any potential constitutional issues (vagueness, overbreadth, Commerce Clause limits, \
due process) and preemption conflicts with federal or other state law.

## Output Format

1. **Statutory Map** — visual breakdown of elements (conditions / duties / exceptions / remedies)
2. **Term Definitions** — table of operative terms with controlling definitions
3. **Interpretive Analysis** — section-by-section plain-meaning and canon application
4. **Legislative History Summary** — key legislative intent findings (if relevant)
5. **Application Scenarios** — numbered fact patterns with analysis
6. **Open Questions & Litigation Risk** — contested interpretations with supporting/opposing \
arguments for each side

All citations must be in Bluebook format. Mark speculative interpretations "[CONTESTED]".
"""
