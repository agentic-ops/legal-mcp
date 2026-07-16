"""Runtime controls and response contracts for bundled demo content."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

DEMO_MODE_ENV = "LEGAL_MCP_DEMO_MODE"
DEMO_WARNING = "DEMO DATA ONLY - NOT VERIFIED LEGAL AUTHORITY OR USER-SUPPLIED CONTENT."


def is_demo_mode() -> bool:
    """Return whether bundled sample legal content is explicitly enabled."""

    raw = os.environ.get(DEMO_MODE_ENV)
    if raw is None:
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def demo_payload(**fields: Any) -> Dict[str, Any]:
    """Build a demo-derived payload with provenance fields first."""

    return {"warning": DEMO_WARNING, "data_mode": "demo", **fields}


def demo_data_disabled_payload(
    capability: str,
    next_steps: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the stable response returned by demo-backed production calls."""

    return {
        "data_mode": "production",
        "available": False,
        "error": "demo_data_disabled",
        "message": (
            f"{capability} uses bundled sample content, which is disabled in "
            "production mode. No local legal database is configured."
        ),
        "next_steps": next_steps
        or [
            "Use real document tools for user-supplied files.",
            "Enable and configure CourtListener for live case-law research.",
            f"Set {DEMO_MODE_ENV}=true only for demonstrations or testing.",
        ],
    }
