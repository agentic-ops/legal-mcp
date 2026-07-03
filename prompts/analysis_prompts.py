# Legal Research & Paralegal MCP Server
# Contract and clause analysis prompts

# TODO: Implement contract review prompt
# TODO: Add clause comparison prompt


def register_analysis_prompts(mcp):
    """Register all analysis prompts with the MCP server"""

    @mcp.prompt()
    def contract_review(contract_type: str = "default") -> str:
        """Comprehensive contract analysis template"""
        return f"""
        Structured contract review for {contract_type}...
        No hidden network calls - pure reasoning frames.
        """

    @mcp.prompt()
    def clause_comparison(clause_type: str = "default") -> str:
        """Side-by-side clause analysis framework"""
        return f"""
        Structured clause comparison for {clause_type}...
        No hidden network calls - pure reasoning frames.
        """
