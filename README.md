# Legal Research & Paralegal MCP Server

A specialized Model Context Protocol (MCP) server for structured legal workflows. This server provides tools, resources, and prompts for precedent retrieval, statute analysis, citation validation, contract analysis, and guided brief scaffolding. **Status: Experimental - Iterating with partner cohort.**

## 🏗️ Architecture

The server is built with a schema-first, inspectable architecture for legal workflow augmentation:

```
legal-mcp/
├── main.py                    # Main server entry point
├── utils.py                   # Core legal data management utilities
├── tools/                     # MCP Tools (organized by category)
│   ├── research_tools.py      # Precedent retrieval and statute extraction
│   ├── citation_tools.py      # Citation validation and normalization
│   ├── contract_tools.py      # Contract analysis and clause differ
│   └── brief_tools.py         # Brief scaffolding and argument outlines
├── resources/                 # MCP Resources (organized by domain)
│   ├── case_resources.py      # Case law and precedent resources
│   ├── statute_resources.py   # Statutory materials
│   ├── contract_resources.py  # Contract templates and analysis
│   └── brief_resources.py     # Brief templates and frameworks
├── prompts/                   # MCP Prompts (user-controlled templates)
│   ├── __init__.py            # Central prompt registration
│   ├── research_prompts.py    # Legal research analysis prompts
│   ├── drafting_prompts.py    # Document drafting prompts
│   ├── analysis_prompts.py    # Contract and clause analysis prompts
│   └── argument_prompts.py    # Brief and argument construction prompts
└── data/                      # Legal data files
    ├── cases/                 # TBD - Case law database
    ├── statutes/              # TBD - Statutory materials
    ├── contracts/             # Sample contracts and clauses
    └── templates/             # Legal document templates
```

## 🚀 Features

### MCP Capabilities
- **6 Tools (Planned)**: Focused legal workflow primitives
- **15+ Resources (Seed)**: Legal reference materials and templates
- **4 Prompts (Planned)**: Structured legal analysis templates
- **SSE Transport**: Web-compatible Server-Sent Events endpoint

### Tool Categories

#### 🔍 Legal Research (Coming Soon)
- Multi-source precedent retrieval adapters (planned)
- Statute excerpt extraction and contextual analysis
- Case law search with relevance ranking
- Jurisdictional filtering and citation tracking

#### ✓ Citation Management (Planned)
- Citation normalization and validation staging
- Bluebook/jurisdiction-specific formatting
- Citation integrity verification
- Cross-reference resolution

#### 📄 Contract Analysis (In Development)
- Clause-level differ with risk identification
- Contract comparison and variance detection
- Template-based clause extraction
- Risk flag categorization and highlighting

#### 📝 Brief Scaffolding (Planned)
- Guided brief outline generation
- Argument structure templates
- Issue statement frameworks
- Authority integration patterns

#### ⚙️ System Management (Coming Soon)
- Data refresh and cache management
- Citation database updates
- System statistics and audit logs

### Resources

#### Static Resources (Seed Data)
- `legal://case-database`: Legal precedent index (TBD)
- `legal://statute-library`: Statutory materials (TBD)
- `legal://contract-templates`: Standard contract templates (Seed)
- `legal://brief-frameworks`: Brief outline templates (Seed)
- `legal://citation-standards`: Citation formatting rules (Seed)

#### Dynamic Resource Templates (Planned)
- `legal://case/{case_id}/analysis`: Case analysis with extraction
- `legal://statute/{statute_id}/context`: Statutory context and history
- `legal://contract/{contract_id}/differ`: Contract comparison results
- `legal://brief/{brief_id}/outline`: Brief structure and arguments
- `legal://citation/{citation_id}/validate`: Citation validation results

### Prompts (4 Planned)

#### Research Prompts (Planned)
- **Precedent Analysis**: Case law evaluation and applicability assessment
- **Statutory Interpretation**: Statute analysis with legislative context

#### Drafting Prompts (Planned)
- **Brief Construction**: Structured brief writing framework
- **Argument Development**: Legal argument construction and refinement

