# Legal MCP Server - Example Workflows

This document provides detailed examples of how legal teams interact with the Legal MCP Server through AI assistants, showcasing the complete workflow from user request to final deliverable.

## 🏗️ Architecture Overview

```
Legal Team → AI Assistant → MCP Server → Tools/Resources/Prompts → Response → Legal Team
```

## 📋 Workflow Categories

- [Contract Analysis Workflow](#contract-analysis-workflow)
- [Legal Research Workflow](#legal-research-workflow)
- [Brief Drafting Workflow](#brief-drafting-workflow)
- [Citation Validation Workflow](#citation-validation-workflow)
- [Statute Analysis Workflow](#statute-analysis-workflow)
- [Negotiation Guide Workflow](#negotiation-guide-workflow)
- [Real Document Analysis & Metadata Extraction Workflow](#real-document-analysis--metadata-extraction-workflow)
- [Privilege Risk Check Workflow](#privilege-risk-check-workflow)
- [Async Analysis Queue Workflow](#async-analysis-queue-workflow)
- [Built on these workflows — Legal Terminal (showcase)](#-built-on-these-workflows--legal-terminal-showcase)

---

## 📄 Contract Analysis Workflow

### **Scenario**: Paralegal needs to compare two NDA versions and identify key differences

#### **Step 1: User Request**
```
Legal Team Member: "I need to compare our standard NDA template with the client's proposed NDA. 
Can you identify the key differences and highlight any potential risks?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll help you analyze the NDA comparison. Let me use our contract analysis tools 
to identify differences and assess potential risks."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "compare_contracts",
    "arguments": {
      "contract_a": "standard_nda_template",
      "contract_b": "client_proposed_nda"
    }
  }
}
```

**Resource Access:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "legal://contract-templates"
  }
}
```

**Prompt Usage:**
```json
{
  "method": "prompts/get",
  "params": {
    "name": "contract_review",
    "arguments": {
      "contract_type": "NDA",
      "analysis_focus": "risk_identification"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Contract Tools** extract clauses from both documents
2. **Contract Resources** provide standard NDA templates for comparison
3. **Analysis Prompts** guide structured risk assessment
4. **Citation Tools** validate any referenced legal standards

#### **Step 5: Response to Legal Team**
```markdown
## NDA Comparison Analysis

### Key Differences Identified:

**1. Confidentiality Scope**
- **Standard**: Broad definition including "all proprietary information"
- **Client**: Narrowed to "specifically marked confidential"
- **Risk Level**: ⚠️ MEDIUM - May limit protection scope

**2. Term Duration**
- **Standard**: 5 years post-termination
- **Client**: 3 years post-termination
- **Risk Level**: ✅ LOW - Reasonable reduction

**3. Return of Materials**
- **Standard**: 30 days to return/destroy
- **Client**: 60 days to return/destroy
- **Risk Level**: ⚠️ MEDIUM - Extended exposure period

### Recommendations:
1. Negotiate broader confidentiality definition
2. Accept reduced term duration
3. Request 30-day return period or immediate destruction option

### Next Steps:
- Review with senior attorney
- Prepare negotiation points
- Schedule client discussion
```

---

## 🔍 Legal Research Workflow

> **⚠️ Cost warning:** The Legal Research workflow may query paid databases such as PACER. AI-driven research can consume a standard account's $30/quarter PACER waiver in minutes. Pro se litigants and individual users should monitor account usage closely. Prefer free sources (CourtListener/RECAP, when integrated) where possible.

### **Scenario**: Associate needs to find precedents for a contract breach case in California

#### **Step 1: User Request**
```
Associate: "I'm working on a contract breach case in California. The client claims the other 
party failed to deliver goods on time. Can you find relevant case law and help me understand 
the key legal principles?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll search for California contract breach precedents related to delivery 
timing issues. Let me find relevant case law and analyze the key legal principles."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "search_precedents",
    "arguments": {
      "query": "contract breach delivery timing California",
      "jurisdiction": "CA",
      "case_type": "commercial_contracts"
    }
  }
}
```

**Resource Access:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "legal://case-database"
  }
}
```

**Prompt Usage:**
```json
{
  "method": "prompts/get",
  "params": {
    "name": "precedent_analysis",
    "arguments": {
      "case_facts": "delivery_timing_breach",
      "jurisdiction": "California"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Research Tools** search case database for relevant precedents
2. **Case Resources** provide detailed case law information
3. **Research Prompts** structure the legal analysis framework
4. **Citation Tools** validate and format case citations

#### **Step 5: Response to Legal Team**
```markdown
## California Contract Breach Research Results

### Key Precedents Found:

**1. Smith v. ABC Corp (2022) - CA Court of Appeal**
- **Citation**: 2022 Cal.App.4th 1234
- **Holding**: Time is of the essence clauses must be explicitly stated
- **Relevance**: ⭐⭐⭐⭐⭐ Direct precedent for delivery timing cases

**2. Johnson v. XYZ Industries (2020) - CA Supreme Court**
- **Citation**: 2020 Cal.4th 567
- **Holding**: Commercial contracts presumed to have reasonable delivery terms
- **Relevance**: ⭐⭐⭐⭐ Establishes default timing standards

**3. Davis v. Tech Solutions (2021) - CA Court of Appeal**
- **Citation**: 2021 Cal.App.4th 890
- **Holding**: Material breach requires substantial non-performance
- **Relevance**: ⭐⭐⭐⭐ Defines breach severity standards

### Legal Principles Summary:

**Time of Essence Requirements:**
- Must be explicitly stated in contract
- Cannot be implied from circumstances
- Failure to include = reasonable timing standard applies

**Material Breach Standards:**
- Substantial non-performance required
- Minor delays typically not material
- Consider industry standards and custom

**Damages Calculation:**
- Direct damages: Lost profits from delay
- Consequential damages: Must be foreseeable
- Mitigation required: Reasonable efforts to minimize loss

### Recommended Next Steps:
1. Review client contract for "time is of the essence" language
2. Gather evidence of industry delivery standards
3. Calculate specific damages with supporting documentation
4. Prepare motion for summary judgment if facts support
```

---

## 📝 Brief Drafting Workflow

### **Scenario**: Partner needs to draft a motion for summary judgment

#### **Step 1: User Request**
```
Partner: "I need to draft a motion for summary judgment in our contract breach case. 
The facts are clear - the defendant failed to deliver goods within the specified timeframe. 
Can you help me structure the argument and identify the strongest legal authorities?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll help you draft a comprehensive motion for summary judgment. Let me 
create an argument structure and identify the most persuasive legal authorities for your case."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_brief_outline",
    "arguments": {
      "case_type": "contract_breach",
      "motion_type": "summary_judgment",
      "jurisdiction": "CA"
    }
  }
}
```

**Resource Access:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "legal://brief-frameworks"
  }
}
```

**Prompt Usage:**
```json
{
  "method": "prompts/get",
  "params": {
    "name": "brief_construction",
    "arguments": {
      "case_type": "contract_breach_summary_judgment",
      "argument_focus": "material_breach_establishment"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Brief Tools** generate structured outline for summary judgment motion
2. **Brief Resources** provide template frameworks and argument patterns
3. **Drafting Prompts** guide legal argument construction
4. **Research Tools** identify supporting authorities

#### **Step 5: Response to Legal Team**
```markdown
## Motion for Summary Judgment - Draft Outline

### I. STATEMENT OF UNDISPUTED FACTS
**A. Contract Formation**
- Date of contract execution
- Parties and their business relationship
- Goods and services specified

**B. Delivery Terms**
- Specific delivery timeframe agreed upon
- "Time is of the essence" language (if present)
- Industry standard delivery practices

**C. Breach Occurrence**
- Defendant's failure to deliver within timeframe
- Plaintiff's performance of all obligations
- Notice of breach provided to defendant

### II. LEGAL STANDARD FOR SUMMARY JUDGMENT
**A. Standard of Review**
- No genuine issue of material fact
- Moving party entitled to judgment as matter of law
- All inferences in favor of non-moving party

**B. Contract Breach Elements**
- Valid contract exists
- Plaintiff performed or was ready to perform
- Defendant breached material term
- Plaintiff suffered damages

### III. ARGUMENT

**A. Valid Contract Exists**
- Written agreement with clear terms
- Both parties signed and acknowledged
- Consideration exchanged

**B. Plaintiff Performed All Obligations**
- Payment made according to terms
- No conditions precedent remaining
- Ready, willing, and able to perform

**C. Defendant Materially Breached Contract**
- **Time is of the essence**: [Cite specific contract language]
- **Industry standard**: Delivery within [X] days is standard practice
- **Materiality**: Delay caused [specific damages/harm]

**D. Damages Are Calculable and Certain**
- Direct damages: [specific amount]
- Consequential damages: [if applicable]
- Mitigation efforts: [what plaintiff did to minimize loss]

### IV. SUPPORTING AUTHORITIES

**Primary Cases:**
- Smith v. ABC Corp (2022) - Time is of the essence requirements
- Johnson v. XYZ Industries (2020) - Material breach standards
- Davis v. Tech Solutions (2021) - Damages calculation

**Statutory Authority:**
- California Commercial Code § 2106 (time of performance)
- California Civil Code § 1657 (reasonable time standards)

### V. CONCLUSION
Defendant's material breach of delivery terms entitles Plaintiff to summary judgment as a matter of law.

### Next Steps:
1. Review and refine argument structure
2. Gather supporting evidence and exhibits
3. Draft detailed factual statements
4. Prepare declaration of supporting witnesses
5. Finalize motion and file with court
```

---

## ✓ Citation Validation Workflow

### **Scenario**: Law clerk needs to verify and format citations for a brief

#### **Step 1: User Request**
```
Law Clerk: "I have a list of citations that need to be verified and formatted according to 
Bluebook standards. Can you check their accuracy and provide the properly formatted versions?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll validate each citation for accuracy and format them according to 
Bluebook standards. Let me check the citations and provide properly formatted versions."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "validate_citation",
    "arguments": {
      "citations": [
        "Smith v. ABC Corp, 2022 Cal.App.4th 1234",
        "Johnson v. XYZ, 2020 Cal.4th 567",
        "Davis v. Tech, 2021 Cal.App.4th 890"
      ],
      "format_standard": "bluebook"
    }
  }
}
```

**Resource Access:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "legal://citation-standards"
  }
}
```

**Prompt Usage:**
```json
{
  "method": "prompts/get",
    "params": {
      "name": "citation_validation",
      "arguments": {
        "citation_format": "bluebook",
        "jurisdiction": "California"
      }
    }
  }
```

#### **Step 4: Server Processing**
1. **Citation Tools** validate each citation against legal databases
2. **Citation Resources** provide formatting rules and standards
3. **Citation Prompts** guide validation workflow
4. **Research Tools** verify case existence and details

#### **Step 5: Response to Legal Team**
```markdown
## Citation Validation Results

### ✅ Validated Citations:

**1. Smith v. ABC Corp**
- **Original**: Smith v. ABC Corp, 2022 Cal.App.4th 1234
- **Validated**: ✅ Accurate
- **Bluebook Format**: Smith v. ABC Corp, 2022 Cal.App.4th 1234
- **Status**: Ready to use

**2. Johnson v. XYZ Industries**
- **Original**: Johnson v. XYZ, 2020 Cal.4th 567
- **Validated**: ⚠️ Incomplete case name
- **Corrected**: Johnson v. XYZ Industries, 2020 Cal.4th 567
- **Bluebook Format**: Johnson v. XYZ Indus., 2020 Cal.4th 567
- **Status**: Updated and ready

**3. Davis v. Tech Solutions**
- **Original**: Davis v. Tech, 2021 Cal.App.4th 890
- **Validated**: ⚠️ Incomplete case name
- **Corrected**: Davis v. Tech Solutions, 2021 Cal.App.4th 890
- **Bluebook Format**: Davis v. Tech Sols., 2021 Cal.App.4th 890
- **Status**: Updated and ready

### 📋 Bluebook Formatting Notes:

**Case Name Abbreviations:**
- "Corporation" → "Corp."
- "Industries" → "Indus."
- "Solutions" → "Sols."

**Court Abbreviations:**
- "Cal.App.4th" → California Court of Appeal, Fourth District
- "Cal.4th" → California Supreme Court

**Pinpoint Citations:**
- Add specific page numbers when referencing particular holdings
- Use "at" for pinpoint citations: "Smith v. ABC Corp, 2022 Cal.App.4th 1234, 1240"

### ✅ Final Citation List:
1. Smith v. ABC Corp, 2022 Cal.App.4th 1234
2. Johnson v. XYZ Indus., 2020 Cal.4th 567
3. Davis v. Tech Sols., 2021 Cal.App.4th 890

### Next Steps:
1. Update brief with corrected citations
2. Add pinpoint citations for specific holdings
3. Verify all citations in final proofread
4. Submit for partner review
```

---

## 📚 Statute Analysis Workflow

### **Scenario**: Associate needs to analyze a specific statute for a client advisory

#### **Step 1: User Request**
```
Associate: "I need to analyze California Civil Code Section 1657 regarding reasonable time 
standards in contracts. Can you provide the statute text, legislative history, and help me 
understand how it applies to our client's situation?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll extract the statute text, provide legislative context, and help you 
analyze how Section 1657 applies to your client's contract timing issues."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "extract_statute",
    "arguments": {
      "statute_id": "Cal.Civ.Code.1657",
      "context": true,
      "include_history": true
    }
  }
}
```

**Resource Access:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "legal://statute-library"
  }
}
```

**Prompt Usage:**
```json
{
  "method": "prompts/get",
  "params": {
    "name": "statutory_interpretation",
    "arguments": {
      "statute_text": "Cal.Civ.Code.1657",
      "analysis_focus": "reasonable_time_standards"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Research Tools** extract statute text and legislative history
2. **Statute Resources** provide contextual information and amendments
3. **Research Prompts** guide statutory interpretation analysis
4. **Citation Tools** validate statute references and formatting

#### **Step 5: Response to Legal Team**
```markdown
## California Civil Code Section 1657 Analysis

### 📜 Statute Text:
```
Cal. Civ. Code § 1657. Reasonable Time
Where no time is specified for the performance of an act required to be performed, a reasonable time is allowed. If the act is in its nature capable of being done instantly, it must be performed immediately, or at least within such time as may be necessary for the performance of the act.
```

### 📚 Legislative History:
- **Enacted**: 1872 (original Civil Code)
- **Last Amended**: 1983 (minor language clarification)
- **Purpose**: Establish default timing standards for contract performance
- **Precedent**: Based on common law reasonable time principles

### 🔍 Statutory Interpretation:

**Key Elements:**
1. **Default Rule**: When no time specified, reasonable time applies
2. **Immediate Performance**: Acts capable of instant performance must be done immediately
3. **Necessary Time**: Allowance for acts requiring preparation or execution time

**Application to Client's Case:**
- **Contract Language**: [Review specific contract terms]
- **Performance Type**: Delivery of goods (not instantly performable)
- **Reasonable Time**: Industry standard + circumstances of case
- **Breach Analysis**: Whether delay exceeded reasonable time

### 📋 Case Law Interpretation:

**Leading Cases:**
- **Smith v. ABC Corp (2022)**: "Reasonable time determined by nature of act and circumstances"
- **Johnson v. XYZ (2020)**: "Industry standards relevant but not dispositive"
- **Davis v. Tech (2021)**: "Commercial context requires business efficiency standards"

### 🎯 Client Advisory Points:

**1. Statute Application:**
- If contract lacks specific delivery time, Section 1657 applies
- "Reasonable time" determined by industry standards and circumstances
- Court considers nature of goods, distance, and business practices

**2. Risk Assessment:**
- **Low Risk**: Industry standard delivery times (e.g., 30-60 days)
- **Medium Risk**: Extended delays beyond industry norms
- **High Risk**: Delays causing material harm or business disruption

**3. Strategic Considerations:**
- **Proactive**: Include specific delivery terms in future contracts
- **Defensive**: Gather evidence of industry standards and practices
- **Offensive**: Argue delay exceeded reasonable time under circumstances

### 📝 Draft Advisory Language:
```
Based on California Civil Code Section 1657, when a contract does not specify a delivery time, 
a "reasonable time" is allowed for performance. The determination of reasonable time depends 
on the nature of the goods, industry standards, and surrounding circumstances.

For your client's situation, we recommend:
1. Documenting industry standard delivery times
2. Gathering evidence of business impact from delay
3. Establishing that delay exceeded reasonable time under circumstances
4. Considering specific delivery terms for future contracts
```

### Next Steps:
1. Review client's specific contract language
2. Gather industry standard delivery time evidence
3. Document business impact and damages
4. Prepare legal argument based on statutory analysis
5. Consider contract language improvements for future agreements
```

---

## 🤝 Negotiation Guide Workflow

### **Scenario**: In-house counsel needs a buyer-side negotiation position on a vendor's Master Services Agreement

#### **Step 1: User Request**
```
In-house Counsel: "We're the buyer on this Master Services Agreement. Can you give me a
clause-by-clause negotiation position — what to accept, what to push back on, and suggested
fallback language?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll generate a negotiation guide from the buyer's perspective, flagging
which clauses to accept, negotiate, or reject, with fallback language for anything risky."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "generate_negotiation_guide",
    "arguments": {
      "contract_id": "master_services_agreement",
      "party_role": "buyer"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Contract Tools** load the MSA's clauses from the template library
2. **Risk Heuristics** (`assess_clause_risk`) score each clause LOW / MEDIUM / HIGH
3. **`POSITION_MATRIX`** maps `(risk_level, party_role)` to a recommended position
4. **`CLAUSE_ALTERNATIVES`** supplies fallback language for risky clause types

#### **Step 5: Response to Legal Team**
```markdown
## Negotiation Guide — Master Services Agreement (Buyer Position)

**1. `limitation_of_liability` — HIGH risk**
- **Position**: ❌ Reject
- **Rationale**: High-risk clause favors seller; seek mutual cap or deletion.
- **Fallback language**: "Indemnifying party's liability shall exclude indirect,
  incidental, or consequential damages and shall not exceed the greater of fees
  paid in the prior twelve months or $100,000."

**2. `term_duration` — MEDIUM risk**
- **Position**: ⚠️ Negotiate
- **Rationale**: Review and narrow scope before accepting.
- **Fallback language**: Standard fixed-term renewal with a 60-day non-renewal
  notice window.

**3. `scope_of_services` — LOW risk**
- **Position**: ✅ Accept
- **Rationale**: Standard market language.

### Next Steps:
1. Route HIGH-risk items to the vendor's counsel as redline priorities
2. Confirm fallback language with senior counsel before sending
3. Track final negotiated positions in the deal file
```

> **Note:** Output is an AI-generated scaffold for attorney review, not legal advice.
> Every response from `generate_negotiation_guide` carries this disclaimer.

---

## 📑 Real Document Analysis & Metadata Extraction Workflow

### **Scenario**: Contracts manager received a signed vendor agreement as a `.docx` file and needs a risk summary plus a quick-reference data sheet — without re-reading the whole document

#### **Step 1: User Request**
```
Contracts Manager: "Here's the signed vendor agreement (vendor_agreement.docx). Can you
flag any risky clauses and pull out the key terms — governing law, term length,
auto-renewal, liability cap — so I don't have to hunt through the document?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll analyze the document for clause-level risk and extract the key
contract terms into a structured summary."
```

#### **Step 3: MCP Server Interactions**

**Tool Call 1 — risk analysis:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "analyze_document",
    "arguments": {
      "file_path": "/contracts/vendor_agreement.docx"
    }
  }
}
```

**Tool Call 2 — structured metadata:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "extract_contract_metadata",
    "arguments": {
      "file_path": "/contracts/vendor_agreement.docx"
    }
  }
}
```

**Tool Call 3 — exportable report:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "export_analysis_report",
    "arguments": {
      "analysis_json": "<result from analyze_document>",
      "output_path": "/contracts/vendor_agreement_analysis.docx"
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Document Tools** read the real `.docx` file directly — no seed-data ID required
2. **Risk Heuristics** flag clauses (e.g., uncapped indemnification, unlimited liability)
3. **Regex extraction** over the same clause text pulls parties, dates, governing law,
   term, auto-renewal, notice period, liability cap, and payment terms
4. **Export Tools** generate a formatted `.docx` report for the deal file

#### **Step 5: Response to Legal Team**
```markdown
## Vendor Agreement — Analysis Summary

**Overall Risk**: ⚠️ MEDIUM (1 of 6 clauses flagged)

### Extracted Contract Metadata
| Field | Value |
| --- | --- |
| Parties | Acme Inc., Vendor Corp. |
| Effective Date | 2026-01-01 |
| Governing Law | Delaware |
| Term | 12 months |
| Auto-Renewal | Yes |
| Notice Period | 30 days |
| Liability Cap | $100,000 |
| Payment Terms | Net 45 |

*Note: `extract_contract_metadata` is pure regex extraction — no legal judgment.
Fields not found in the text return `null` rather than a guess.*

### Flagged Clause
**`indemnification`** — MEDIUM risk: no cap on indemnification obligations.

A formatted `.docx` report was exported to
`/contracts/vendor_agreement_analysis.docx` for the deal file.

### Next Steps:
1. Route the indemnification clause to counsel for a cap negotiation
2. File the exported report alongside the signed agreement
```

---

## 🔒 Privilege Risk Check Workflow

### **Scenario**: Associate wants to paste a draft litigation memo into a general-purpose AI chatbot for a quick sanity check, but isn't sure if that risks attorney-client privilege

#### **Step 1: User Request**
```
Associate: "Before I paste this litigation memo into ChatGPT for a quick review, can you
check whether that's a privilege risk?"
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll run a privilege risk check against the memo, taking into account the
provider you're planning to use and whether this review is attorney-directed."
```

#### **Step 3: MCP Server Interactions**

**Tool Call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "check_privilege_risk",
    "arguments": {
      "file_path": "/drafts/litigation_memo.docx",
      "inference_provider": "openai",
      "counsel_directed": false
    }
  }
}
```

#### **Step 4: Server Processing**
1. **Document Tools** read the memo's text
2. **Privilege heuristics** scan for privilege-indicating language ("attorney-client",
   "work product", "privileged", "legal advice", etc.) and AI-generation artifacts
3. **`PROVIDER_POSTURES`** looks up the named provider's data retention and training
   posture (`openai`, `anthropic`, `azure_openai`, `vertex_ai`, `openrouter`, `ollama`)
4. Indicators + provider posture + `counsel_directed` combine into a risk score

#### **Step 5: Response to Legal Team**
```markdown
## Privilege Risk Check — litigation_memo.docx

**Provider**: OpenAI (API: no training by default, no ZDR option)
**Counsel-Directed**: No
**Privilege Indicators Found**: "attorney-client", "work product", "legal advice"

**Privilege Risk**: 🔴 HIGH

**Recommended Posture**: Do not route this document without explicit attorney
authorization. The document may contain privileged content and the selected
provider does not offer zero data retention. Use a local inference provider
(e.g., Ollama) or obtain a BAA/ZDR agreement.

**Heppner Note**: *United States v. Heppner* (S.D.N.Y. 2026) held that routing
attorney-client privileged communications through a third-party AI inference
provider may constitute a waiver of privilege where the provider retains data
and the disclosure was not narrowly necessary.

**ABA Rule**: ABA Model Rule 1.6 requires lawyers to make reasonable efforts to
prevent inadvertent disclosure of client confidential information. ABA Formal
Opinion 512 (2023) addresses competence obligations when using generative AI
tools in legal practice.

### Next Steps:
1. Get explicit authorization from supervising counsel before sending
2. Consider re-running the check with `inference_provider: "ollama"` for a
   local, zero-retention alternative
3. If proceeding, set `counsel_directed: true` only once an attorney has
   actually authorized the disclosure
```

> **Note:** This check is a risk-screening heuristic, not a privilege determination.
> Always consult qualified counsel before making privilege decisions.

---

## 📥 Async Analysis Queue Workflow

### **Scenario**: Paralegal has a batch of 20 incoming vendor contracts to risk-screen overnight and wants to check results the next morning

#### **Step 1: User Request**
```
Paralegal: "Queue up all 20 contracts in the /intake folder for analysis. I'll check the
results tomorrow morning."
```

#### **Step 2: AI Assistant Processing**
```
AI Assistant: "I'll queue each contract for AI risk analysis and give you the job IDs so
you can check status and pull results whenever you're ready."
```

#### **Step 3: MCP Server Interactions**

**Tool Call — queue each file:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "queue_document_analysis",
    "arguments": {
      "file_path": "/intake/vendor_contract_07.docx",
      "analysis_notes": "Batch intake — Q3 vendor onboarding"
    }
  }
}
```

**Next morning — check status:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_analysis_status",
    "arguments": { "job_id": "3f1c9e2a-....-....-............" }
  }
}
```

**Retrieve the result:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_analysis_result",
    "arguments": { "job_id": "3f1c9e2a-....-....-............" }
  }
}
```

**List everything queued so far:**
```json
{
  "method": "tools/call",
  "params": { "name": "list_analysis_jobs", "arguments": {} }
}
```

#### **Step 4: Server Processing**
1. Each call to `queue_document_analysis` generates a UUID job ID, writes a `queued`
   record to a local SQLite store (`legal_mcp_analysis.db`), runs the same risk
   analysis as `analyze_document`, and updates the record to `complete` or `error`
2. `get_analysis_status` / `get_analysis_result` / `list_analysis_jobs` read back from
   the same local store — no network calls, no external submission

#### **Step 5: Response to Legal Team**
```markdown
## Batch Analysis Queue — Q3 Vendor Onboarding

20 contracts queued. 19 complete, 1 error (unsupported file format: `.pdf`).

| Job ID (short) | File | Status | Overall Risk |
| --- | --- | --- | --- |
| 3f1c9e2a | vendor_contract_07.docx | complete | MEDIUM |
| 7b4d0f11 | vendor_contract_08.docx | complete | HIGH |
| a92e88c0 | vendor_contract_09.pdf | error | — (unsupported format) |
| ... | ... | ... | ... |

### Next Steps:
1. Prioritize review of the 3 contracts flagged HIGH risk
2. Convert the failed `.pdf` to `.docx` and re-queue
3. Archive `complete` results into the contract management system
```

> **Note:** This is a local AI analysis job store, not a document submission
> service — nothing leaves your machine, and no attorney workload is created.
> For professional attorney review of flagged documents, contact
> [edwin@genego.io](mailto:edwin@genego.io).

---

## 🖥 Built on these workflows — Legal Terminal (showcase)

The workflows above describe how an **AI assistant** chains MCP tools on behalf
of a legal team. **[Legal Terminal](https://github.com/genego-io/legal-terminal)**
is a reference **showcase** that implements the same patterns in a dedicated
product UI — a Bloomberg-style, keyboard-first workstation with a React web
terminal and a Python TUI, both calling the same 27 tools this server exposes.

| | |
| --- | --- |
| **Live demo** | [legal-terminal.up.railway.app](https://legal-terminal.up.railway.app/) — mock mode by default; explore panels without a backend |
| **Source** | [github.com/genego-io/legal-terminal](https://github.com/genego-io/legal-terminal) — showcase repo; proprietary license (viewing for evaluation) |

The demo ships with a `MockClient` and fixture data so every panel works
offline. Toggle **Live** in the status bar (or wire up `LiveClient` in the
repo) to connect to a running `legal-mcp` instance over SSE and run the real
tool calls described in the workflows below.

### How each workflow maps to the terminal

| Workflow in this doc | Legal Terminal panel | Key MCP tools |
| --- | --- | --- |
| [Contract Analysis](#contract-analysis-workflow) | `CTRX` — Contract Workbench | `compare_contracts`, `analyze_clauses`, `suggest_clause_alternatives` |
| [Legal Research](#legal-research-workflow) | `PREC` — Precedent Search; `CHAT` — Paralegal | `search_precedents`, `search_case_law`, `research_legal_issue` |
| [Brief Drafting](#brief-drafting-workflow) | `BRF` — Brief Builder | `generate_brief_outline`, `create_argument_structure`, `generate_issue_statement` |
| [Citation Validation](#citation-validation-workflow) | `CITE` — Citation Console | `validate_citation`, `normalize_citation`, `verify_citation_integrity` |
| [Statute Analysis](#statute-analysis-workflow) | `STAT` — Statute Viewer | `extract_statute` |
| [Negotiation Guide](#negotiation-guide-workflow) | `CTRX` — Contract Workbench | `generate_negotiation_guide`, `analyze_clauses` |
| [Real Document Analysis & Metadata](#real-document-analysis--metadata-extraction-workflow) | `DOCA` — Document Analyzer | `analyze_document`, `extract_contract_metadata`, `export_analysis_report` |
| [Privilege Risk Check](#privilege-risk-check-workflow) | `PRIV` — Privilege Check; `CONF` — Privacy Settings | `check_privilege_risk` |
| [Async Analysis Queue](#async-analysis-queue-workflow) | `JOBS` — Analysis Queue | `queue_document_analysis`, `get_analysis_status`, `get_analysis_result`, `list_analysis_jobs` |

Additional panels surface cross-cutting concerns from this server:

- **`WKFL`** — runs the [`legal-mcp-toolkit`](.agents/skills/legal-mcp-toolkit/SKILL.md) workflow playbooks as checklists (the same sequences an AI assistant would follow in the steps above).
- **`LIVE`** — `integration_status` for CourtListener and PACER.
- **`AUDT`** — local audit log mirroring `utils.audit` from every tool invocation.

Legal Terminal is maintained separately as a **showcase** (not part of this
repo). Use it to study how multi-step MCP workflows become panel UX, command-bar
mnemonics (`PREC breach of contract`, `CITE 2022 Cal.App.4th 1234`), and
mock/live client patterns; extend **this** repo when you need new tools or
data.

---

## 🔄 Workflow Summary

### **Common Patterns Across All Workflows:**

1. **User Request** → Clear, specific legal need
2. **AI Processing** → Understanding and tool selection
3. **MCP Server** → Coordinated tool, resource, and prompt usage
4. **Server Processing** → Legal analysis and data synthesis
5. **Structured Response** → Actionable legal guidance

### **Key Benefits:**

✅ **Comprehensive Analysis** - Multiple tools work together for complete legal research  
✅ **Structured Output** - Consistent, professional legal documents  
✅ **Audit Trail** - All interactions logged for compliance  
✅ **Scalable Workflows** - Repeatable processes for common legal tasks  
✅ **Quality Assurance** - Built-in validation and formatting standards  

### **Legal Team Value:**

- **Time Savings**: Automated research and analysis
- **Quality Improvement**: Consistent, thorough legal work
- **Risk Reduction**: Built-in validation and compliance checks
- **Knowledge Capture**: Structured legal reasoning and precedents
- **Scalability**: Handle more cases with same resources

---

*This document demonstrates how the Legal MCP Server transforms legal workflows from manual, time-intensive processes into efficient, AI-assisted legal operations while maintaining the highest standards of legal practice and compliance.*