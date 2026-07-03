"""Contract templates and analysis resources."""

from __future__ import annotations

import json

from utils import audit, get_data_manager


def register_contract_resources(mcp) -> None:
    """Register all contract resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://contract-templates")
    def contract_templates() -> str:
        """Standard contract templates index."""
        audit("resource_contract_templates")
        return json.dumps(
            {
                "count": len(data.contracts),
                "templates": data.list_contracts(),
            },
            indent=2,
        )

    @mcp.resource("legal://contract/{contract_id}/differ")
    def contract_differ(contract_id: str) -> str:
        """Clause-level representation of a contract, ready for diffing."""
        audit("resource_contract_differ", contract_id=contract_id)
        contract = data.get_contract(contract_id)
        if contract is None:
            return json.dumps(
                {"contract_id": contract_id, "error": "Contract not found."},
                indent=2,
            )
        clauses = contract.get("clauses", {})
        return json.dumps(
            {
                "id": contract["id"],
                "title": contract.get("title"),
                "type": contract.get("type"),
                "clauses": [
                    {"clause": name, "text": text} for name, text in clauses.items()
                ],
            },
            indent=2,
        )