#### Analysis Prompts (Planned)
- **Contract Review**: Comprehensive contract analysis template
- **Clause Comparison**: Side-by-side clause analysis framework

#### Citation Prompts (Planned)
- **Citation Validation**: Citation integrity checking workflow
- **Authority Integration**: Strategic authority placement guidance

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/agentic-ops/legal-mcp.git
   cd legal-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```

## 🔍 MCP Inspector

To inspect and debug your MCP server, you can use the MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector
```

This will launch the MCP Inspector interface, allowing you to:
- Monitor MCP messages in real-time
- Debug tool and resource calls
- Inspect server responses
- Test server functionality
- Validate schema conformance

## 🌐 Server Transport

The server uses **Server-Sent Events (SSE)** transport, making it compatible with:
- Web browsers and HTTP clients
- Traditional MCP clients
- Custom legal workflow integrations

### Connection Details
- **SSE Endpoint**: `http://127.0.0.1:8000/sse` (for establishing SSE connection)
- **Message Endpoint**: `http://127.0.0.1:8000/messages/` (for posting MCP messages)
- **Transport**: SSE (Server-Sent Events)
- **Protocol**: MCP (Model Context Protocol)

### Web Client Example
```javascript
// Establish SSE connection
const eventSource = new EventSource('http://127.0.0.1:8000/sse');
eventSource.onmessage = function(event) {
    const mcpMessage = JSON.parse(event.data);
    // Handle MCP protocol messages
};

// Send MCP messages
async function sendMCPMessage(message) {
    const response = await fetch('http://127.0.0.1:8000/messages/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message)
    });
    return response.json();
}
```

## 🔧 Component Details

### Core Components

#### `utils.py` - Legal Data Management (In Development)
- `LegalDataManager`: Central data access class for legal materials
- `CitationParser`: Citation extraction and normalization utilities
- JSON/XML legal document loading and caching
- Cross-referencing and citation relationship mapping
- **Status**: Schema-first design, core utilities in active development

#### `main.py` - Server Entry Point
- FastMCP server initialization
- Component registration orchestration
- SSE transport configuration
- Startup logging and diagnostics
- Audit logging for legal workflow compliance

### Tool Modules

Each tool module follows a consistent pattern:
```python
def register_[category]_tools(mcp: FastMCP):
    """Register all [category] tools with the MCP server"""
    
    @mcp.tool()
    def tool_function(parameters) -> str:
        """Tool description with clear legal intent"""
        # Implementation with audit trail
        return json.dumps(result, indent=2)
```

**Status**: Tool signatures defined, implementations in active iteration.

### Resource Modules

Resources are organized by legal domain for audit-friendly access:

#### Case Resources (`case_resources.py`) - TBD
- Case law precedent retrieval
- Jurisdictional filtering
- Citation-based case lookup

#### Statute Resources (`statute_resources.py`) - TBD
- Statutory text extraction
- Legislative history context
- Amendment tracking

#### Contract Resources (`contract_resources.py`) - Seed Data Available
- Contract templates and frameworks
- Standard clause library
- Contract analysis results

#### Brief Resources (`brief_resources.py`) - Seed Data Available
- Brief outline templates
- Argument structure frameworks
- Authority integration patterns

Each module follows a consistent pattern:
```python
def register_[domain]_resources(mcp: FastMCP):
    """Register all [domain] resources with the MCP server"""
    
    @mcp.resource("legal://resource-name")
    def resource_function() -> str:
        """Resource description with provenance tracking"""
        return json.dumps(data, indent=2)
```

### Prompt Templates

Prompts guide structured legal analysis with audit-friendly deterministic scaffolds:
```python
@mcp.prompt()
def analysis_prompt(param: str = "default") -> str:
    """Legal analysis prompt with clear reasoning framework"""
    return f"""
    Structured analysis instructions for {param}...
    No hidden network calls - pure reasoning frames.
    """
```

**Status**: Prompt frameworks defined, templates under partner review.

## 📊 Data Structure

The server operates on structured legal data (selective disclosure):

