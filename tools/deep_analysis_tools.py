"""Deep clause analysis via MCP LLM sampling with heuristic fallback."""

from __future__ import annotations

import json
from typing import Any, Optional

from mcp import types
from mcp.server.fastmcp import Context

from tools.risk_helpers import assess_clause_risk
from utils import audit

_SAMPLING_CAPABILITY = types.ClientCapabilities(sampling=types.SamplingCapability())
DISCLAIMER = "AI-generated reasoning for attorney review only. Not legal advice."
_SAMPLING_UNAVAILABLE_NOTE = (
    "Connected MCP client does not support LLM sampling; returning "
    "keyword-based heuristic analysis only."
)


def _heuristic_only_payload(
    clause_text: str,
    clause_type: str,
    heuristic: dict,
    *,
    note: str = _SAMPLING_UNAVAILABLE_NOTE,
    error: Optional[str] = None,
) -> str:
    payload = {
        "clause_type": clause_type,
        "input_clause": clause_text,
        "heuristic_analysis": heuristic,
        "llm_reasoning": None,
        "note": note,
        "disclaimer": DISCLAIMER,
        "notice": "not legal advice",
    }
    if error:
        payload["error"] = error
    return json.dumps(payload, indent=2)


def register_deep_analysis_tools(mcp) -> None:
    """Register deep clause analysis tools with the MCP server."""

    @mcp.tool()
    async def deep_analyze_clause(
        clause_text: str,
        clause_type: str = "general",
        ctx: Optional[Context] = None,
    ) -> str:
        """Run keyword heuristics, then ask the connected client's LLM for deeper
        reasoning via MCP sampling. Falls back to heuristic-only output when the
        client does not support sampling. Not legal advice."""
        audit("deep_analyze_clause", clause_type=clause_type)
        heuristic = assess_clause_risk(clause_text)

        supports_sampling = False
        session: Any = None
        if ctx is not None:
            try:
                session = ctx.session
                supports_sampling = session.check_client_capability(
                    _SAMPLING_CAPABILITY
                )
            except ValueError:
                supports_sampling = False
        if session is None or not supports_sampling:
            return _heuristic_only_payload(clause_text, clause_type, heuristic)

        try:
            result = await session.create_message(
                messages=[
                    types.SamplingMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=(
                                f"Analyze this {clause_type} clause for risk beyond "
                                f"keyword matching; note anything the following scan "
                                f"may have missed in 2-4 sentences.\n\n"
                                f"Clause:\n{clause_text}\n\n"
                                f"Keyword scan found: {json.dumps(heuristic)}"
                            ),
                        ),
                    )
                ],
                max_tokens=500,
                system_prompt=(
                    "You are a careful contract-review assistant. Be specific and "
                    "concise. Not legal advice."
                ),
            )
            if result.content.type == "text":
                llm_text = result.content.text
            else:
                llm_text = str(result.content)
        except Exception as exc:
            return _heuristic_only_payload(
                clause_text,
                clause_type,
                heuristic,
                note=_SAMPLING_UNAVAILABLE_NOTE,
                error=f"Sampling request failed: {exc}",
            )

        return json.dumps(
            {
                "clause_type": clause_type,
                "input_clause": clause_text,
                "heuristic_analysis": heuristic,
                "llm_reasoning": llm_text,
                "disclaimer": DISCLAIMER,
                "notice": "not legal advice",
            },
            indent=2,
        )
