"""Optional live legal-data integrations.

This package holds adapters for external legal databases that are
*disabled by default* and enabled per-integration via feature flags and
API credentials (see :mod:`integrations.config`).

* :mod:`integrations.courtlistener` -- CourtListener / RECAP (Free Law
  Project). Free, preferred source.
* :mod:`integrations.pacer` -- PACER (federal court records). Paid;
  usage may incur per-page/per-search fees. Off by default.
"""

from __future__ import annotations

from integrations.config import (
    CourtListenerSettings,
    IntegrationSettings,
    PacerSettings,
    get_integration_settings,
)
from integrations.courtlistener import CourtListenerClient
from integrations.pacer import PacerClient

__all__ = [
    "CourtListenerSettings",
    "IntegrationSettings",
    "PacerSettings",
    "get_integration_settings",
    "CourtListenerClient",
    "PacerClient",
]