- **Case Database**: TBD - Precedent index with citation graph
- **Statute Library**: TBD - Statutory materials with amendment tracking
- **Contract Templates**: Seed data - Standard agreements and clauses
- **Brief Frameworks**: Seed data - Outline templates and argument structures
- **Citation Standards**: Seed data - Bluebook and jurisdiction-specific rules

**Note**: Schema stability prioritized before data expansion.

## 🔍 Usage Examples

### MCP Client Examples (Planned Workflows)

For proper MCP client integration, use the MCP protocol with the correct endpoints:

```bash
# Establish SSE connection (listen for server messages)
curl -N http://127.0.0.1:8000/sse

# Send MCP messages (in a separate terminal)
# Search case precedents (Coming Soon)
curl -X POST http://127.0.0.1:8000/messages/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "search_precedents", "arguments": {"query": "contract breach", "jurisdiction": "CA"}}}'

# Validate citation (Planned)
curl -X POST http://127.0.0.1:8000/messages/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "validate_citation", "arguments": {"citation": "123 F.3d 456"}}}'

# Get contract templates (Seed Data Available)
curl -X POST http://127.0.0.1:8000/messages/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "legal://contract-templates"}}'

# Analyze contract clauses (In Development)
curl -X POST http://127.0.0.1:8000/messages/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "compare_contracts", "arguments": {"contract_a": "NDA_v1", "contract_b": "NDA_v2"}}}'
```

## 🧪 Testing

**Status**: Test infrastructure planned, core test patterns being established with partner cohort.

### Test Structure (Planned)

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests for core components
│   ├── test_utils.py        # LegalDataManager and CitationParser tests
│   └── test_*.py            # Additional unit tests
├── integration/             # Integration tests for MCP components
│   ├── test_research_tools.py    # Legal research tools tests
│   ├── test_citation_tools.py    # Citation validation tests
│   ├── test_contract_tools.py    # Contract analysis tests
│   ├── test_resources.py         # Resource endpoint tests
│   └── test_prompts.py           # Prompt template tests
└── __init__.py
```

### Test Categories (In Development)

#### Unit Tests (`tests/unit/`) - Coming Soon
- **Data Manager Tests**: Core legal data handling functionality
- **Citation Parser Tests**: Citation extraction and validation logic
- **Utility Functions**: Helper functions and data validation

#### Integration Tests (`tests/integration/`) - Planned
- **Research Tools**: Case search, precedent retrieval, statute extraction
- **Citation Tools**: Citation validation, normalization, cross-referencing
- **Contract Tools**: Contract analysis, clause differ, risk identification
- **Brief Tools**: Outline generation, argument scaffolding
- **Resources**: Static resources and dynamic templates
- **Prompts**: Template generation and legal reasoning frameworks

### Running Tests (When Available)

#### Prerequisites
```bash
# Install testing dependencies
pip install -r requirements.txt
```

#### Quick Test Commands (Planned)
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
```

### Test Data Validation (Planned)

The test suite will validate:
- ✅ Citation parsing and normalization accuracy
- ✅ Contract clause extraction and comparison logic
- ✅ Brief outline generation conformance
- ✅ Resource endpoints return valid, auditable JSON
- ✅ Prompt templates generate proper legal reasoning frameworks
- ✅ Error handling for missing or malformed legal data
- ✅ Audit trail integrity for all operations
- ✅ Schema conformance across all components

**Note**: Test development gated by schema stability and partner feedback.

## 🛠️ Development

### Adding New Tools
1. Choose appropriate category in `tools/`
2. Add tool function with `@mcp.tool()` decorator
3. Include audit logging and provenance tracking
4. Register in the category's `register_*_tools()` function
5. Import and call registration in `main.py`
6. **Add Tests**: Create corresponding tests when test infrastructure is ready
7. **Partner Review**: Submit for cohort validation before broader deployment

