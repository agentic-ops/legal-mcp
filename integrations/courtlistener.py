"""CourtListener / RECAP adapter (Free Law Project).

CourtListener exposes a free, rate-limited REST API (v4) that also serves
the RECAP Archive of PACER documents. It is the preferred live source
because it avoids PACER fees.

API reference: https://www.courtlistener.com/help/api/rest/
Auth: an ``Authorization: Token <token>`` header on every request.
Search endpoint: ``GET {base}/search/?q=...&type=o``

This adapter is disabled by default. When disabled or unconfigured it
returns a structured status payload instead of making any network call.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from integrations.config import CourtListenerSettings, get_integration_settings
from utils import audit

# CourtListener search `type` parameter values (subset).
SEARCH_TYPES = {
    "o": "Case law opinions",
    "r": "RECAP dockets (PACER)",
    "rd": "RECAP documents (PACER)",
    "oa": "Oral arguments",
    "p": "Judges / people",
}


class CourtListenerClient:
    """Thin, testable wrapper over the CourtListener REST API."""

    def __init__(
        self,
        settings: Optional[CourtListenerSettings] = None,
        http_client: Any = None,
    ) -> None:
        self.settings = settings or get_integration_settings().courtlistener
        # Optional injected httpx-like client (used for testing / reuse).
        self._http_client = http_client

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    def status(self) -> Dict[str, Any]:
        """Return a non-sensitive status report (never leaks the token)."""

        return {
            "source": "courtlistener",
            "enabled": self.settings.enabled,
            "configured": self.settings.configured,
            "base_url": self.settings.base_url,
            "missing_settings": self.settings.missing_settings(),
            "cost": "free (rate-limited); preferred over PACER",
        }

    def _get_client(self):
        if self._http_client is not None:
            return self._http_client
        import httpx

        return httpx.Client(timeout=30.0)

    def search(
        self, query: str, result_type: str = "o", limit: int = 5
    ) -> Dict[str, Any]:
        """Search CourtListener; returns a structured, JSON-friendly dict."""

        audit(
            "courtlistener_search",
            query=query,
            result_type=result_type,
            enabled=self.settings.enabled,
        )
        if not self.settings.enabled:
            return {
                **self.status(),
                "query": query,
                "message": (
                    "CourtListener integration is disabled. Set "
                    "COURTLISTENER_ENABLED=true to enable it."
                ),
                "results": [],
            }
        if not self.settings.configured:
            return {
                **self.status(),
                "query": query,
                "message": (
                    "CourtListener is enabled but no API token is set. "
                    "Set COURTLISTENER_API_TOKEN."
                ),
                "results": [],
            }

        headers = {"Authorization": f"Token {self.settings.api_token}"}
        params = {"q": query, "type": result_type}
        try:
            client = self._get_client()
            response = client.get(
                f"{self.settings.base_url}/search/",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # pragma: no cover - network failure path
            return {
                **self.status(),
                "query": query,
                "error": f"CourtListener request failed: {exc}",
                "results": [],
            }

        results = payload.get("results", [])[:limit]
        return {
            "source": "courtlistener",
            "enabled": True,
            "query": query,
            "result_type": result_type,
            "result_count": payload.get("count"),
            "results": results,
        }
