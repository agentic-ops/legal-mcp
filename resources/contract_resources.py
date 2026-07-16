"""Contract templates and analysis resources."""

from __future__ import annotations

import json

from demo_mode import demo_data_disabled_payload, demo_payload
from utils import audit, get_data_manager


def register_contract_resources(mcp) -> None:
    """Register all contract resources with the MCP server."""

    data = get_data_manager()

    @mcp.resource("legal://contract-templates")
    def contract_templates() -> str:
        """Standard contract templates index."""
        audit("resource_contract_templates")
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload(
                    "Bundled contract-template resource",
                    [
                        "Use document tools with a user-supplied contract.",
                        "Set LEGAL_MCP_DEMO_MODE=true only for demonstrations or testing.",
                    ],
                ),
                indent=2,
            )
        return json.dumps(
            demo_payload(
                count=len(data.contracts),
                templates=[
                    {"source": "demo_seed", "authoritative": False, **template}
                    for template in data.list_contracts()
                ],
            ),
            indent=2,
        )

    @mcp.resource("legal://contract/{contract_id}/differ")
    def contract_differ(contract_id: str) -> str:
        """Clause-level representation of a contract, ready for diffing."""
        audit("resource_contract_differ", contract_id=contract_id)
        if not data.demo_mode:
            return json.dumps(
                demo_data_disabled_payload(
                    "Bundled contract-template differ resource",
                    [
                        "Use compare_documents with user-supplied contracts.",
                        "Set LEGAL_MCP_DEMO_MODE=true only for demonstrations or testing.",
                    ],
                ),
                indent=2,
            )
        contract = data.get_contract(contract_id)
        if contract is None:
            return json.dumps(
                demo_payload(contract_id=contract_id, error="Contract not found."),
                indent=2,
            )
        clauses = contract.get("clauses", {})
        return json.dumps(
            demo_payload(
                source="demo_seed",
                authoritative=False,
                id=contract["id"],
                title=contract.get("title"),
                type=contract.get("type"),
                clauses=[
                    {"clause": name, "text": text} for name, text in clauses.items()
                ],
            ),
            indent=2,
        )