### Adding New Resources
1. Choose appropriate domain module in `resources/` (case, statute, contract, brief)
2. Add resource function with `@mcp.resource()` decorator and URI pattern
3. Include data provenance and update timestamps
4. Register in the domain's `register_*_resources()` function
5. Import and call registration in `main.py`
6. **Add Tests**: Include resource tests when infrastructure is ready
7. **Schema Validation**: Ensure conformance to established legal data schemas

### Adding New Prompts
1. Choose appropriate category in `prompts/` (research, drafting, analysis, argument)
2. Add prompt function with `@mcp.prompt()` decorator
3. Include parameter defaults and comprehensive legal reasoning instructions
4. Ensure deterministic output (no hidden network calls)
5. Register in the category's `register_*_prompts()` function
6. **Add Tests**: Include prompt tests when infrastructure is ready
7. **Partner Review**: Validate reasoning frameworks with legal experts

### Adding New Prompt Categories
1. Create new file in `prompts/` directory (e.g., `prompts/discovery_prompts.py`)
2. Follow the existing pattern with `register_discovery_prompts(mcp)` function
3. Import and register in `prompts/__init__.py`
4. **Add Tests**: Create corresponding test fixtures and test methods
5. **Schema Definition**: Document expected inputs and outputs

## 🔄 Benefits of SSE Transport

- **Web Compatible**: Direct browser integration for legal web applications
- **Real-time**: Server-sent events for live legal research updates
- **HTTP Standard**: Works with standard HTTP tools and corporate firewalls
- **Firewall Friendly**: Uses standard HTTP port (critical for law firm IT environments)
- **Scalable**: Supports multiple concurrent paralegal/attorney connections
- **Audit-Friendly**: All requests logged via standard HTTP access logs

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- ✅ Core MCP server architecture
- ✅ SSE transport implementation
- ✅ Seed data for contract templates and brief frameworks
- 🔄 Schema stabilization with partner cohort
- 🔄 Citation parser core utilities

### Phase 2: Research Capabilities (Q1 2025 - Planned)
- 📋 Multi-source precedent retrieval adapters
- 📋 Statute excerpt extraction and context
- 📋 Citation validation and normalization
- 📋 Basic case law search functionality

### Phase 3: Analysis & Drafting (Q2 2025 - Planned)
- 📋 Contract clause differ with risk identification
- 📋 Brief scaffolding and outline generation
- 📋 Argument structure templates
- 📋 Enhanced citation integrity tools

### Phase 4: Expansion (TBD)
- 📋 Jurisdictional filtering enhancements
- 📋 Legislative history tracking
- 📋 Multi-document analysis workflows
- 📋 Advanced audit and compliance features

**Note**: Roadmap subject to change based on partner feedback and schema maturity.

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

**Status**: Currently in closed partner cohort phase. Public contributions will be welcomed after schema stabilization.

For partner cohort members:
1. Review current schemas and design patterns
2. Provide feedback on tool definitions and workflows
3. Test with real-world legal workflow scenarios
4. Report edge cases and audit requirements
5. Follow established coding patterns and audit trail requirements

## 🔐 Legal & Compliance Considerations

This MCP server is designed with legal workflow compliance in mind:

- **Audit Trails**: All operations logged with timestamps and provenance
- **Data Provenance**: Clear source attribution for all legal materials
- **Schema-First Design**: Predictable, inspectable outputs for legal review
- **No Hidden Operations**: Deterministic reasoning frames, no undisclosed network calls
- **Selective Disclosure**: Sensitive implementations kept confidential during development

**Important**: This server provides legal workflow augmentation tools. It does not provide legal advice and does not replace attorney review and judgment.

---

## 📖 Further Reading

For more information about MCP architecture and legal AI applications:

**[🔌 MCP Servers - Model Context Protocol Implementation](https://edwin.genego.io/ai/mcp-servers)**

Topics covered:
- Understanding MCP Servers and their business impact
- Architecture patterns for professional services
- Legal workflow automation considerations
- Security and audit requirements
- Compliance-friendly AI integration

---

*Built with the Model Context Protocol (MCP) for verifiable legal workflow augmentation*

**Status**: Experimental - Iterating with partner cohort - Schema-first, selective disclosure