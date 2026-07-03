# Legal Research & Paralegal MCP Server
# Document drafting prompts

# TODO: Implement brief construction prompt
# TODO: Add argument development prompt


def register_drafting_prompts(mcp):
    """Register all drafting prompts with the MCP server"""

    @mcp.prompt()
    def brief_construction(case_type: str = "default") -> str:
        """Structured brief writing framework"""
        return f"""
        Structured brief construction for {case_type}...
        No hidden network calls - pure reasoning frames.
        """

    @mcp.prompt()
    def argument_development(legal_issue: str = "default") -> str:
        """Legal argument construction and refinement"""
        return f"""
        Structured argument development for {legal_issue}...
        No hidden network calls - pure reasoning frames.
        """
